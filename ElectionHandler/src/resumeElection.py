import os
import os.path
import json
import shutil
from shutil import ignore_patterns
import collections
import errno
import sys
import codecs
import subprocess


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
        
        
# the root dir is three folders back
rootDirProject = os.path.realpath(__file__)
for i in range(3):
    rootDirProject=os.path.split(rootDirProject)[0]
sElectDir = rootDirProject + "/sElect"

electionConfig = rootDirProject + "/_handlerConfigFiles_/handlerConfigFile.json"

#get elections
jsonFile = open(electionConfig, 'r')
jsonData = json.load(jsonFile, object_pairs_hook=collections.OrderedDict)
elecs = jsonData["elections"]
jsonFile.close()

#resume elections which haven't been removed and update PIDs
for x in range (len(elecs)):
    
    electionID = elecs[x]["electionID"]
    startingTime = elecs[x]["startTime"]    
    numMix = elecs[x]["mixServers"]
    tStamp = startingTime.replace("-", "").replace(":", "").split()
    
    dstroot = os.path.join(rootDirProject, "elections/" + tStamp[0]+tStamp[1] + "_" + electionID + "_" + os.path.split(sElectDir)[1])

    #restart all node servers
    if os.path.exists(dstroot+"/CollectingServer/_data_/partialResult.msg"):
        col = subprocess.Popen(["node", "collectingServer.js", "--serveResult"], cwd=(dstroot+"/CollectingServer"))
    else:
        col = subprocess.Popen(["node", "collectingServer.js", "--resume"], cwd=(dstroot+"/CollectingServer"))
    mix = []
    for z in range(numMix):
        numMixStr = str(z)
        if z < 10:
            numMixStr = "0"+str(z)
        if os.path.exists(dstroot+"/mix/"+numMixStr+"/_data_/ballots"+numMixStr+"_output.msg"):
            mix.append(subprocess.Popen(["node", "mixServer.js", "--serveResult"], cwd=(dstroot+"/mix/"+numMixStr)))
        else:
            mix.append(subprocess.Popen(["node", "mixServer.js"], cwd=(dstroot+"/mix/"+numMixStr)))
    if os.path.exists(dstroot+"/BulletinBoard/_data_/resultMIX"+str(numMix)+".msg"):
        bb = subprocess.Popen(["node", "bb.js", "--serveResult"], cwd=(dstroot+"/BulletinBoard"))
    else:
        bb = subprocess.Popen(["node", "bb.js"], cwd=(dstroot+"/BulletinBoard"))
    
    newPIDs = [col.pid, bb.pid]
    for z in range(numMix):
        newPIDs.append(mix[z].pid)
    print("this is "+str(x))
    jwriteAdv(electionConfig, "elections", newPIDs, x, "processIDs")

