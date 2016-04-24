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

    dstroot = os.path.join(rootDirProject, "elections/" + electionID + "_" + os.path.split(sElectDir)[1])

    #restart all node servers
    if os.path.exists(dstroot+"/CollectingServer/_data_/partialResult.msg"):
        col = subprocess.Popen(["node", "collectingServer.js", "--serveResult"], cwd=(dstroot+"/CollectingServer"))
    else:
        col = subprocess.Popen(["node", "collectingServer.js", "--resume"], cwd=(dstroot+"/CollectingServer"))
        
    if os.path.exists(dstroot+"/mix/00/_data_/ballots00_output.msg"):
        m1 = subprocess.Popen(["node", "mixServer.js", "--serveResult"], cwd=(dstroot+"/mix/00"))
    else:
        m1 = subprocess.Popen(["node", "mixServer.js"], cwd=(dstroot+"/mix/00"))
        
    if os.path.exists(dstroot+"/mix/01/_data_/ballots01_output.msg"):
        m2 = subprocess.Popen(["node", "mixServer.js", "--serveResult"], cwd=(dstroot+"/mix/01"))
    else:
        m2 = subprocess.Popen(["node", "mixServer.js"], cwd=(dstroot+"/mix/01"))
        
    if os.path.exists(dstroot+"/mix/02/_data_/ballots02_output.msg"):
        m3 = subprocess.Popen(["node", "mixServer.js", "--serveResult"], cwd=(dstroot+"/mix/02"))
    else:
        m3 = subprocess.Popen(["node", "mixServer.js"], cwd=(dstroot+"/mix/02"))
    if os.path.exists(dstroot+"/BulletinBoard/_data_/resultMIX2.msg"):
        bb = subprocess.Popen(["node", "bb.js", "--serveResult"], cwd=(dstroot+"/BulletinBoard"))
    else:
        bb = subprocess.Popen(["node", "bb.js"], cwd=(dstroot+"/BulletinBoard"))
    newPIDs = [col.pid, m1.pid, m2.pid, m3.pid, bb.pid]
        
    jwriteAdv(electionConfig, "elections", newPIDs, 0, "processIDs")

