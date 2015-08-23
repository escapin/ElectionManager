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
import time
from signal import SIGKILL

def copy(src, dest):
    try:
        shutil.copytree(src, dest, symlinks=True, ignore=ignore_patterns("*.py", "00", "01", "02", "ElectionHandler"))
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
    utcTime = utcTime + datetime.timedelta(hours=1)
    return utcTime

def addSec(tm, secs):
    fulldate = tm + datetime.timedelta(seconds=secs)
    return fulldate

def createElec():
    jsonFile = open(srcdir[0] + electionConfig, 'w')
    jsonData = {"electionIDs": [], "maxElections": (3500-3300)//6, "available-ports": [3300, 3500], "used-ports": []}
    json.dump(jsonData, jsonFile, indent = 4)
    jsonFile.close()

def usePorts():
    newPorts = []
    try:
        jsonFile = open(srcdir[0] + electionConfig, 'r')
        jsonData = json.load(jsonFile, object_pairs_hook=collections.OrderedDict)
        rangePorts = jsonData["available-ports"]
        listPorts = jsonData["used-ports"]
        usingPorts = []
        for x in range(len(listPorts)):
            usingPorts.extend(listPorts[x])        
        for openPort in range(rangePorts[0], rangePorts[1]):
            if openPort in usingPorts:
                continue
            newPorts.append(openPort)
            if len(newPorts) >= 6:
                break
        if len(newPorts) < 6:
            sys.exit("Not enough ports available.")
        listPorts.append(newPorts)
        jsonData["used-ports"] = listPorts
        jsonFile.close()
    except IOError:
        createElec()
        newPorts = [3300, 3301, 3302, 3111, 3299, 3333]
    return newPorts

def getID():
    manifestHash = hashManifest()
    elecID = manifestHash[:5]
    print(manifestHash)
    return elecID

def hashManifest():
    manifest_raw = codecs.open(srcdir[0] + manifest, 'r', encoding='utf8').read()
    manifest_raw = manifest_raw.replace("\n", '').replace("\r", '').strip()
    m = hashlib.sha1()
    m.update(manifest_raw)
    return m.hexdigest()

electionConfig = "/ElectionConfigFile.json"
manifest = "/_sElectConfigFiles_/ElectionManifest.json"
collectingConf = "/CollectingServer/config.json"
bulletinConf = "/BulletinBoard/config.json"
votingManifest = "/VotingBooth/ElectionManifest.json"     
votingConf = "/VotingBooth/config.json"  
mix00Conf = "/templates/config_mix00.json"
mix01Conf = "/templates/config_mix01.json"
mix02Conf = "/templates/config_mix02.json"
nginxConf = "/nginx_select.conf"

srcfile = os.path.realpath(__file__)
srcdir = os.path.split(os.path.split(srcfile)[0])

votingTime = 300    #sec
ports = usePorts()

#modify ElectionManifest
currentTime = getTime().strftime("%Y.%m.%d %H:%M GMT+0100")
endingTime = addSec(getTime(), votingTime).strftime("%Y.%m.%d %H:%M GMT+0100")
jwrite(srcdir[0] + manifest, "startTime", currentTime)
jwrite(srcdir[0] + manifest, "endTime", endingTime)
jwriteAdv(srcdir[0] + manifest, "collectingServer", "http://localhost:" + str(ports[4]), "URI")
jwriteAdv(srcdir[0] + manifest, "bulletinBoards", "http://localhost:" + str(ports[3]), 0, "URI")
jwriteAdv(srcdir[0] + manifest, "mixServers", "http://localhost:" + str(ports[0]), 0, "URI")
jwriteAdv(srcdir[0] + manifest, "mixServers", "http://localhost:" + str(ports[1]), 1, "URI")
jwriteAdv(srcdir[0] + manifest, "mixServers", "http://localhost:" + str(ports[2]), 2, "URI")

#get ID after modifying Manifest
electionID = getID()
dstroot = os.path.join(os.path.split(srcdir[0])[0], electionID + "_" + os.path.split(srcdir[0])[1])
jAddList(srcdir[0] + electionConfig, "electionIDs", electionID)
ports.insert(0, electionID)
jAddList(srcdir[0] + electionConfig, "used-ports", ports)

#modify Server ports
jwrite(srcdir[0] + mix00Conf, "port", ports[1])
jwrite(srcdir[0] + mix01Conf, "port", ports[2])
jwrite(srcdir[0] + mix02Conf, "port", ports[3])
jwrite(srcdir[0] + bulletinConf, "port", ports[4])
jwrite(srcdir[0] + collectingConf, "port", ports[5])
jwrite(srcdir[0] + votingConf, "port", ports[6])

#modify nginx File
nginxFile = open(srcdir[0] + nginxConf, 'r+')
nginxData = nginxFile.readlines()
lastBracket = 0
counter = 0
for line in nginxData:
    if line == "}\n":
        lastBracket = counter
    counter = counter + 1
bracketIt = nginxData[lastBracket:]
del nginxData[lastBracket:]
comments = ["\n    # Voting Booth " + electionID + " \n", "    location " + "/" + electionID + "/votingBooth {\n", "        alias " + dstroot + "/VotingBooth/webapp/;\n", "        index votingBooth.html;\n","    }\n", "\n",
            "    # Collecting server " + electionID + " \n", "    location " + "/" + electionID + "/collectingServer/ {\n", "        proxy_pass http://localhost:" + str(ports[5]) + "/;\n", "    }\n", "\n",
            "    # Mix server " + electionID + " #1\n", "    location " + "/" + electionID + "/mix/00/ {\n", "        proxy_pass http://localhost:" + str(ports[1]) + "/;\n", "    }\n", "\n",
            "    # Mix server " + electionID + " #2\n", "    location " + "/" + electionID + "/mix/01/ {\n", "        proxy_pass http://localhost:" + str(ports[2]) + "/;\n", "    }\n", "\n",
            "    # Mix server " + electionID + " #3\n", "    location " + "/" + electionID + "/mix/03/ {\n", "        proxy_pass http://localhost:" + str(ports[3]) + "/;\n", "    }\n", "\n",
            "    # Bulletin board " + electionID + " \n", "    location " + "/" + electionID + "/bulletinBoard/ {\n", "        proxy_pass http://localhost:" + str(ports[4]) + "/;\n", "    }\n"]
comments.extend(bracketIt)
nginxData.extend(comments)
nginxFile.seek(0)
nginxFile.writelines(nginxData)
nginxFile.close()


copy(srcdir[0], dstroot)
link(dstroot)

#get all PIDs with node
nodes = subprocess.check_output(["pgrep", "node"])
oldPIDs = nodes.split()

os.system("nginx -s reload")
subprocess.call([srcdir[0] + "/ElectionHandler/refreshConfig2.sh"], cwd=(srcdir[0]+"/ElectionHandler"))
subprocess.call([dstroot + "/" + srcdir[1] + "/start.sh"], cwd=dstroot)
#alternative maybe
#vot = subprocess.Popen(["node", "server.js"], cwd=(dstroot+"/VotingBooth"))
#col = subprocess.Popen(["node", "collectingServer.js"], cwd=(dstroot+"/CollectingServer"))
#m1 = subprocess.Popen(["node", "mixServer.js"], cwd=(dstroot+"/mix/00"))
#m2 = subprocess.Popen(["node", "mixServer.js"], cwd=(dstroot+"/mix/01"))
#m3 = subprocess.Popen(["node", "mixServer.js"], cwd=(dstroot+"/mix/02"))
#bb = subprocess.Popen(["node", "bb.js"], cwd=(dstroot+"/BulletinBoard"))
#procs = [electionID, vot.pid, col.pid, m1.pid, m2.pid, m3.pid, bb.pid]
#jAddList(srcdir[0] + electionConfig, "processIDs", procs)

time.sleep(2)
#get all PIDs with Node
nodes = subprocess.check_output(["pgrep", "node"])
allPIDs = nodes.split()
newPIDs = []
for x in allPIDs:
    if x not in oldPIDs:
        newPIDs.append(x)
        
newPIDs = [int(i) for i in newPIDs]
print(newPIDs)

timeout = 10
while len(newPIDs) < 6 and timeout > 0:
    nodes = subprocess.check_output(["pgrep", "node"])
    allPIDs = nodes.split()
    newPIDs = []
    for x in allPIDs:
        if x not in oldPIDs:
            newPIDs.append(x)
    timeout = timeout - 1
    time.sleep(1)

#add PIDs to config
newPIDs = [int(i) for i in newPIDs]
newPIDs.insert(0, electionID)
jAddList(srcdir[0] + electionConfig, "processIDs", newPIDs)

#should be 6 new processes, otherwise close and ERROR, this should not happen
if len(newPIDs) != 6:
    subprocess.call([srcdir[0] + "/ElectionSetup/CloseSession.py", electionID], cwd=(srcdir[0]+"/ElectionSetup"))
    sys.exit("multiple calls, try again")
