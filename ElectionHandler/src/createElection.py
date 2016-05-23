import os
import json
import shutil
from shutil import ignore_patterns
import collections
import errno
import datetime
import sys
import hashlib
import codecs
import subprocess
from subprocess import check_output
import time
import random
import string
import re
import timeit

def copy(src, dest):
    try:
        shutil.copytree(src, dest, symlinks=False, ignore=ignore_patterns("*.py", "00", "01", "02", "ElectionHandler", "nginx*"))
    except OSError as e:
        # source is a file, not a directory
        if e.errno == errno.ENOTDIR:
            shutil.copy(src, dest)
        else:
            print("Directory not copied. Error: %s" % e)
            
def link(dest):
    os.mkdir(dstroot+"/mix/00")
    os.mkdir(dstroot+"/mix/01")
    os.mkdir(dstroot+"/mix/02")
    os.symlink(dstroot+"/MixServer/run.sh", dstroot+"/mix/00/run.sh")
    os.symlink(dstroot+"/MixServer/cleanData.sh", dstroot+"/mix/00/cleanData.sh")
    os.symlink(dstroot+"/MixServer/mixServer.js", dstroot+"/mix/00/mixServer.js")
    os.symlink(dstroot+"/templates/config_mix00.json", dstroot+"/mix/00/config.json")
    
    os.symlink(dstroot+"/MixServer/run.sh", dstroot+"/mix/01/run.sh")
    os.symlink(dstroot+"/MixServer/cleanData.sh", dstroot+"/mix/01/cleanData.sh")
    os.symlink(dstroot+"/MixServer/mixServer.js", dstroot+"/mix/01/mixServer.js")
    os.symlink(dstroot+"/templates/config_mix01.json", dstroot+"/mix/01/config.json")
    
    os.symlink(dstroot+"/MixServer/run.sh", dstroot+"/mix/02/run.sh")
    os.symlink(dstroot+"/MixServer/cleanData.sh", dstroot+"/mix/02/cleanData.sh")
    os.symlink(dstroot+"/MixServer/mixServer.js", dstroot+"/mix/02/mixServer.js")
    os.symlink(dstroot+"/templates/config_mix02.json", dstroot+"/mix/02/config.json")
    
    os.remove(dstroot + votingManifest)
    os.symlink(dstroot + manifest, dstroot + votingManifest)

def copyFast(src, dest):
    if sys.platform.startswith("win"):
        os.system("xcopy /s " + src + " " + dest)
    else:
        os.system("cp -rf " + src + " " + dest)

def jwrite(src, key, value):
    try:
        jsonFile = open(src, 'r+')
        jsonData = json.load(jsonFile, object_pairs_hook=collections.OrderedDict)
        jsonData[key] = value
        jsonFile.seek(0)
    except IOError:
        jsonFile = open(src, 'w')
        jsonData = {key: value}
    json.dump(jsonData, jsonFile, indent = 4)
    jsonFile.truncate()
    jsonFile.close()
    
def jwriteAdv(src, key, value, pos="", key2=""):
    if pos is "" and key2 is "":
        jwrite(src, key, value)
    else:
        try:
            jsonFile = open(src, 'r+')
            jsonData = json.load(jsonFile, object_pairs_hook=collections.OrderedDict)
            if key2 is "":
                jsonData[key][pos] = value
            else:
                jsonData[key][pos][key2] = value
            jsonFile.seek(0)
        except IOError:
            jsonFile = open(src, 'w')
            if key2 is "":
                jsonData = {key: {pos: value}}
            else:
                jsonData = {key: {key2: value}}
            jsonData = {key: value}
        json.dump(jsonData, jsonFile, indent = 4)
        jsonFile.truncate()
        jsonFile.close()
        
def jAddList(src, key, value):
    try:
        jsonFile = open(src, 'r+')
        jsonData = json.load(jsonFile, object_pairs_hook=collections.OrderedDict)
        iDs = jsonData[key]
        iDs.append(value)
        jsonData[key] = iDs
        jsonFile.seek(0)
    except IOError:
        jsonFile = open(src, 'w')
        jsonData = {key: value}
    json.dump(jsonData, jsonFile, indent = 4)
    jsonFile.truncate()
    jsonFile.close()

def getTime():
    utcTime = datetime.datetime.utcnow()
    return utcTime

def addSec(tm, secs):
    fulldate = tm + datetime.timedelta(seconds=secs)
    return fulldate

def usePorts():
    newPorts = []
    try:
        jsonFile = open(electionConfig, 'r')
        jsonData = json.load(jsonFile, object_pairs_hook=collections.OrderedDict)
        rangePorts = jsonData["available-ports"]
        elecs = jsonData["elections"]
        usingPorts = []
        for x in range (len(elecs)):
            usingPorts.extend(elecs[x]["used-ports"]) 
        for openPort in range(rangePorts[0], rangePorts[1]):
            if openPort in usingPorts:
                continue
            newPorts.append(openPort)
            if len(newPorts) >= 2+len(mixServers):
                break
        if len(newPorts) < 2+len(mixServers):
            sys.exit("Not enough ports available.")
        jsonFile.close()
    except IOError:
        sys.exit("handlerConfigFile.json missing or corrupt")
    return newPorts

def getsAddress():
    sAddress = []
    try:
        jsonFile = open(electionConfig, 'r')
        jsonData = json.load(jsonFile, object_pairs_hook=collections.OrderedDict)
        if not deployment:
            for x in range(4+len(mixServers)):
                sAddress.append("http://localhost:"+str(jsonData["nginx-port"]))
            sAddress.append("http://localhost:"+str(jsonData["nginx-port"])+"/auth")
            jsonFile.close()
        else:
            jsonFile.close()
            jsonFile = open(serverAddr, 'r')
            jsonData = json.load(jsonFile, object_pairs_hook=collections.OrderedDict)
            addresses = jsonData["server-address"]
            sAddress.append(addresses["collectingserver"])
            sAddress.append(addresses["bulletinboard"])
            sAddress.append(addresses["votingbooth"])
            sAddress.append(addresses["authbooth"])
            for x in range(len(mixServers)):
                sAddress.append(addresses["mix"+str(x)])
        jsonFile.close()
    except IOError:
        sys.exit("serverAddresses.json missing or corrupt")
    return sAddress

def getID(num):
    manifestHash = hashManifest()
    elecID = manifestHash[:num]
    print(manifestHash)
    return elecID

def hashManifest():
    manifest_raw = codecs.open(sElectDir + manifest, 'r', encoding='utf8').read()
    manifest_raw = manifest_raw.replace("\n", '').replace("\r", '').strip()
    m = hashlib.sha256()
    m.update(manifest_raw)
    return m.hexdigest()

# sElect (partial) mixFiles path
manifest = "/_sElectConfigFiles_/ElectionManifest.json"
collectingConf = "/CollectingServer/config.json"
bulletinConf = "/BulletinBoard/config.json"
votingManifest = "/VotingBooth/ElectionManifest.json"     
votingConf = "/VotingBooth/config.json"  




# the root dir is three folders back
rootDirProject = os.path.realpath(__file__)
for i in range(3):
    rootDirProject=os.path.split(rootDirProject)[0]
#print rootDirProject

# absolute paths
sElectDir = rootDirProject + "/sElect"
electionConfig = rootDirProject + "/_handlerConfigFiles_/handlerConfigFile.json"
defaultManifest = rootDirProject + "/_handlerConfigFiles_/ElectionManifest.json"
nginxConf =  rootDirProject + "/nginx_config/nginx_select.conf"
passList =  rootDirProject + "/ElectionHandler/_data_/pwd.json"
nginxLog = rootDirProject + "/nginx_config/log"

#get duration and deployment status from handlerConfigFile
deployment = False
try:
    jsonFile = open(electionConfig, 'r')
    jsonData = json.load(jsonFile, object_pairs_hook=collections.OrderedDict)
    votingTime = jsonData["electionDurationInHours"]*60*60    #hours to seconds
    mockVoters = jsonData["numberOfMockVoters"]
    nginxPort = jsonData["nginx-port"]
    if jsonData["deployment"] is True:
        serverAddr = rootDirProject + "/deployment/serverAddresses.json"
        deployment = True
    jsonFile.close()
except IOError:
    sys.exit("handlerConfigFile.json missing or corrupt (electionDurationInHours)")

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
    
    
ports = json.loads(sys.argv[1])['usedPorts']
ELS = ports[len(ports)-1]                                   #for the demo version the ELS will be the port of VotingBooth
increment = json.loads(sys.argv[1])['electionsCreated']
tStamp = startingTime.replace("-", "").replace(":", "").split()
sName = tStamp[0] + tStamp[1] + "_" + str(increment)


#where the servers are placed
serverAddress = getsAddress()

#mix server config mixFiles
mixConf = []
for x in range(len(mixServers)):
    if x < 10:
        mixConf.append("/templates/config_mix0" + str(x) + ".json")
    else:
        mixConf.append("/templates/config_mix" + str(x) + ".json")

#update keys
pattern="[0-9]+"
keyGeneratorMix_file="genKeys4mixServer.js"
keyGeneratorCS_file="genKeys4collectingServer.js"
tools_path = sElectDir + "/tools"

keys = check_output(["node", os.path.join(tools_path,"keyGen.js"), str(len(mixServers))]).splitlines()

#write new keys to manifest and config files
jwriteAdv(sElectDir + manifest, "collectingServer", json.loads(keys[len(keys)-1])["encryptionKey"], "encryption_key")
jwriteAdv(sElectDir + manifest, "collectingServer", json.loads(keys[len(keys)-1])["verificationKey"], "verification_key")
jwrite(sElectDir + collectingConf, "signing_key", json.loads(keys[len(keys)-1])["signingKey"])
jwrite(sElectDir + collectingConf, "decryption_key", json.loads(keys[len(keys)-1])["decryptionKey"])
for x in range(len(mixServers)):
    jwriteAdv(sElectDir + manifest, "mixServers", json.loads(keys[x])["encryptionKey"], x, "encryption_key")
    jwriteAdv(sElectDir + manifest, "mixServers", json.loads(keys[x])["verificationKey"], x, "verification_key")
    jwrite(sElectDir + mixConf[x], "encryption_key", json.loads(keys[x])["encryptionKey"])
    jwrite(sElectDir + mixConf[x], "verification_key", json.loads(keys[x])["verificationKey"])
    jwrite(sElectDir + mixConf[x], "signing_key", json.loads(keys[x])["signingKey"])
    jwrite(sElectDir + mixConf[x], "decryption_key", json.loads(keys[x])["decryptionKey"])


#modify ElectionManifest, if no arguments are given, this is a mock election
jwrite(sElectDir + manifest, "startTime", startingTime)
jwrite(sElectDir + manifest, "endTime", endingTime)
jwrite(sElectDir + manifest, "title", elecTitle)
jwrite(sElectDir + manifest, "description", elecDescr)
jwrite(sElectDir + manifest, "question", elecQuestion)
jwrite(sElectDir + manifest, "choices", eleChoices)  
jwrite(sElectDir + manifest, "publishListOfVoters", publish)

if "localhost" not in serverAddress[0]:
    jwriteAdv(sElectDir + manifest, "collectingServer", serverAddress[0] + "/" + str(ELS) + "/", "URI")    #str(ports[0])
    jwriteAdv(sElectDir + manifest, "bulletinBoards", serverAddress[1] + "/" + str(ELS) + "/", 0, "URI")   #str(ports[1])
    for x in range(len(mixServers)):
        jwriteAdv(sElectDir + manifest, "mixServers", serverAddress[x+4] + "/" + str(ELS) + "/", x, "URI")       #str(ports[x+2])   
else:
    jwriteAdv(sElectDir + manifest, "collectingServer", serverAddress[0] + "/" + "cs/" + str(ELS) + "/", "URI")    #str(ports[0])
    jwriteAdv(sElectDir + manifest, "bulletinBoards", serverAddress[1] + "/" + "bb/" + str(ELS) + "/", 0, "URI")   #str(ports[1])
    for x in range(len(mixServers)):
        jwriteAdv(sElectDir + manifest, "mixServers", serverAddress[x+4] + "/" + "m"+str(x)+"/" + str(ELS) + "/", x, "URI")       #str(ports[x+2])

#get new keys
try:
    jsonFile = open(sElectDir + manifest, 'r')
    jsonData = json.load(jsonFile, object_pairs_hook=collections.OrderedDict)
    mixServers = jsonData["mixServers"]
    mixServerEncKey = []
    for x in range(len(mixServers)):
        mixServerEncKey.append(mixServers[x]["encryption_key"])
except IOError:
    sys.exit("sElect/_sElectConfigFiles_/ElectionManifest.json missing or corrupt")
    
#get ID after modifying Manifest
iDlength = 5
while(iDlength < 40):
    electionID = getID(iDlength)
    dstroot = os.path.join(rootDirProject, "elections/" + tStamp[0]+tStamp[1] + "_" + electionID + "_" + os.path.split(sElectDir)[1])

    try:
        copy(sElectDir, dstroot)
        link(dstroot)
        break
    except:
        iDlength = iDlength+1
        #sys.exit("ElectionID already exists.")

#add the password
jwrite(passList, electionID, password)

#modify Server ports
for x in range(len(mixServers)):     
    jwrite(dstroot + mixConf[x], "port", ports[x+2])
jwrite(dstroot + collectingConf, "port", ports[0])
jwrite(dstroot + bulletinConf, "port", ports[1])
#jwrite(dstroot + votingConf, "port", ports[5])        #not using the VotingBooth server, static path instead
jwrite(dstroot + votingConf, "authenticate", serverAddress[3])
jwrite(dstroot + collectingConf, "serverAdminPassword", password)

#change user randomness if not a mock election
if not mockElection:
    jwrite(dstroot + votingConf, "userChosenRandomness", random)

#create Ballots
if mockElection:
    os.mkdir(dstroot+"/CollectingServer/_data_")
    mixServerEncKeyString = str(mixServerEncKey).replace(" ", "").replace("u'", "").replace("'", "")
    ballotFile = dstroot+"/CollectingServer/_data_/accepted_ballots.log"
    for x in range(mockVoters):
        userEmail = "user"+str(x)+"@uni-trier.de"
        userRandom = ''.join([random.choice(string.ascii_letters + string.digits) for n in xrange(8)])
        userChoice = random.randint(0,(len(eleChoices)-1))
        ballots = subprocess.Popen(["node", "createBallots.js", ballotFile, userEmail, userRandom, str(userChoice), hashManifest(), mixServerEncKeyString], cwd=(rootDirProject+"/ElectionHandler/src"))
        ballots.wait()


#start all node servers
subprocess.call([dstroot + "/VotingBooth/refresh.sh"], cwd=(dstroot+"/VotingBooth"))
#vot = subprocess.Popen(["node", "server.js"], cwd=(dstroot+"/VotingBooth"))
if mockElection:
    col = subprocess.Popen(["node", "collectingServer.js", "--resume"], cwd=(dstroot+"/CollectingServer"))
else:
    col = subprocess.Popen(["node", "collectingServer.js"], cwd=(dstroot+"/CollectingServer"))
mix = []
for x in range(len(mixServers)):
    if x < 10:
        mix.append(subprocess.Popen(["node", "mixServer.js"], cwd=(dstroot+"/mix/0"+str(x))))
    else:
        mix.append(subprocess.Popen(["node", "mixServer.js"], cwd=(dstroot+"/mix/"+str(x))))
bb = subprocess.Popen(["node", "bb.js"], cwd=(dstroot+"/BulletinBoard"))
#newPIDs = [vot.pid, col.pid, m1.pid, m2.pid, m3.pid, bb.pid]
newPIDs = [col.pid, bb.pid]
for x in range(len(mixServers)):
    newPIDs.append(mix[x].pid)

#add PIDs to config
newElection = { "used-ports": ports, "processIDs": newPIDs, "electionID": electionID, "electionTitle": elecTitle, "electionDescription": elecDescr, "startTime": startingTime, "endTime": endingTime, "mixServers": len(mixServers), "ELS": ELS, "timeStamp": sName, "protect": not mockElection}
jAddList(electionConfig, "elections", newElection)
subprocess.call([sElectDir + "/../ElectionHandler/refreshConfig.sh"], cwd=(sElectDir+"/../ElectionHandler"))


#modify nginx File
if "localhost" not in serverAddress[0]:
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

    for x in range(len(mixServers)):
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
        if "end main server" in line:
            break
        counter = counter + 1
    bracketIt = nginxData[prevBracket:]
    del nginxData[prevBracket:]
    comments = ["    # Voting Booth " + electionID + " \n", "    location " + "/" + electionID + "/" + "vb" + "/ {\n", "        alias " + dstroot + "/VotingBooth/webapp/;\n", "        index votingBooth.html;\n","    }\n", "\n"]
    comments.extend(bracketIt)
    nginxData.extend(comments)
    nginxFile.seek(0)
    
    prevBracket = 0
    counter = 0
    for line in nginxData:
        if "end voting booth" in line:
            break
        counter = counter + 1
    bracketIt = nginxData[counter:]
    del nginxData[counter:]
    comments = ["  # Voting Booth " + electionID + " \n", "  server {\n", "    listen " + str(ELS) + ";\n", "\n", "    access_log " + nginxLog +"/access.log;\n", 
                "    error_log " + nginxLog +"/error.log;\n", "\n", "    server_name vb."+ serverAddress[3].split("://")[1] +";\n", "\n", "    proxy_set_header X-Forwarded-For $remote_addr;\n", "\n",
                "    location " + "/" + "vb" + "/ {\n", "        alias " + dstroot + "/VotingBooth/webapp/;\n", "        index votingBooth.html;\n","    }\n", "\n", "  }\n", "\n"]
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
    #for line in nginxData:
    #    if "}" in line:
    #        prevBracket = lastBracket
    #        lastBracket = counter
    #    counter = counter + 1
    for line in nginxData:
        if "}" in line:
            prevBracket = counter
        if "end main server" in line:
            break
        counter = counter + 1
    bracketIt = nginxData[prevBracket:]
    del nginxData[prevBracket:]
    '''
    comments = ["    # Voting Booth " + electionID + " \n", "    location " + "/" + electionID + "/votingBooth {\n", "        alias " + dstroot + "/VotingBooth/webapp/;\n", "        index votingBooth.html;\n","    }\n", "\n",     #old link
    comments = ["    # Voting Booth " + electionID + " \n", "    location " + "/" + "vb/" + str(ELS) + "/ {\n", "        alias " + dstroot + "/VotingBooth/webapp/;\n", "        index votingBooth.html;\n","    }\n", "\n",
                "    # Collecting server " + electionID + " \n", "    location " + "/" + electionID + "/collectingServer/ {\n", "        proxy_pass " + "http://localhost" + ":" + str(ports[0]) + "/;\n", "    }\n", "\n",
                "    # Bulletin board " + electionID + " \n", "    location " + "/" + electionID + "/bulletinBoard/ {\n", "        proxy_pass " + "http://localhost" + ":" + str(ports[1]) + "/;\n", "    }\n"]
    for x in range(len(mixServers)):
        if x < 10:
            comments.extend(["    # Mix server " + electionID + " #"+str(x)+"\n", "    location " + "/" + electionID + "/mix/0"+str(x)+"/ {\n", "        proxy_pass " + "http://localhost" + ":" + str(ports[x+2]) + "/;\n", "    }\n", "\n"])    
        else:
            comments.extend(["    # Mix server " + electionID + " #"+str(x)+"\n", "    location " + "/" + electionID + "/mix/"+str(x)+"/ {\n", "        proxy_pass " + "http://localhost" + ":" + str(ports[x+2]) + "/;\n", "    }\n", "\n"])
    '''
    comments = ["    # Voting Booth " + electionID + " \n", "    location " + "/" + electionID + "/" + "vb" + "/ {\n", "        alias " + dstroot + "/VotingBooth/webapp/;\n", "        index votingBooth.html;\n","    }\n", "\n"]
    comments.extend(["    # Collecting server " + electionID + " \n", "    location " + "/" + "cs/" + str(ELS) + "/ {\n", "        proxy_pass " + "http://localhost" + ":" + str(ports[0]) + "/;\n", "    }\n", "\n",
                    "    # Bulletin board " + electionID + " \n", "    location " + "/" + "bb/" + str(ELS) + "/ {\n", "        proxy_pass " + "http://localhost" + ":" + str(ports[1]) + "/;\n", "    }\n", "\n"])
    for x in range(len(mixServers)):
        comments.extend(["    # Mix server " + electionID + " #"+str(x)+"\n", "    location " + "/" + "m"+str(x)+"/" + str(ELS) + "/ {\n", "        proxy_pass " + "http://localhost" + ":" + str(ports[x+2]) + "/;\n", "    }\n", "\n"])

    comments.extend(bracketIt)
    nginxData.extend(comments)
    nginxFile.seek(0)
    
    prevBracket = 0
    counter = 0
    for line in nginxData:
        if "end voting booth" in line:
            break
        counter = counter + 1
    bracketIt = nginxData[counter:]
    del nginxData[counter:]
    comments = ["  # Voting Booth " + electionID + " \n", "  server {\n", "    listen " + str(ELS) + ";\n", "\n", "    access_log " + nginxLog +"/access.log;\n", 
                "    error_log " + nginxLog +"/error.log;\n", "\n", "    server_name "+ serverAddress[3].split("://")[1].split(":")[0] +";\n", "\n", "    proxy_set_header X-Forwarded-For $remote_addr;\n", "\n",
                "    location " + "/" + "vb" + "/ {\n", "        alias " + dstroot + "/VotingBooth/webapp/;\n", "        index votingBooth.html;\n","    }\n", "\n", "  }\n", "\n"]
    comments.extend(bracketIt)
    nginxData.extend(comments)
    nginxFile.seek(0)    
    
    nginxFile.writelines(nginxData)
    nginxFile.close()


#refresh nginx 
#TODO: fix /usr/sbin nginx issue
subprocess.call(["/usr/sbin/nginx", "-c", nginxConf,"-s", "reload"], stderr=open(os.devnull, 'w'))

