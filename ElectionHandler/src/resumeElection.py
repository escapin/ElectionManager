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
    #vot = subprocess.Popen(["node", "server.js"], cwd=(dstroot+"/VotingBooth"))
    col = subprocess.Popen(["node", "collectingServer.js", "--resume"], cwd=(dstroot+"/CollectingServer"))
    m1 = subprocess.Popen(["node", "mixServer.js"], cwd=(dstroot+"/mix/00"))
    m2 = subprocess.Popen(["node", "mixServer.js"], cwd=(dstroot+"/mix/01"))
    m3 = subprocess.Popen(["node", "mixServer.js"], cwd=(dstroot+"/mix/02"))
    bb = subprocess.Popen(["node", "bb.js"], cwd=(dstroot+"/BulletinBoard"))
    #newPIDs = [vot.pid, col.pid, m1.pid, m2.pid, m3.pid, bb.pid]
    newPIDs = [col.pid, m1.pid, m2.pid, m3.pid, bb.pid]

    jwriteAdv(electionConfig, "elections", newPIDs, 0, "processIDs")

