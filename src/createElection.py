import os
import json
import collections
import shutil
from shutil import ignore_patterns
import errno
import datetime
import time
import sys
import subprocess
from subprocess import check_output
import random
import string
import re
import jwrite
import electionUtils

'''
The script can be called with 1 to 3 arguments

[1] argument should be a either "mockElection" or "customElection",
    depending on whether it should be a simple test election without many arguments or not.
    To avoid misspelling, a mock election will be created as long as the argument contains the string "mock".

[2] argument (not needed for mock elections) should be a stringified JSON object containing the following elements
    (which are all included in a proper ElectionManifest.json):
        "title": string
        "description": string
        "startTime": string of format: "yy-mm-dd hh:mm UTC+0000", example: "2014-01-01 15:00 UTC+0000"
        "endTime": string of format: "yy-mm-dd hh:mm UTC+0000", example: "2018-11-10 16:00 UTC+0000"
        "voters": array/list of strings  
        "publishListOfVoters": true or false (boolean)
        "minChoicesPerVoter": positive integer
        "maxChoicesPerVoter": positive integer no higher than the amount of choices
        "question": string
        "furtherInfo" : string
        "choices": array/list of strings

[3] argument (optional) should be a stringified JSON object, with optional keys:
        "password": string encrypted with 'bcrypt'
        "userChosenRandomness": true or false (boolean)
        "hidden": true or false (boolean)
        "subdomain": a subdomain all the servers will be on, this will replace the ELS,
                therefore two election with the same subdomain should not be created (no check yet).
        "confidentialVotersFile": path to json file containing a list of emails (voters) in the key "voters"
        "keys": array/list containing 1+<numberOfMixServers> (usually three mix servers) JSON objects
                containing 4 corresponding keypairs: {encryption_key, verification_key, signing_key, decryption_key}
'''



'''
single function to copy a directory or file using shutil,
while some folders can be omitted (specified in the ignore parameter)
'''
def copy(src, dest):
    try:
        shutil.copytree(src, dest, symlinks=False, ignore=ignore_patterns("*.py", "00", "01", "02", "tests"))
    except OSError as e:
        # source is a file, not a directory
        if e.errno == errno.ENOTDIR:
            shutil.copy(src, dest)
        else:
            print("Directory not copied. Error: %s" % e)

def getTime():
    utcTime = datetime.datetime.utcnow()
    return utcTime

'''
modifies a date by seconds, currently used to set starting time 24h prior
to creation date for mock elections
'''
def addSec(tm, secs):
    fulldate = tm + datetime.timedelta(seconds=secs)
    return fulldate

'''
defines the location of every file that will 
be written to or read from, except the files for
the mix server and key generation, since the 
number of mix servers can only be determined at 
a later time; will be defined at getMixServerConfig()
'''
def setConfigFiles():
    global rootDirProject
    
    global sElectDir
    global electionConfig
    global electionInfo
    global electionInfoHidden
    global defaultManifest
    global electionURI
    global nginxConf
    global passList
    global nginxLog
    
    global manifest
    global collectingConf
    global bulletinConf
    global votingManifest
    global votingConf
    global authManifest
    global authConf
    global mixConf

    # the root dir is two folders back
    rootDirProject = os.path.realpath(__file__)
    for i in range(2):
        rootDirProject=os.path.split(rootDirProject)[0]
    
    # absolute paths
    sElectDir = rootDirProject + "/sElect"
    electionConfig = rootDirProject + "/_configFiles_/handlerConfigFile.json"
    electionInfo = rootDirProject + "/_configFiles_/electionInfo.json"
    defaultManifest = rootDirProject + "/_configFiles_/ElectionManifest.json"
    electionURI = rootDirProject + "/_configFiles_/electionsURI.json"
    electionInfoHidden = rootDirProject + "/_configFiles_/electionHiddenInfo.json"
    nginxConf =  rootDirProject + "/nginx_config/nginx_select.conf"
    passList =  rootDirProject + "/ElectionHandler/_data_/pwd.json"
    nginxLog = rootDirProject + "/nginx_config/log"
    
    # sElect (partial) mixFiles path
    manifest = "/_sElectConfigFiles_/ElectionManifest.json"
    collectingConf = "/CollectingServer/config.json"
    bulletinConf = "/BulletinBoard/config.json"
    votingManifest = "/VotingBooth/ElectionManifest.json"     
    votingConf = "/VotingBooth/config.json" 
    authManifest = "/Authenticator/ElectionManifest.json"     
    authConf = "/Authenticator/config.json" 
    mixConf = []

'''
reads the configuration data for the ElectionManager,
the ElectionManifest will be read for default configurations;
parameters will be overwritten if they are specified in the
input parameters (mock elections will mostly use the default settings)
'''
def getConfigData():
    global deployment
    global serverAddr
    global votingTime
    global mockVoters
    global numMix
    global createdElections
    global nginxPort
    global minChoices
    global maxChoices
    
    global elecTitle
    global elecDescr
    global elecQuestion
    global furtherInfo
    global eleChoices
    global publish
    
    #get duration and deployment status from handlerConfigFile
    deployment = False
    serverAddr = False
    try:
        jsonFile = open(electionConfig, 'r')
        jsonData = json.load(jsonFile, object_pairs_hook=collections.OrderedDict)
        votingTime = jsonData["electionDurationInHours"]*60*60    #hours to seconds
        mockVoters = jsonData["numberOfMockVoters"]
        numMix = jsonData["numberOfMixServers"]
        createdElections = jsonData["electionsCreated"]
        nginxPort = jsonData["nginx-port"]
        if jsonData["deployment"] is True:
            serverAddr = rootDirProject + "/_configFiles_/serverAddresses.json"
            deployment = True
        jsonFile.close()
    except IOError:
        sys.exit("handlerConfigFile.json missing or corrupt")
    
    #read default data from sElect/templates/ElectionManifest.json
    try:
        jsonFile = open(defaultManifest, 'r')
        jsonData = json.load(jsonFile, object_pairs_hook=collections.OrderedDict)
        elecTitle = jsonData["title"]
        elecDescr = jsonData["description"]
        elecQuestion = jsonData["question"]
        eleChoices = jsonData["choices"]
        publish = jsonData["publishListOfVoters"]
        minChoices = jsonData["minChoicesPerVoter"]
        maxChoices = jsonData["maxChoicesPerVoter"]
        furtherInfo = jsonData["furtherInfo"]
        jsonFile.close()
    except IOError:
        sys.exit("ElectionManifest missing or corrupt")


'''
handles the input received, in case it is not a
mock election that is created, most parameters defined
in getConfigData() will be overwritten
'''
def getInput():
    global password
    global mockElection
    global startingTime
    global endingTime
    global minChoices
    global maxChoices
    
    global elecTitle
    global elecDescr
    global elecQuestion
    global furtherInfo
    global voters
    global eleChoices
    global publish
    global randomness
    global keys
    global hidden
    global ELS
    global getELS
    global confidentialVotersFile
    
    #get input parameters (if any)
    startingTime = addSec(getTime(), -24*60*60).strftime("%Y-%m-%d %H:%M UTC+0000")
    endingTime = addSec(getTime(), votingTime).strftime("%Y-%m-%d %H:%M UTC+0000")
    voters = []
    confidentialVotersFile = ""
    #check if a mock election should be created
    mockElection = True if len(sys.argv) < 2 or "mock" in sys.argv[1] else False
    if not mockElection:
        electionArgs = json.loads(sys.argv[2])
        startingTime = electionArgs['startTime']
        endingTime = electionArgs['endTime']
        elecTitle = electionArgs['title']
        elecDescr = electionArgs['description']
        elecQuestion = electionArgs['question']
        try:
            eleChoices = electionArgs['choices[]']
        except:                                     #needed due to differences in how javascript handles json objects
            eleChoices = electionArgs['choices']
        publish = electionArgs['publishListOfVoters']
        publish = True if publish == "true" or publish == True else False
        minChoices = 1
        maxChoices = 1
        if "minChoicesPerVoter" in electionArgs:
            minChoices = electionArgs['minChoicesPerVoter']
        if "maxChoicesPerVoter" in electionArgs:
            maxChoices = electionArgs['maxChoicesPerVoter']
        if "voters" in electionArgs:
            voters = electionArgs['voters']
        elif "voters[]" in electionArgs:            #needed due to differences in how javascript handles json objects
            voters = electionArgs['voters[]']
        if "furtherInfo" in electionArgs:
        	furtherInfo = electionArgs['furtherInfo']
 
    #get additional parameters
    password = ""
    randomness = False
    keys = []
    hidden = False
    getELS = True
    if len(sys.argv) > 3:
        additionalArgs = json.loads(sys.argv[3])
        if "password" in additionalArgs:
            password = additionalArgs['password']
        if "userChosenRandomness" in additionalArgs:
            randomness = additionalArgs['userChosenRandomness']
            randomness = True if randomness == "true" or randomness == True else False
        if "keys" in additionalArgs:
            keys = additionalArgs["keys"]
        if "hidden" in additionalArgs:
            hidden = additionalArgs["hidden"]
            hidden = True if hidden == "true" or hidden == True else False
        if "subdomain" in additionalArgs:
            if len(additionalArgs["subdomain"]) > 0:
                ELS = "."+additionalArgs["subdomain"]
                getELS = False
                #if a subdomain is used, the ELS is not needed (since the subdomain should be unique)
        if "confidentialVotersFile" in additionalArgs:
            confidentialVotersFile = additionalArgs["confidentialVotersFile"]


'''
with the number of mix servers now knows, specify
the file locations
'''
def getMixServerConfig():
    global mixConf
    
    #mix server config mixFiles
    for x in range(numMix):
        if x < 10:
            mixConf.append("/templates/config_mix0" + str(x) + ".json")
        else:
            mixConf.append("/templates/config_mix" + str(x) + ".json")

'''
reads from serverAddresses.json to create the URI
for the node servers; if a subdomain was not specified,
it will use a "00" to "99" as the ELS
'''
def getServerLocations():
    global ports
    global ELS
    global serverAddress
    global tStamp
    global sName
    
    #get server URI's
    ports = electionUtils.usePorts(electionConfig, 3+numMix)
    if getELS:
        ELS = electionUtils.getELS(electionConfig)          #number between 00 and 100/maxElections, corresponds with subdomains
    serverAddress = electionUtils.getsAddress(electionConfig, deployment, numMix, nginxPort, ELS, serverAddr)
    #time stamp for folder path
    tStamp = startingTime.replace("-", "").replace(":", "").split()
    sName = tStamp[0] + tStamp[1]

'''
uses the key generation scripts in sElect/tools
to create new keys for each election
'''
def updateKeys():
    global mixServerEncKey
    global keys
    
    #update encryption keys
    pattern = "[0-9]+"
    keyGeneratorMix_file = "genKeys4mixServer.js"
    keyGeneratorCS_file = "genKeys4collectingServer.js"
    tools_path = sElectDir + "/tools"
    keyFile = rootDirProject + "/ElectionHandler/_data_/keys.json"
    
    if  len(keys) < numMix+1:
        keys = check_output(["node", os.path.join(tools_path,"keyGen.js"), str(numMix+1)]).splitlines()
        for x in range(len(keys)):
            keys[x] = json.loads(keys[x])
    else:
        pass
        
    #write new keys to manifest and config files
    jwrite.jwriteAdv(sElectDir + manifest, "collectingServer", keys[numMix]["encryptionKey"], "encryption_key")
    jwrite.jwriteAdv(sElectDir + manifest, "collectingServer", keys[numMix]["verificationKey"], "verification_key")
    jwrite.jwrite(sElectDir + collectingConf, "signing_key", keys[numMix]["signingKey"])
    jwrite.jwrite(sElectDir + collectingConf, "decryption_key", keys[numMix]["decryptionKey"])
    for x in range(numMix):
        jwrite.jwriteAdv(sElectDir + manifest, "mixServers", keys[x]["encryptionKey"], x, "encryption_key")
        jwrite.jwriteAdv(sElectDir + manifest, "mixServers", keys[x]["verificationKey"], x, "verification_key")
        jwrite.jwrite(sElectDir + mixConf[x], "encryption_key", keys[x]["encryptionKey"])
        jwrite.jwrite(sElectDir + mixConf[x], "verification_key", keys[x]["verificationKey"])
        jwrite.jwrite(sElectDir + mixConf[x], "signing_key", keys[x]["signingKey"])
        jwrite.jwrite(sElectDir + mixConf[x], "decryption_key", keys[x]["decryptionKey"])
            
    #get new keys
    mixServerEncKey = []
    for x in range(numMix):
        mixServerEncKey.append(keys[x]["encryptionKey"])


def writeManifest():
    #modify ElectionManifest, if no arguments are given, this is a mock election
    jwrite.jwrite(sElectDir + manifest, "startTime", startingTime)
    jwrite.jwrite(sElectDir + manifest, "endTime", endingTime)
    jwrite.jwrite(sElectDir + manifest, "title", elecTitle)
    jwrite.jwrite(sElectDir + manifest, "description", elecDescr)
    jwrite.jwrite(sElectDir + manifest, "voters", voters)
    jwrite.jwrite(sElectDir + manifest, "question", elecQuestion)
    jwrite.jwrite(sElectDir + manifest, "choices", eleChoices)
    jwrite.jwrite(sElectDir + manifest, "furtherInfo", furtherInfo)
    jwrite.jwriteAdv(sElectDir + manifest, "minChoicesPerVoter", minChoices)
    jwrite.jwriteAdv(sElectDir + manifest, "maxChoicesPerVoter", maxChoices)
    jwrite.jwrite(sElectDir + manifest, "publishListOfVoters", publish)
    jwrite.jwriteAdv(sElectDir + manifest, "collectingServer", serverAddress["collectingserver"], "URI")
    jwrite.jwriteAdv(sElectDir + manifest, "bulletinBoards", serverAddress["bulletinboard"], 0, "URI")
    for x in range(numMix):
        jwrite.jwriteAdv(sElectDir + manifest, "mixServers", serverAddress["mix"+str(x)], x, "URI")

'''
create the electionID using the hash of the ElectionManifest and
copy the sElect directory to "elections/<timestamp>_<electionID>_sElect"
'''
def sElectCopy(iDlength):
    global dstroot
    global electionID
    
    dstFolder = "elections/"
    if hidden:
        dstFolder = "elections_hidden/"
        
    #get ID after modifying Manifest
    while(iDlength < 40):
        electionID = electionUtils.getID(sElectDir + manifest, iDlength)
        dstroot = os.path.join(rootDirProject, dstFolder + tStamp[0]+tStamp[1] + "_" + electionID + "_" + os.path.split(sElectDir)[1])
        try:
            copy(sElectDir, dstroot)
            electionUtils.link(dstroot, manifest, votingManifest, authManifest)
            break
        except:
            iDlength = iDlength+1
    if confidentialVotersFile is not "":
        copy(confidentialVotersFile, dstroot+"/CollectingServer/confidentialVoters.json")

def writesElectConfigs():
    #modify Server ports
    jwrite.jwrite(dstroot + collectingConf, "port", ports[0])
    jwrite.jwrite(dstroot + bulletinConf, "port", ports[1])
    jwrite.jwrite(dstroot + votingConf, "authenticator", serverAddress["authenticator"])
    jwrite.jwrite(dstroot + votingConf, "authChannel", serverAddress["authchannel"])
    jwrite.jwrite(dstroot + votingConf, "userChosenRandomness", randomness)
    jwrite.jwrite(dstroot + authConf, "authChannel", serverAddress["authchannel"])
    jwrite.jwrite(dstroot + authConf, "votingBooth", serverAddress["votingbooth"])
    jwrite.jwrite(dstroot + collectingConf, "serverAdminPassword", password)
    for x in range(numMix):     
        jwrite.jwrite(dstroot + mixConf[x], "port", ports[x+2])
        
    #change user randomness if not a mock election
    if mockElection:
        jwrite.jwrite(dstroot + votingConf, "showOtp", True)
        jwrite.jwrite(dstroot + authConf, "showOtp", True)
        jwrite.jwrite(dstroot + collectingConf, "sendOtpBack", True)
        jwrite.jwrite(dstroot + collectingConf, "sendEmail", False)

def updateTrustedOrigins():
    #split the URI to receive the domain
    authdomain = serverAddress["authenticator"]
    temp = authdomain.split("://")
    temp[1] = temp[1].split("/")[0]
    authdomain = "://".join(temp)
    
    vbdomain = serverAddress["votingbooth"]
    temp = vbdomain.split("://")
    temp[1] = temp[1].split("/")[0]
    vbdomain = "://".join(temp)
    
    #specify the voting booth and authenticator domains as trusted domains
    varname = "trustedOrigins"
    csTrusts = 'var '+varname+' = ["'+vbdomain+'","'+authdomain+'"];'
    csFile = "/CollectingServer/webapp/trustedOrigins.js"
    
    file = open(dstroot+csFile, 'w')
    file.write(csTrusts)
    file.close()

'''
creates a number of ballots determined by <mockVoters>,
each ballot uses a (pseudo)random number of random choices 
(within the boundary of how many choices are allowed) and
saves them in the collecting servers accepted ballots file;
only used for mock elections
'''
def createBallots():
    if mockElection:
        #create Ballots
        os.mkdir(dstroot+"/CollectingServer/_data_")
        mixServerEncKeyString = str(mixServerEncKey).replace(" ", "").replace("u'", "").replace("'", "")
        ballotFile = dstroot+"/CollectingServer/_data_/accepted_ballots.log"
        for x in range(mockVoters):
            max = maxChoices if maxChoices < len(eleChoices) else len(eleChoices)
            nChoices = random.randint(minChoices,max)
            userRandom = []
            userChoices = []
            
            #add some randomness to the choices made
            for i in range(nChoices):
                temp = random.randint(0,(len(eleChoices)-1))
                while temp in userChoices:
                    temp = random.randint(0,(len(eleChoices)-1))
                userChoices.append(temp)
            
            userRandom = "".join([random.choice(string.ascii_letters + string.digits) for n in xrange(8)]) if randomness else ""
            userEmail = "user"+str(x)+"@uni-trier.de"
            userChoices = str(userChoices).replace(" ", "").replace("u'", "").replace("'", "")
            
            ballots = subprocess.Popen(["node", "createBallots.js", ballotFile, userEmail, userRandom, userChoices, electionUtils.hashManifest(sElectDir+manifest), mixServerEncKeyString], cwd=(rootDirProject+"/src"))
        ballots.wait()

'''
starts the node servers for sElect, redirects their STDOUT
to log files while keeping the STDERR linked to the parent,
so that the parent node application (which calls this file)
can handle the errors that arise.
'''
def sElectStart():
    global newPIDs
    
    if not os.path.exists(dstroot+"/LOG"):
        os.makedirs(dstroot+"/LOG")
    logfolder = dstroot+"/LOG"
    
    #start all node servers
    subprocess.Popen(["node", "compileEJS.js"], cwd=(dstroot+"/VotingBooth/webapp/ejs"))
    subprocess.call([dstroot + "/VotingBooth/refresh.sh"], cwd=(dstroot+"/VotingBooth"))
    subprocess.call([dstroot + "/Authenticator/refresh.sh"], cwd=(dstroot+"/Authenticator"))
    with open(logfolder+"/CollectingServer.log", 'w') as file_out:
        #since ballots are pre-created for mock elections, the resume option will have to be used
        if mockElection:
            col = subprocess.Popen(["node", "collectingServer.js", "--resume"], stdout=file_out, cwd=(dstroot+"/CollectingServer"))
        else:
            col = subprocess.Popen(["node", "collectingServer.js"], stdout=file_out, cwd=(dstroot+"/CollectingServer"))
    
    mix = []
    for x in range(numMix):
        with open(logfolder+"/MixServer"+str(x)+".log", 'w') as file_out:
            if x < 10:
                mix.append(subprocess.Popen(["node", "mixServer.js"], stdout=file_out, cwd=(dstroot+"/mix/0"+str(x))))
            else:
                mix.append(subprocess.Popen(["node", "mixServer.js"], stdout=file_out, cwd=(dstroot+"/mix/"+str(x))))
    with open(logfolder+"/BulletinBoard.log", 'w') as file_out:
        bb = subprocess.Popen(["node", "bb.js"], cwd=(dstroot+"/BulletinBoard"))
        newPIDs = {"cs": col.pid, "bb": bb.pid}
        for x in range(numMix):
            newPIDs["m"+str(x)] = mix[x].pid   

'''
writes information about the created election in the
handlerConfigFile.json (unless hidden), creates a file
with the minimum amount of information needed for the
ElectionHandler and sends the returns the information
'''
def writeToHandlerConfig():
    global eleInfo
    #add the password
    jwrite.jwrite(passList, electionID, password)
    
    #add ports to config
    for x in range(len(ports)):
        jwrite.jAddList(electionConfig, "usedPorts", ports[x])
    electionUrlsFile = [electionUtils.hashManifest(sElectDir+manifest), serverAddress["votingbooth"], serverAddress["collectingserver"]+"admin/panel/", serverAddress["bulletinboard"], "hidden" if hidden else "visible"]
    jwrite.jwrite(electionURI, electionID, electionUrlsFile)
    
    
    if not hidden:
        #write all election details
        newElection = { "used-ports": ports, "processIDs": newPIDs, "electionID": electionID, "electionTitle": elecTitle, "electionDescription": elecDescr, "startTime": startingTime, "endTime": endingTime, "mixServers": numMix, "ELS": ELS, "timeStamp": sName, "protect": not mockElection}
        jwrite.jAddList(electionConfig, "elections", newElection)
        jwrite.jwrite(electionConfig, "electionsCreated", createdElections+1)
        subprocess.call([sElectDir + "/../ElectionHandler/refreshConfig.sh"], cwd=(sElectDir+"/../ElectionHandler"))
    
        #write minimal election details
        eleInfo = {"electionID": electionID, "electionTitle": elecTitle, "startTime": startingTime, "endTime": endingTime, "ELS": ELS, "protect": not mockElection}
        eleInfo = jwrite.jAddListAndReturn(electionInfo, "elections", eleInfo)
    else:
        #write details in different file to not show in the Election Manager
        eleInfo = {"electionID": electionID, "electionTitle": elecTitle, "startTime": startingTime, "endTime": endingTime, "ELS": ELS, "processIDs": newPIDs, "used-ports": ports}
        jwrite.jAddList(electionInfoHidden, "elections", eleInfo)


'''
template to redirect a domain to a specified URI,
used to redirect http to https
'''
def redirectHttp(nginxData, electionID, listenPort, domainIN, urlOUT, code):
    counter = 0
    for line in nginxData:
        if "end main server" in line:
            break
        counter = counter + 1
    bracketIt = nginxData[counter:]
    del nginxData[counter:]
    
    comments = ["  # Redirect http " + str(electionID) + " \n", "  server {\n", 
                "    listen "+str(listenPort)+";", "\n",
                "    server_name "+ " ".join(domainIN) + ";\n", "\n"]
    comments.extend(["    return " +str(code)+ " " + urlOUT, ";\n", "  }\n", "\n"])
    comments.extend(bracketIt)
    nginxData.extend(comments)
    
    return nginxData


'''
configures nginx to work with the newly created election,
differentiates between a local setting (election running on
local machine and no internet connection required, cannot
connect from the outside) by checking if the server URI's
include "https://localhost".
Further differentiates between a subdomain being used or not
(in which case multiple redirections are used to make user
links more flexible.
In a non a local setting, this method requires the 
nginx file to have the lines at the end of the http block:

-    #end main server
-    #end collecting server
-    #end bulletin board
-    #end mix server <number>
-    #end voting booth
-    #end authenticator

since those will be used to keep structure 
(see templates/nginx_select.conf)
'''
def writeToNginxConfig():
    
    #modify nginx File
    if "http://localhost" not in serverAddress["collectingserver"]:
        onSSL = True
        ssl_adds = ["    ssl_protocols       TLSv1 TLSv1.1 TLSv1.2;\n",
                            "    ssl_ciphers         HIGH:!aNULL:!MD5;\n", "\n",
                            "    proxy_set_header X-Forwarded-For $remote_addr;\n", "\n"]
        
        #folder containing the folders for certificates
        crtPath = serverAddress["tlspath"]
        listenPort = "    listen " + str(nginxPort)
        if onSSL:
            listenPort = listenPort + " ssl"
        listenPort = listenPort + ";\n"
        
        nginxFile = open(nginxConf, 'r+')
        nginxData = nginxFile.readlines()
        
        ###### Redirect ######
        if not getELS:
            vb = serverAddress["votingbooth"]
            vb = vb[:len(vb)-1]
            
            domain = serverAddress["votingbooth"].split("://")[1]
            domain = domain[:len(domain)-1]
            #certificate folder for this domain
            keyFolder = domain.split(".")
            del keyFolder[0]
            keyFolder = ".".join(keyFolder)
            
            counter = 0
            for line in nginxData:
                if "end main server" in line:
                    break
                counter = counter + 1
            bracketIt = nginxData[counter:]
            del nginxData[counter:]
            
            comments = ["  # Redirect https " + str(electionID) + " \n", "  server {\n", 
                        listenPort, "\n",
                        "    server_name "+ keyFolder + ";\n", "\n"]
            if onSSL:
                comments.extend(["    ssl_certificate " + crtPath + keyFolder + "/fullchain.pem;\n",
                            "    ssl_certificate_key " + crtPath + keyFolder + "/privkey.pem;\n"])
                comments.extend(ssl_adds)
            comments.extend(["    return 302 " + vb, ";\n", "  }\n", "\n"])
            comments.extend(bracketIt)
            nginxData.extend(comments)
            nginxFile.seek(0)
            
            
            csdomain = serverAddress["collectingserver"].split("://")[1]
            csdomain = csdomain[:len(csdomain)-1]
            bbdomain = serverAddress["bulletinboard"].split("://")[1]
            bbdomain = bbdomain[:len(bbdomain)-1]
            authdomain = serverAddress["authenticator"].split("://")[1]
            authdomain = authdomain[:len(authdomain)-1]
            
            cs = serverAddress["collectingserver"]
            cs = cs[:len(cs)-1]
            bb = serverAddress["bulletinboard"]
            bb = bb[:len(bb)-1]
            auth = serverAddress["bulletinboard"]
            auth = auth[:len(auth)-1]
            
            nginxData = redirectHttp(nginxData, electionID, 8080, [domain, keyFolder], vb, 302)
            nginxFile.seek(0)
            nginxData = redirectHttp(nginxData, electionID, 8080, [csdomain], cs, 302)
            nginxFile.seek(0)
            nginxData = redirectHttp(nginxData, electionID, 8080, [bbdomain], bb, 302)
            nginxFile.seek(0)
            nginxData = redirectHttp(nginxData, electionID, 8080, [authdomain], auth, 302)
            nginxFile.seek(0)
            for x in range(numMix):
                mxdomain = serverAddress["mix"+str(x)].split("://")[1]
                mxdomain = mxdomain[:len(mxdomain)-1]
                mx = serverAddress["mix"+str(x)]
                mx = mx[:len(mx)-1]
                redirectHttp(nginxData, electionID, 8080, [mxdomain], mx, 302)
                nginxFile.seek(0)
                
        ###### Collecting server ######
        domain = serverAddress["collectingserver"].split("://")[1]
        domain = domain[:len(domain)-1]
        
        keyFolder = domain.split(".")
        keyFolder[0] = keyFolder[0][:(len(keyFolder[0])-2)]+"00"
        keyFolder = ".".join(keyFolder)
        if not getELS:
            keyFolder = domain.split(".")
            del keyFolder[0]
            keyFolder = ".".join(keyFolder)
            
        counter = 0
        for line in nginxData:
            if "end collecting server" in line:
                break
            counter = counter + 1
        bracketIt = nginxData[counter:]
        del nginxData[counter:]
        
        comments = ["  # Collecting Server " + str(electionID) + " \n", "  server {\n", 
                    listenPort, "\n",
                    "    server_name "+ domain + ";\n", "\n"]
        if onSSL:
            comments.extend(["    ssl_certificate " + crtPath + keyFolder + "/fullchain.pem;\n",
                        "    ssl_certificate_key " + crtPath + keyFolder + "/privkey.pem;\n"])
            comments.extend(ssl_adds)
        comments.extend(["    location " + "~ /.well-known {\n", "        allow all;\n ", "    }\n", "\n"])
        comments.extend(["    location " + "/ {\n", "        proxy_pass " + "http://localhost" + ":" + str(ports[0]) + "/;\n", "    }\n", "\n", "  }\n", "\n"])        
        comments.extend(bracketIt)
        nginxData.extend(comments)
        nginxFile.seek(0)
    
        ###### Bulletin board ######
        domain = serverAddress["bulletinboard"].split("://")[1]
        domain = domain[:len(domain)-1]
        
        keyFolder = domain.split(".")
        keyFolder[0] = keyFolder[0][:(len(keyFolder[0])-2)]+"00"
        keyFolder = ".".join(keyFolder)
        if not getELS:
            keyFolder = domain.split(".")
            del keyFolder[0]
            keyFolder = ".".join(keyFolder)
            
        counter = 0
        for line in nginxData:
            if "end bulletin board" in line:
                break
            counter = counter + 1
        bracketIt = nginxData[counter:]
        del nginxData[counter:]
        
        comments = ["  # Bulletin Board " + str(electionID) + " \n", "  server {\n", 
                    listenPort, "\n",
                    "    server_name "+ domain + ";\n", "\n"]
        if onSSL:
            comments.extend(["    ssl_certificate " + crtPath + keyFolder + "/fullchain.pem;\n",
                        "    ssl_certificate_key " + crtPath + keyFolder + "/privkey.pem;\n"])
            comments.extend(ssl_adds)
        comments.extend(["    location " + "~ /.well-known {\n", "        allow all;\n ", "    }\n", "\n"])
        comments.extend(["    location " + "/ {\n", "        proxy_pass " + "http://localhost" + ":" + str(ports[1]) + "/;\n", "    }\n", "\n", "  }\n", "\n"])
        comments.extend(bracketIt)
        nginxData.extend(comments)
        nginxFile.seek(0)
    
        ###### Mix Server ######
        for x in range(numMix):
            domain = serverAddress["mix"+str(x)].split("://")[1]
            domain = domain[:len(domain)-1]
            
            keyFolder = domain.split(".")
            keyFolder[0] = keyFolder[0][:(len(keyFolder[0])-2)]+"00"
            keyFolder = ".".join(keyFolder)
            if not getELS:
                keyFolder = domain.split(".")
                del keyFolder[0]
                keyFolder = ".".join(keyFolder)
                
            counter = 0
            for line in nginxData:
                if "end mix server " + str(x) in line:
                    break
                counter = counter + 1
            bracketIt = nginxData[counter:]
            del nginxData[counter:]
            
            comments = ["  # Mix Server "+str(x) +" "+ str(electionID) + " \n", "  server {\n", 
                        listenPort, "\n",
                        "    server_name "+ domain + ";\n", "\n"]
            if onSSL:
                comments.extend(["    ssl_certificate " + crtPath + keyFolder + "/fullchain.pem;\n",
                            "    ssl_certificate_key " + crtPath + keyFolder + "/privkey.pem;\n"])
                comments.extend(ssl_adds)
            comments.extend(["    location " + "~ /.well-known {\n", "        allow all;\n ", "    }\n", "\n"])
            comments.extend(["    location " + "/ {\n", "        proxy_pass " + "http://localhost" + ":" + str(ports[x+2]) + "/;\n", "    }\n", "\n", "  }\n", "\n"])
            comments.extend(bracketIt)
            nginxData.extend(comments)
            nginxFile.seek(0)
      
      
        ###### Voting Booth ######
        domain = serverAddress["votingbooth"].split("://")[1]
        domain = domain[:len(domain)-1]
        
        keyFolder = domain.split(".")
        keyFolder[0] = keyFolder[0][:(len(keyFolder[0])-2)]+"00"
        keyFolder = ".".join(keyFolder)
        if not getELS:
            keyFolder = domain.split(".")
            del keyFolder[0]
            keyFolder = ".".join(keyFolder)
            
        counter = 0
        for line in nginxData:
            if "end voting booth" in line:
        	   break
            counter = counter + 1
        bracketIt = nginxData[counter:]
        del nginxData[counter:]
        
        comments = ["  # Voting Booth " + str(electionID) + " \n", "  server {\n", 
                    listenPort, "\n",
                    "    server_name "+ domain + ";\n", "\n"]
        if onSSL:
            comments.extend(["    ssl_certificate " + crtPath + keyFolder + "/fullchain.pem;\n",
                        "    ssl_certificate_key " + crtPath + keyFolder + "/privkey.pem;\n"])
            comments.extend(ssl_adds)
        comments.extend(["    location " + "~ /.well-known {\n", "        allow all;\n ", "    }\n", "\n"])
        comments.extend(["    location " + "/ {\n", "        alias " + dstroot + "/VotingBooth/webapp/;\n", "        index votingBooth.html;\n","    }\n", "\n", "  }\n", "\n"])
        comments.extend(bracketIt)
        nginxData.extend(comments)
        nginxFile.seek(0)
        
        ###### Authenticator ######
        domain = serverAddress["authenticator"].split("://")[1]
        domain = domain[:len(domain)-1]
        
        keyFolder = domain.split(".")
        keyFolder[0] = keyFolder[0][:(len(keyFolder[0])-2)]+"00"
        keyFolder = ".".join(keyFolder)
        if not getELS:
            keyFolder = domain.split(".")
            del keyFolder[0]
            keyFolder = ".".join(keyFolder)
            
        counter = 0
        for line in nginxData:
            if "end authenticator" in line:
                break
            counter = counter + 1
        bracketIt = nginxData[counter:]
        del nginxData[counter:]
        
        comments = ["  # Authenticator " + str(electionID) + " \n", "  server {\n", 
                    listenPort, "\n",
                    "    server_name "+ domain + ";\n", "\n"]
        if onSSL:
            comments.extend(["    ssl_certificate " + crtPath + keyFolder + "/fullchain.pem;\n",
                        "    ssl_certificate_key " + crtPath + keyFolder + "/privkey.pem;\n"])
            comments.extend(ssl_adds)
        comments.extend(["    location " + "~ /.well-known {\n", "        allow all;\n ", "    }\n", "\n"])
        comments.extend(["    location " + "/ {\n", "        alias " + dstroot + "/Authenticator/webapp/;\n", "        index authenticator.html;\n","    }\n", "\n", "  }\n", "\n"])
        comments.extend(bracketIt)
        nginxData.extend(comments)
        nginxFile.seek(0)
        
        nginxFile.writelines(nginxData)
        nginxFile.close()
    else:
        nginxFile = open(nginxConf, 'r+')
        nginxData = nginxFile.readlines()
        prevBracket = 0
        lastBracket = 0
        counter = 0
        for line in nginxData:
            if "}" in line:
                prevBracket = counter
            if "end main server" in line:
                break
            counter = counter + 1
        bracketIt = nginxData[prevBracket:]
        del nginxData[prevBracket:]
        comments = []
        comments.extend(["    # Collecting server " + electionID + " \n", "    location " + "/" + "cs/" + str(ELS) + "/ {\n", "        proxy_pass " + "http://localhost" + ":" + str(ports[0]) + "/;\n", "    }\n", "\n",
                        "    # Bulletin board " + electionID + " \n", "    location " + "/" + "bb/" + str(ELS) + "/ {\n", "        proxy_pass " + "http://localhost" + ":" + str(ports[1]) + "/;\n", "    }\n", "\n"])
        for x in range(numMix):
            comments.extend(["    # Mix server " + electionID + " #"+str(x)+"\n", "    location " + "/" + "m"+str(x)+"/" + str(ELS) + "/ {\n", "        proxy_pass " + "http://localhost" + ":" + str(ports[x+2]) + "/;\n", "    }\n", "\n"])
    
        comments.extend(bracketIt)
        nginxData.extend(comments)
        nginxFile.seek(0)
        
        prevBracket = 0
        counter = 0
        for line in nginxData:
            if "}" in line:
                prevBracket = counter
            if "end main server" in line:
                break
            counter = counter + 1
        bracketIt = nginxData[prevBracket:]
        del nginxData[prevBracket:]
        comments = ["    # Voting Booth " + electionID + " \n", 
                    "    location " + "/" + str(ELS) + "/ {\n", "        alias " + dstroot + "/VotingBooth/webapp/;\n", "        index votingBooth.html;\n","    }\n", "\n"]
        comments.extend(bracketIt)
        nginxData.extend(comments)
        nginxFile.seek(0)    
        
        prevBracket = 0
        counter = 0
        for line in nginxData:
            if "}" in line:
                prevBracket = counter
            if "end main server" in line:
                break
            counter = counter + 1
        bracketIt = nginxData[prevBracket:]
        del nginxData[prevBracket:]
        comments = ["    # Authenticator " + electionID + " \n", 
                    "    location " + "/" + "auth/" + str(ELS) + "/ {\n", "        alias " + dstroot + "/Authenticator/webapp/;\n", "        index authenticator.html;\n","    }\n", "\n"]
        comments.extend(bracketIt)
        nginxData.extend(comments)
        nginxFile.seek(0)   
        
        nginxFile.writelines(nginxData)
        nginxFile.close()
        
    
    #refresh nginx 
    #TODO: fix /usr/sbin nginx issue
    subprocess.call(["/usr/sbin/nginx", "-c", nginxConf,"-s", "reload"], stderr=open(os.devnull, 'w'))

    

#MAIN THREAD STARTS HERE
IDlength = 7

setConfigFiles()
getConfigData()
getInput()
getMixServerConfig()
getServerLocations()
updateKeys()
writeManifest()
sElectCopy(IDlength)
writesElectConfigs()
updateTrustedOrigins()
createBallots()
sElectStart()
writeToHandlerConfig()
writeToNginxConfig()

#prints election details to server.js
electionUrls = {"ElectionIdentifier": electionUtils.hashManifest(sElectDir+manifest), "electionID": electionID,
                "VotingBooth": serverAddress["votingbooth"], "CollectingServer": serverAddress["collectingserver"]+"admin/panel",
                "BulletinBoard": serverAddress["bulletinboard"], "hidden": hidden}
print("electionUrls.json:\n"+json.dumps(electionUrls))
print("electionInfo.json:\n"+json.dumps(eleInfo))

