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
import electionops

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


def updateKeys():
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
    return mixServerEncKey

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
    #get ID after modifying Manifest
    while(iDlength < 40):
        electionID = electionops.getID(sElectDir + manifest, iDlength)
        dstroot = os.path.join(rootDirProject, "elections/" + tStamp[0]+tStamp[1] + "_" + electionID + "_" + os.path.split(sElectDir)[1])
        try:
            copy(sElectDir, dstroot)
            electionops.link(dstroot, manifest, votingManifest)
            break
        except:
            iDlength = iDlength+1
    return (dstroot, electionID) 
        
        
def sElectConfig():
    #modify Server ports
    for x in range(numMix):     
        jwrite.jwrite(dstroot + mixConf[x], "port", ports[x+2])
    jwrite.jwrite(dstroot + collectingConf, "port", ports[0])
    jwrite.jwrite(dstroot + bulletinConf, "port", ports[1])
    jwrite.jwrite(dstroot + votingConf, "authenticate", serverAddress["votingbooth"])
    jwrite.jwrite(dstroot + collectingConf, "serverAdminPassword", password)
    
    #change user randomness if not a mock election
    if not mockElection:
        jwrite.jwrite(dstroot + votingConf, "userChosenRandomness", random)
    

def createBallots():
    #create Ballots
    if mockElection:
        os.mkdir(dstroot+"/CollectingServer/_data_")
        mixServerEncKeyString = str(mixServerEncKey).replace(" ", "").replace("u'", "").replace("'", "")
        ballotFile = dstroot+"/CollectingServer/_data_/accepted_ballots.log"
        for x in range(mockVoters):
            userEmail = "user"+str(x)+"@uni-trier.de"
            userRandom = ''.join([random.choice(string.ascii_letters + string.digits) for n in xrange(8)])
            userChoice = random.randint(0,(len(eleChoices)-1))
            ballots = subprocess.Popen(["node", "createBallots.js", ballotFile, userEmail, userRandom, str(userChoice), electionops.hashManifest(sElectDir+manifest), mixServerEncKeyString], cwd=(rootDirProject+"/ElectionHandler/src"))
        ballots.wait()


def sElectStart():
    #start all node servers
    subprocess.call([dstroot + "/VotingBooth/refresh.sh"], cwd=(dstroot+"/VotingBooth"))
    #vot = subprocess.Popen(["node", "server.js"], cwd=(dstroot+"/VotingBooth"))
    if mockElection:
        col = subprocess.Popen(["node", "collectingServer.js", "--resume"], cwd=(dstroot+"/CollectingServer"))
    else:
        col = subprocess.Popen(["node", "collectingServer.js"], cwd=(dstroot+"/CollectingServer"))
    mix = []
    for x in range(numMix):
        if x < 10:
            mix.append(subprocess.Popen(["node", "mixServer.js"], cwd=(dstroot+"/mix/0"+str(x))))
        else:
            mix.append(subprocess.Popen(["node", "mixServer.js"], cwd=(dstroot+"/mix/"+str(x))))
    bb = subprocess.Popen(["node", "bb.js"], cwd=(dstroot+"/BulletinBoard"))
    newPIDs = [col.pid, bb.pid]
    for x in range(numMix):
        newPIDs.append(mix[x].pid)   
    return newPIDs


def writeConfig():
    #add the password
    jwrite.jwrite(passList, electionID, password)
    
    #add PIDs to config
    for x in range(len(ports)):
        jwrite.jAddList(electionConfig, "usedPorts", ports[x])
    
    #write all election details
    newElection = { "used-ports": ports, "processIDs": newPIDs, "electionID": electionID, "electionTitle": elecTitle, "electionDescription": elecDescr, "startTime": startingTime, "endTime": endingTime, "mixServers": numMix, "ELS": ELS, "timeStamp": sName, "protect": not mockElection}
    jwrite.jAddList(electionConfig, "elections", newElection)
    subprocess.call([sElectDir + "/../ElectionHandler/refreshConfig.sh"], cwd=(sElectDir+"/../ElectionHandler"))
    
    #write minimal election details
    eleInfo = {"electionID": electionID, "electionTitle": elecTitle, "startTime": startingTime, "endTime": endingTime, "ELS": ELS, "protect": not mockElection}
    eleInfo = jwrite.jAddListAndReturn(electionInfo, "elections", eleInfo)
    return eleInfo
    
# the root dir is three folders back
rootDirProject = os.path.realpath(__file__)
for i in range(3):
    rootDirProject=os.path.split(rootDirProject)[0]

# absolute paths
sElectDir = rootDirProject + "/sElect"
electionConfig = rootDirProject + "/_handlerConfigFiles_/handlerConfigFile.json"
electionInfo = rootDirProject + "/_handlerConfigFiles_/electionInfo.json"
defaultManifest = rootDirProject + "/_handlerConfigFiles_/ElectionManifest.json"
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

#get input parameters (if any)
password = "";
mockElection = True
startingTime = addSec(getTime(), -24*60*60).strftime("%Y-%m-%d %H:%M UTC+0000")
endingTime = addSec(getTime(), votingTime).strftime("%Y-%m-%d %H:%M UTC+0000")
if(len(sys.argv) > 2 and len(sys.argv[2]) > 1 ):
    electionArgs = json.loads(sys.argv[2])
    startingTime = electionArgs['startTime']
    endingTime = electionArgs['endTime']
    elecTitle = electionArgs['title']
    elecDescr = electionArgs['description']
    elecQuestion = electionArgs['question']
    eleChoices = electionArgs['choices[]']
    publish = electionArgs['publishVoters']
    publish = True if publish == "true" else False
    random = electionArgs['random']
    random = True if random == "true" else False
    password = electionArgs['password']
    mockElection = False

#mix server config mixFiles
for x in range(numMix):
    if x < 10:
        mixConf.append("/templates/config_mix0" + str(x) + ".json")
    else:
        mixConf.append("/templates/config_mix" + str(x) + ".json")


#get server URI's
ports = electionops.usePorts(electionConfig, 3+numMix)
ELS = ports[len(ports)-1]                                   #for the demo version the ELS will be the port of VotingBooth
serverAddress = electionops.getsAddress(electionConfig, deployment, numMix, nginxPort, ELS, serverAddr)
tStamp = startingTime.replace("-", "").replace(":", "").split()
sName = tStamp[0] + tStamp[1]


mixServerEncKey = updateKeys()
writeManifest()
dstroot, electionID = sElectCopy(7)
sElectConfig()
createBallots()
newPIDs = sElectStart()
eleInfo = writeConfig()




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
    comments = ["    # Voting Booth" + electionID + " \n", "    location " + "/" + str(ELS) + "/ {\n", "        alias " + dstroot + "/VotingBooth/webapp/;\n", "        index votingBooth.html;\n","    }\n", "\n", "  }\n", "\n"]
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


jwrite.jwrite(electionConfig, "electionsCreated", createdElections+1)

#refresh nginx 
#TODO: fix /usr/sbin nginx issue
subprocess.call(["/usr/sbin/nginx", "-c", nginxConf,"-s", "reload"], stderr=open(os.devnull, 'w'))

#prints election details to server.js
print("electionInfo.json:\n"+json.dumps(eleInfo))

