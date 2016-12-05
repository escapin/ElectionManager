import json
import os
import collections
import sys
import subprocess
from signal import SIGKILL
import jwrite

def getProcIDs(src, key, value):
    procID = []
    try:
        jsonFile = open(src, 'r')
        jsonData = json.load(jsonFile, object_pairs_hook=collections.OrderedDict)
        elecs = jsonData["elections"]
        for x in range(len(elecs)):
            if elecs[x]["electionID"] == value:
                procID = elecs[x][key]
                break
        jsonFile.close()
        return procID
    except IOError:
        sys.exit("cannot find process ID.")

def matchPass(src, key, value):
    try:
        jsonFile = open(src, 'r')
        jsonData = json.load(jsonFile, object_pairs_hook=collections.OrderedDict)
        match = jsonData[value]
        try:
            if(key == match):
                return True;
            elif(key == jsonData["adminpassword"]):    #if no masterpass been chosen, this will throw an error
                return True;
            else:
                sys.exit("wrong password")
        except:
            sys.exit("wrong password")
    except IOError:
        sys.exit("file missing")
        
def removePass(src, value):
    try:
        jsonFile = open(src, 'r+')
        jsonData = json.load(jsonFile, object_pairs_hook=collections.OrderedDict)
        del jsonData[value]
        jsonFile.seek(0)
        json.dump(jsonData, jsonFile, indent = 4)
        jsonFile.truncate()
        jsonFile.close()
    except IOError:
        sys.exit("file missing")

def setConfigFiles():
    global rootDirProject
    global electionConfig
    global electionInfo
    global electionInfoHidden
    global electionURI
    global nginxConf
    global passList
    
    # the root dir is three folders back
    rootDirProject = os.path.realpath(__file__)
    for i in range(2):
        rootDirProject=os.path.split(rootDirProject)[0]
                 
    electionConfig = rootDirProject + "/_configFiles_/handlerConfigFile.json"
    electionInfo = rootDirProject + "/_configFiles_/electionInfo.json"
    electionInfoHidden = rootDirProject + "/_configFiles_/electionHiddenInfo.json"
    electionURI = rootDirProject + "/_configFiles_/electionsURI.json"
    nginxConf = rootDirProject + "/nginx_config/nginx_select.conf"
    passList = rootDirProject + "/ElectionHandler/_data_/pwd.json"

def getInput():
    global electionID
    global password
    global hidden
    
    #get ElectionID
    electionID = sys.argv[1]
    password = sys.argv[2]
    try:
        hidden = True if sys.argv[3] == "true" else False
    except:
        hidden = False

def shutdownServers():
    #kill processes
    config = electionInfoHidden if hidden else electionConfig
    nPIDs = getProcIDs(config, "processIDs", electionID)
    for x in nPIDs:
        try:
            os.kill(nPIDs[x], SIGKILL)
        except:
            pass

def writeToHandlerConfig():
    global eleInfo
    global hidden

    #modify electionconfig File
    try:
        jsonFile = open(electionConfig, 'r+')
        jsonData = json.load(jsonFile, object_pairs_hook=collections.OrderedDict)
        jsonData["electionsCreated"] = jsonData["electionsCreated"]-1
        jsonFile.seek(0)
        json.dump(jsonData, jsonFile, indent = 4)
        jsonFile.truncate()
        jsonFile.close()
    except IOError:
        sys.exit("handlerConfigFile.json missing or corrupt")
    try:
        jsonFile = open(electionURI, 'r+')
        jsonData = json.load(jsonFile, object_pairs_hook=collections.OrderedDict)
        del jsonData[electionID]
        jsonFile.seek(0)
        json.dump(jsonData, jsonFile, indent = 4)
        jsonFile.truncate()
        jsonFile.close()
    except IOError:
        sys.exit("electionsURI.json missing or corrupt")
    except KeyError:
        pass
	#print(electionID + "not found i electionsURI.json, continue without removing.")
    if not hidden:
        print("did this")
        try:
            jwrite.jRemElec(electionConfig, electionID)
            eleInfo = jwrite.jRemElecAndReturn(electionInfo, electionID)
        except:
            jwrite.jRemHidden(electionInfoHidden, electionConfig, electionID)
            hidden = True
    else:
        jwrite.jRemHidden(electionInfoHidden, electionConfig, electionID)
    subprocess.call([rootDirProject + "/ElectionHandler/refreshConfig.sh"], cwd=(rootDirProject + "/ElectionHandler"))
    

def writeToNginxConfig():
    #modify nginx File
    nginxFile = open(nginxConf, 'r+')
    nginxData = nginxFile.readlines()
    lineStart = []
    votingBooth = 0
    counter = 0
    for line in nginxData:
        if " "+electionID in line:
            lineStart.append(counter)
        counter = counter + 1
    lineEnd = []
    for x in range(len(lineStart)):
        brackets = -1
        for y in range(len(nginxData)-lineStart[x]):
            if "{" in nginxData[lineStart[x]+y]:
                if brackets == -1:
                    brackets = 0
                brackets = brackets + 1
            if "}" in nginxData[lineStart[x]+y]:
                brackets = brackets - 1
            if brackets == 0:
                lineEnd.append(lineStart[x]+y)
                break       
    for x in range(len(lineStart)):
        del nginxData[lineStart[-x-1]:lineEnd[-x-1]+1]
        if nginxData[lineStart[-x-1]] == "\n":
            del nginxData[lineStart[-x-1]]
    nginxFile.seek(0)
    nginxFile.writelines(nginxData)
    nginxFile.truncate()
    nginxFile.close()
    
    #refresh nginx
    subprocess.call(["/usr/sbin/nginx", "-c", nginxConf,"-s", "reload"], stderr=open(os.devnull, 'w'))


#MAIN THREAD STARTS HERE

setConfigFiles()
getInput()
matchPass(passList, password, electionID)
shutdownServers()
writeToHandlerConfig()
writeToNginxConfig()
removePass(passList, electionID)

#prints election details to server.js
if not hidden:
    print("electionInfo.json:\n"+json.dumps(eleInfo))


