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
    
def jRemElec(src, value):
    try:
        jsonFile = open(src, 'r+')
        jsonData = json.load(jsonFile, object_pairs_hook=collections.OrderedDict)
        elecs = jsonData["elections"]
        for x in range(len(elecs)):
            if elecs[x]["electionID"] == value:
                remElec = elecs.pop(x)
                remPorts = remElec["used-ports"]
                break
        jsonData["elections"] = elecs
        portsInUse = jsonData["usedPorts"]
        #don't remove the ports here, one is blocked while the others remain unchanged
        #for x in range(len(remPorts)):
        #    portsInUse.remove(remPorts[x])
        jsonFile.seek(0)
    except IOError:
        print("file missing")
    json.dump(jsonData, jsonFile, indent = 4)
    jsonFile.truncate()
    jsonFile.close()
    

# the root dir is three folders back
rootDirProject = os.path.realpath(__file__)
for i in range(3):
    rootDirProject=os.path.split(rootDirProject)[0]
sElectDir = rootDirProject + "/sElect"
nginxConf =  rootDirProject + "/nginx_config/nginx_select.conf"

electionConfig = rootDirProject + "/_handlerConfigFiles_/handlerConfigFile.json"

errPort = int(sys.argv[1])
newPort = int(sys.argv[2])
print("Attempting to replace port " + str(errPort) + " with " + str(newPort))
#get elections
jsonFile = open(electionConfig, 'r')
jsonData = json.load(jsonFile, object_pairs_hook=collections.OrderedDict)
elecs = jsonData["elections"]
jsonFile.close()


oldPort = -1
for x in range (len(elecs)):
    
    usedPorts = elecs[x]["used-ports"]
    if errPort not in usedPorts:
        continue
    
    election = elecs[x]
    
    #print("Port being searched: " + str(errPort) + " in: "+ str(usedPorts))
    electionID = elecs[x]["electionID"]
    startingTime = elecs[x]["startTime"]    
    tStamp = startingTime.replace("-", "").replace(":", "").split()
    dstroot = os.path.join(rootDirProject, "elections/" + tStamp[0]+tStamp[1] + "_" + electionID + "_" + os.path.split(sElectDir)[1])
    
    jRemElec(electionConfig, electionID)

    print("Reconfigurating ports for election " + str(electionID))
    serverByIndex = usedPorts.index(errPort)
    newPIDs = election["processIDs"]
    
    numMix = election["mixServers"]
    
    # sElect (partial) mixFiles path
    collectingConf = "/CollectingServer/config.json"
    bulletinConf = "/BulletinBoard/config.json"
    mixConf = []
    for x in range(numMix):
        if x < 10:
            mixConf.append("/templates/config_mix0" + str(x) + ".json")
        else:
            mixConf.append("/templates/config_mix" + str(x) + ".json")
            
    
    if serverByIndex == 0:
        jsonFile = open(dstroot + collectingConf, 'r')
        jsonData = json.load(jsonFile, object_pairs_hook=collections.OrderedDict)
        oldPort = jsonData["port"]
        jsonFile.close()
        if oldPort != errPort:
            sys.exit("why the **** are these ports different: " + str(oldPort) + " and " + str(errPort))
        jwrite(dstroot + collectingConf, "port", newPort)
        if os.path.exists(dstroot+"/CollectingServer/_data_/partialResult.msg"):
            proc = subprocess.Popen(["node", "collectingServer.js", "--serveResult"], cwd=(dstroot+"/CollectingServer"))
        else:
            proc = subprocess.Popen(["node", "collectingServer.js", "--resume"], cwd=(dstroot+"/CollectingServer"))
    elif serverByIndex == 1:
        jsonFile = open(dstroot + bulletinConf, 'r')
        jsonData = json.load(jsonFile, object_pairs_hook=collections.OrderedDict)
        oldPort = jsonData["port"]
        jsonFile.close()
        if oldPort != errPort:
            sys.exit("why the **** are these ports different: " + str(oldPort) + " and " + str(errPort))
        jwrite(dstroot + bulletinConf, "port", newPort)
        if os.path.exists(dstroot+"/BulletinBoard/_data_/resultMIX"+str(numMix)+".msg"):
            proc = subprocess.Popen(["node", "bb.js", "--serveResult"], cwd=(dstroot+"/BulletinBoard"))
        else:
            proc = subprocess.Popen(["node", "bb.js"], cwd=(dstroot+"/BulletinBoard"))
    elif serverByIndex > 1:
        mixServer = serverByIndex-2
        numMixStr = str(mixServer)
        jsonFile = open(dstroot + mixConf[mixServer], 'r')
        jsonData = json.load(jsonFile, object_pairs_hook=collections.OrderedDict)
        oldPort = jsonData["port"]
        jsonFile.close()
        if oldPort != errPort:
            sys.exit("why the **** are these ports different: " + str(oldPort) + " and " + str(errPort))
        jwrite(dstroot + mixConf[mixServer], "port", newPort)
        if mixServer < 10:
            numMixStr = "0"+str(mixServer)
        if os.path.exists(dstroot+"/mix/"+numMixStr+"/_data_/ballots"+numMixStr+"_output.msg"):
            proc = subprocess.Popen(["node", "mixServer.js", "--serveResult"], cwd=(dstroot+"/mix/"+numMixStr))
        else:
            proc = subprocess.Popen(["node", "mixServer.js"], cwd=(dstroot+"/mix/"+numMixStr))
    
    newPIDs[serverByIndex] = proc.pid
    usedPorts[serverByIndex] = newPort
    #print("Final ports: " + str(usedPorts))
    #print("Final PIDs: " + str(newPIDs))
    #add PIDs to config    
    
    election["processIDs"] = newPIDs
    election["used-ports"] = usedPorts

    jAddList(electionConfig, "elections", election)
    
    #modify nginx File
    nginxFile = open(nginxConf, 'r+')
    nginxData = nginxFile.readlines()
    counter = 0
    for line in nginxData:
        if "http://localhost:"+str(oldPort) in line:
            nginxData[counter] = line.replace("http://localhost:"+str(errPort), "http://localhost:"+str(newPort))
        counter = counter + 1
    nginxFile.seek(0)
    nginxFile.writelines(nginxData)
    nginxFile.truncate()
    nginxFile.close()
    
    #refresh nginx
    subprocess.call(["/usr/sbin/nginx", "-c", nginxConf,"-s", "reload"], stderr=open(os.devnull, 'w'))
    subprocess.call([rootDirProject + "/ElectionHandler/refreshConfig.sh"], cwd=(rootDirProject + "/ElectionHandler"))
    
    print("...done.")

if oldPort < 0:
    sys.exit("Port " + str(errPort) + " not found in handlerConfigFile.")


        