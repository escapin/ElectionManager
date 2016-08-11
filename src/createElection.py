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
        shutil.copytree(src, dest, symlinks=False, ignore=ignore_patterns("*.py", "00", "01", "02", "ElectionHandler", "nginx*"))
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
    global hidden
    
    #get input parameters (if any)
    password = "";
    mockElection = True
    startingTime = addSec(getTime(), -24*60*60).strftime("%Y-%m-%d %H:%M UTC+0000")
    endingTime = addSec(getTime(), votingTime).strftime("%Y-%m-%d %H:%M UTC+0000")
    randomness = False
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
        password = electionArgs['password']
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
    ELS = ports[len(ports)-1]                                   #for the demo version the ELS will be the port of VotingBooth
    serverAddress = electionUtils.getsAddress(electionConfig, deployment, numMix, nginxPort, ELS, serverAddr)
    #time stamp for folder path
    tStamp = startingTime.replace("-", "").replace(":", "").split()
    sName = tStamp[0] + tStamp[1]

def updateKeys():
    global mixServerEncKey
    
    #update encryption keys
    pattern="[0-9]+"
    keyGeneratorMix_file="genKeys4mixServer.js"
    keyGeneratorCS_file="genKeys4collectingServer.js"
    tools_path = sElectDir + "/tools"
    
    keys = check_output(["node", os.path.join(tools_path,"keyGen.js"), str(numMix+1)]).splitlines()
    
    #write new keys to manifest and config files
    jwrite.jwriteAdv(sElectDir + manifest, "collectingServer", json.loads(keys[len(keys)-1])["encryptionKey"], "encryption_key")
    jwrite.jwriteAdv(sElectDir + manifest, "collectingServer", json.loads(keys[len(keys)-1])["verificationKey"], "verification_key")
    jwrite.jwrite(sElectDir + collectingConf, "signing_key", json.loads(keys[len(keys)-1])["signingKey"])
    jwrite.jwrite(sElectDir + collectingConf, "decryption_key", json.loads(keys[len(keys)-1])["decryptionKey"])
    for x in range(numMix):
        jwrite.jwriteAdv(sElectDir + manifest, "mixServers", json.loads(keys[x])["encryptionKey"], x, "encryption_key")
        jwrite.jwriteAdv(sElectDir + manifest, "mixServers", json.loads(keys[x])["verificationKey"], x, "verification_key")
        jwrite.jwrite(sElectDir + mixConf[x], "encryption_key", json.loads(keys[x])["encryptionKey"])
        jwrite.jwrite(sElectDir + mixConf[x], "verification_key", json.loads(keys[x])["verificationKey"])
        jwrite.jwrite(sElectDir + mixConf[x], "signing_key", json.loads(keys[x])["signingKey"])
        jwrite.jwrite(sElectDir + mixConf[x], "decryption_key", json.loads(keys[x])["decryptionKey"])
    
    #get new keys
    mixServerEncKey = []
    for x in range(numMix):
        mixServerEncKey.append(json.loads(keys[x])["encryptionKey"])

def writeManifest():
    #modify ElectionManifest, if no arguments are given, this is a mock election
    jwrite.jwrite(sElectDir + manifest, "startTime", startingTime)
    jwrite.jwrite(sElectDir + manifest, "endTime", endingTime)
    jwrite.jwrite(sElectDir + manifest, "title", elecTitle)
    jwrite.jwrite(sElectDir + manifest, "description", elecDescr)
    jwrite.jwrite(sElectDir + manifest, "question", elecQuestion)
    jwrite.jwrite(sElectDir + manifest, "choices", eleChoices)
    jwrite.jwrite(sElectDir + manifest, "userChosenRandomness", randomness)
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
    jwrite.jwrite(dstroot + votingConf, "authenticate", serverAddress["votingbooth"])
    jwrite.jwrite(dstroot + collectingConf, "serverAdminPassword", password)
    for x in range(numMix):     
        jwrite.jwrite(dstroot + mixConf[x], "port", ports[x+2])
        
    #change user randomness if not a mock election
    if not mockElection:
        jwrite.jwrite(dstroot + votingConf, "userChosenRandomness", randomness)
    else:
        jwrite.jwrite(dstroot + votingConf, "showOtp", True)
        jwrite.jwrite(dstroot + collectingConf, "sendOtpBack", True)
    

def createBallots():
    if mockElection:
        #check if random or not
        isRand = False
        try:
            jsonFile = open(sElectDir+manifest, 'r')
            jsonData = json.load(jsonFile, object_pairs_hook=collections.OrderedDict)
            isRand = jsonData["userChosenRandomness"]
            jsonFile.close()
        except IOError:
            sys.exit("ElectionManifest.json missing or corrupt")
        #create Ballots
        os.mkdir(dstroot+"/CollectingServer/_data_")
        mixServerEncKeyString = str(mixServerEncKey).replace(" ", "").replace("u'", "").replace("'", "")
        ballotFile = dstroot+"/CollectingServer/_data_/accepted_ballots.log"
        for x in range(mockVoters):
            userEmail = "user"+str(x)+"@uni-trier.de"
            userRandom = "".join([random.choice(string.ascii_letters + string.digits) for n in xrange(8)]) if isRand else ""
            userChoice = random.randint(0,(len(eleChoices)-1))
            ballots = subprocess.Popen(["node", "createBallots.js", ballotFile, userEmail, userRandom, str(userChoice), electionUtils.hashManifest(sElectDir+manifest), mixServerEncKeyString], cwd=(rootDirProject+"/src"))
        ballots.wait()


def sElectStart():
    global newPIDs
    
    if not os.path.exists(dstroot+"/STDOUT_STDERR"):
        os.makedirs(dstroot+"/STDOUT_STDERR")
    logfolder = dstroot+"/STDOUT_STDERR"
    
    #start all node servers
    
    subprocess.call([dstroot + "/VotingBooth/refresh.sh"], cwd=(dstroot+"/VotingBooth"))
    with open(logfolder+"/ColllectingServer.log", 'w') as file_out:
        if mockElection:
            col = subprocess.Popen(["node", "collectingServer.js", "--resume"], stdout=file_out, stderr=subprocess.STDOUT, cwd=(dstroot+"/CollectingServer"))
        else:
            col = subprocess.Popen(["node", "collectingServer.js"], stdout=file_out, stderr=subprocess.STDOUT, cwd=(dstroot+"/CollectingServer"))
    with open(logfolder+"/MixServer.log", 'w') as file_out:
        mix = []
        for x in range(numMix):
            if x < 10:
                mix.append(subprocess.Popen(["node", "mixServer.js"], stdout=file_out, stderr=subprocess.STDOUT, cwd=(dstroot+"/mix/0"+str(x))))
            else:
                mix.append(subprocess.Popen(["node", "mixServer.js"], stdout=file_out, stderr=subprocess.STDOUT, cwd=(dstroot+"/mix/"+str(x))))
    with open(logfolder+"/BulletinBoard.log", 'w') as file_out:
        bb = subprocess.Popen(["node", "bb.js"], cwd=(dstroot+"/BulletinBoard"))
        newPIDs = [col.pid, bb.pid]
        for x in range(numMix):
            newPIDs.append(mix[x].pid)   


def writeToHandlerConfig():
    global eleInfo
    global electionUrls
    #add the password
    jwrite.jwrite(passList, electionID, password)
    
    #add ports to config
    for x in range(len(ports)):
        jwrite.jAddList(electionConfig, "usedPorts", ports[x])
    electionUrls = {"ElectionIdentifier": electionUtils.hashManifest(sElectDir+manifest), "VotingBooth": serverAddress["votingbooth"], "CollectingServerAdmin": serverAddress["collectingserver"] + "admin/panel/", "BulletinBoard": serverAddress["bulletinboard"]}
    electionUrls["handlerVisibility"] = "hidden" if hidden else "visible"
    jwrite.jwrite(electionURI, electionID, electionUrls)
    electionUrls["electionID"] = electionID
    
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
    #modify nginx File
    if "http://localhost" not in serverAddress["collectingserver"]:
        nginxFile = open(nginxConf, 'r+')
        nginxData = nginxFile.readlines()
        prevBracket = 0
        counter = 0
        for line in nginxData:
            if "}" in line:
                prevBracket = counter
            if "end collecting server" in line:
                break
            counter = counter + 1
        bracketIt = nginxData[prevBracket:]
        del nginxData[prevBracket:]
        comments = ["    # Collecting server " + electionID + " \n", "    location " + "/" + str(ELS) + "/ {\n", "        proxy_pass " + "http://localhost" + ":" + str(ports[0]) + "/;\n", "    }\n", "\n"]
        comments.extend(bracketIt)
        nginxData.extend(comments)
        nginxFile.seek(0)
    
        prevBracket = 0
        counter = 0
        for line in nginxData:
            if "}" in line:
                prevBracket = counter
            if "end bulletin board" in line:
                break
            counter = counter + 1
        bracketIt = nginxData[prevBracket:]
        del nginxData[prevBracket:]
        comments = ["    # Bulletin board " + electionID + " \n", "    location " + "/" + str(ELS) + "/ {\n", "        proxy_pass " + "http://localhost" + ":" + str(ports[1]) + "/;\n", "    }\n", "\n"]
        comments.extend(bracketIt)
        nginxData.extend(comments)
        nginxFile.seek(0)
    
        for x in range(numMix):
            prevBracket = 0
            counter = 0
            for line in nginxData:
                if "}" in line:
                    prevBracket = counter
                if "end mix server "+str(x) in line:
                    break
                counter = counter + 1
            bracketIt = nginxData[prevBracket:]
            del nginxData[prevBracket:]
            comments = ["    # Mix server " + electionID + " #"+str(x)+"\n", "    location " + "/" + str(ELS) + "/ {\n", "        proxy_pass " + "http://localhost" + ":" + str(ports[x+2]) + "/;\n", "    }\n", "\n"]
            comments.extend(bracketIt)
            nginxData.extend(comments)
            nginxFile.seek(0)
      
        prevBracket = 0
        counter = 0
        for line in nginxData:
            if "}" in line:
                prevBracket = counter
            if "end voting booth" in line:
                break
            counter = counter + 1
        bracketIt = nginxData[prevBracket:]
        del nginxData[prevBracket:]
        comments = ["    # Voting Booth " + electionID + " \n", "    location " + "/" + str(ELS) + "/ {\n", "        alias " + dstroot + "/VotingBooth/webapp/;\n", "        index votingBooth.html;\n","    }\n", "\n"]
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
createBallots()
sElectStart()
writeToHandlerConfig()
writeToNginxConfig()

#prints election details to server.js
print("electionUrls.json:\n"+json.dumps(electionUrls))
print("electionInfo.json:\n"+json.dumps(eleInfo))

