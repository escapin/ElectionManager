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


def copy(src, dest):
    try:
        shutil.copytree(src, dest, symlinks=False, ignore=ignore_patterns("*.py", "00", "01", "02", "Authenticator", "tests"))
    except OSError as e:
        # source is a file, not a directory
        if e.errno == errno.ENOTDIR:
            shutil.copy(src, dest)
        else:
            print("Directory not copied. Error: %s" % e)

def getTime():
    utcTime = datetime.datetime.utcnow()
    return utcTime

def addSec(tm, secs):
    fulldate = tm + datetime.timedelta(seconds=secs)
    return fulldate

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
    global mixConf

    # the root dir is three folders back
    rootDirProject = os.path.realpath(__file__)
    for i in range(2):
        rootDirProject=os.path.split(rootDirProject)[0]
    
    # absolute paths
    sElectDir = rootDirProject + "/sElect"
    electionConfig = rootDirProject + "/_configFiles_/handlerConfigFile.json"
    electionInfo = rootDirProject + "/_configFiles_/electionInfo.json"
    defaultManifest = rootDirProject + "/_configFiles_/ElectionManifest.json"
    electionURI = rootDirProject + "/_configFiles_/electionsURI.json"
    electionInfoHidden = rootDirProject + "/elections_hidden/electionInfo.json"
    nginxConf =  rootDirProject + "/nginx_config/nginx_select.conf"
    passList =  rootDirProject + "/ElectionHandler/_data_/pwd.json"
    nginxLog = rootDirProject + "/nginx_config/log"
    
    # sElect (partial) mixFiles path
    manifest = "/_sElectConfigFiles_/ElectionManifest.json"
    collectingConf = "/CollectingServer/config.json"
    bulletinConf = "/BulletinBoard/config.json"
    votingManifest = "/VotingBooth/ElectionManifest.json"     
    votingConf = "/VotingBooth/config.json"  
    mixConf = []
    
def getConfigData():
    #get duration and deployment status from handlerConfigFile
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
    global eleChoices
    global publish
    global mixServers
    
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
            serverAddr = rootDirProject + "/deployment/serverAddresses.json"
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
        mixServers = jsonData["mixServers"]
        minChoices = jsonData["minChoicesPerVoter"]
        maxChoices = jsonData["maxChoicesPerVoter"]
        jsonFile.close()
    except IOError:
        sys.exit("ElectionManifest missing or corrupt")
        
def getInput():
    global password
    global mockElection
    global startingTime
    global endingTime
    
    global elecTitle
    global elecDescr
    global elecQuestion
    global eleChoices
    global publish
    global mixServers
    global randomness
    global keys
    global hidden
    
    #get input parameters (if any)
    password = "";
    mockElection = True
    startingTime = addSec(getTime(), -24*60*60).strftime("%Y-%m-%d %H:%M UTC+0000")
    endingTime = addSec(getTime(), votingTime).strftime("%Y-%m-%d %H:%M UTC+0000")
    randomness = False
    if "mockElection" in sys.argv[1]:
        mockArgs = json.loads(sys.argv[1])
        randomness = mockArgs["userChosenRandomness"]
        randomness = True if randomness == "true" else False
        keys = mockArgs["keys"]
    hidden = True if sys.argv[1] == "true" else False
    if(len(sys.argv) > 2 and len(sys.argv[2]) > 1 ):
        electionArgs = json.loads(sys.argv[2])
        startingTime = electionArgs['startTime']
        endingTime = electionArgs['endTime']
        elecTitle = electionArgs['title']
        elecDescr = electionArgs['description']
        elecQuestion = electionArgs['question']
        try:
            eleChoices = electionArgs['choices[]']
        except:
            eleChoices = electionArgs['choices']
        publish = electionArgs['publishListOfVoters']
        randomness = electionArgs['userChosenRandomness']
        randomness = True if randomness == "true" else False
        password = electionArgs['password']
        if "keys" in electionArgs:
            keys = electionArgs["keys"]
        else:
            keys = []
        mockElection = False


def getMixServerConfig():
    global mixConf
    
    #mix server config mixFiles
    for x in range(numMix):
        if x < 10:
            mixConf.append("/templates/config_mix0" + str(x) + ".json")
        else:
            mixConf.append("/templates/config_mix" + str(x) + ".json")

def getServerLocations():
    global ports
    global ELS
    global serverAddress
    global tStamp
    global sName
    
    #get server URI's
    ports = electionUtils.usePorts(electionConfig, 3+numMix)
    ELS = electionUtils.getELS(electionConfig)                      #number between 00 and 100/maxElections, corresponds with subdomains
    serverAddress = electionUtils.getsAddress(electionConfig, deployment, numMix, nginxPort, ELS, serverAddr)
    #time stamp for folder path
    tStamp = startingTime.replace("-", "").replace(":", "").split()
    sName = tStamp[0] + tStamp[1]

def updateKeys():
    global mixServerEncKey
    global keys
    
    #update encryption keys
    pattern="[0-9]+"
    keyGeneratorMix_file="genKeys4mixServer.js"
    keyGeneratorCS_file="genKeys4collectingServer.js"
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
    jwrite.jwrite(sElectDir + manifest, "question", elecQuestion)
    jwrite.jwrite(sElectDir + manifest, "choices", eleChoices)
    jwrite.jwrite(sElectDir + manifest, "publishListOfVoters", publish)
    jwrite.jwriteAdv(sElectDir + manifest, "collectingServer", serverAddress["collectingserver"], "URI")
    jwrite.jwriteAdv(sElectDir + manifest, "bulletinBoards", serverAddress["bulletinboard"], 0, "URI")
    for x in range(numMix):
        jwrite.jwriteAdv(sElectDir + manifest, "mixServers", serverAddress["mix"+str(x)], x, "URI")


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
            electionUtils.link(dstroot, manifest, votingManifest)
            break
        except:
            iDlength = iDlength+1

        
def writesElectConfigs():
    #modify Server ports
    jwrite.jwrite(dstroot + collectingConf, "port", ports[0])
    jwrite.jwrite(dstroot + bulletinConf, "port", ports[1])
    jwrite.jwrite(dstroot + votingConf, "authenticator", serverAddress["authenticator"])
    jwrite.jwrite(dstroot + votingConf, "authChannel", serverAddress["authchannel"])
    jwrite.jwrite(dstroot + votingConf, "userChosenRandomness", randomness)
    jwrite.jwrite(dstroot + collectingConf, "serverAdminPassword", password)
    for x in range(numMix):     
        jwrite.jwrite(dstroot + mixConf[x], "port", ports[x+2])
        
    #change user randomness if not a mock election
    if mockElection:
        jwrite.jwrite(dstroot + votingConf, "showOtp", True)
        jwrite.jwrite(dstroot + collectingConf, "sendOtpBack", True)
        jwrite.jwrite(dstroot + collectingConf, "sendEmail", False)

def updateTrustedDomains():
    authdomain = serverAddress["authenticator"]
    vbdomain = serverAddress["votingbooth"]
    vbdomain = vbdomain[:len(vbdomain)-1]
    varname = "trustedDomains"
    csTrusts = 'var '+varname+' = ["'+vbdomain+'","'+authdomain+'"];'
    csFile = "/CollectingServer/webapp/trustedDomains.js"
    file = open(dstroot+csFile, 'w')
    file.write(csTrusts)
    file.close()

def createBallots():
    if mockElection:
        #create Ballots
        os.mkdir(dstroot+"/CollectingServer/_data_")
        mixServerEncKeyString = str(mixServerEncKey).replace(" ", "").replace("u'", "").replace("'", "")
        ballotFile = dstroot+"/CollectingServer/_data_/accepted_ballots.log"
        for x in range(mockVoters):
            nChoices = random.randint(minChoices,maxChoices)
            userRandom = []
            userChoices = []
            for i in range(len(nChoices)):
                userChoice.append(random.randint(0,(len(eleChoices)-1)))
            userRandom = "".join([random.choice(string.ascii_letters + string.digits) for n in xrange(8)]) if randomness else ""
            userEmail = "user"+str(x)+"@uni-trier.de"
            userChoices = str(userChoices).replace(" ", "").replace("u'", "").replace("'", "")
            ballots = subprocess.Popen(["node", "createBallots.js", ballotFile, userEmail, userRandom, userChoices, electionUtils.hashManifest(sElectDir+manifest), mixServerEncKeyString], cwd=(rootDirProject+"/src"))
        ballots.wait()


def sElectStart():
    global newPIDs
    
    if not os.path.exists(dstroot+"/LOG"):
        os.makedirs(dstroot+"/LOG")
    logfolder = dstroot+"/LOG"
    
    #start all node servers
    subprocess.Popen(["node", "compileEJS.js"], cwd=(dstroot+"/VotingBooth/webapp/ejs"))
    subprocess.call([dstroot + "/VotingBooth/refresh.sh"], cwd=(dstroot+"/VotingBooth"))
    with open(logfolder+"/ColllectingServer.log", 'w') as file_out:
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
        newPIDs = [col.pid, bb.pid]
        for x in range(numMix):
            newPIDs.append(mix[x].pid)   


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
    

def writeToNginxConfig():
    onSSL = True
    crtPath = "/etc/letsencrypt/live/"
    listenPort = "    listen " + str(nginxPort)
    if onSSL:
        listenPort = listenPort + " ssl"
    listenPort = listenPort + ";\n"
    
    #modify nginx File
    if "http://localhost" not in serverAddress["collectingserver"]:
        nginxFile = open(nginxConf, 'r+')
        nginxData = nginxFile.readlines()
        
        ###### Collecting server ######
        domain = serverAddress["collectingserver"].split("://")[1]
        domain = domain[:len(domain)-1]
        keyFolder = domain.split(".")
        keyFolder[0] = keyFolder[0][:(len(keyFolder[0])-2)]+"00"
        keyFolder = ".".join(keyFolder)
        prevBracket = 0
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
                        "    ssl_certificate_key " + crtPath + keyFolder + "/privkey.pem;\n",
                        "    ssl_protocols       TLSv1 TLSv1.1 TLSv1.2;\n",
                        "    ssl_ciphers         HIGH:!aNULL:!MD5;\n", "\n",
                        "    proxy_set_header X-Forwarded-For $remote_addr;\n", "\n"])
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
        prevBracket = 0
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
                        "    ssl_certificate_key " + crtPath + keyFolder + "/privkey.pem;\n",
                        "    ssl_protocols       TLSv1 TLSv1.1 TLSv1.2;\n",
                        "    ssl_ciphers         HIGH:!aNULL:!MD5;\n", "\n",
                        "    proxy_set_header X-Forwarded-For $remote_addr;\n", "\n"])
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
            prevBracket = 0
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
	                    "    ssl_certificate_key " + crtPath + keyFolder + "/privkey.pem;\n",
                            "    ssl_protocols       TLSv1 TLSv1.1 TLSv1.2;\n",
                            "    ssl_ciphers         HIGH:!aNULL:!MD5;\n", "\n",
                            "    proxy_set_header X-Forwarded-For $remote_addr;\n", "\n"])
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
        prevBracket = 0
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
                        "    ssl_certificate_key " + crtPath + keyFolder + "/privkey.pem;\n",
                        "    ssl_protocols       TLSv1 TLSv1.1 TLSv1.2;\n",
                        "    ssl_ciphers         HIGH:!aNULL:!MD5;\n", "\n",
                        "    proxy_set_header X-Forwarded-For $remote_addr;\n", "\n"])
        comments.extend(["    location " + "~ /.well-known {\n", "        allow all;\n ", "    }\n", "\n"])
        comments.extend(["    location " + "/ {\n", "        alias " + dstroot + "/VotingBooth/webapp/;\n", "        index votingBooth.html;\n","    }\n", "\n", "  }\n", "\n"])
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
updateTrustedDomains()
createBallots()
sElectStart()
writeToHandlerConfig()
writeToNginxConfig()

#prints election details to server.js
electionUrls = {"ElectionIdentifier": electionUtils.hashManifest(sElectDir+manifest), "electionID": electionID,
                "VotingBooth": serverAddress["votingbooth"], "CollectingServer": serverAddress["collectingserver"]+"/admin/panel", 
                "BulletinBoard": serverAddress["bulletinboard"], "hidden": hidden}
print("electionUrls.json:\n"+json.dumps(electionUrls))
print("electionInfo.json:\n"+json.dumps(eleInfo))

