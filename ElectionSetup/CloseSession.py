import json
import os
import collections
import sys
import subprocess
from signal import SIGKILL

def jRemList(src, key, value):
    try:
        jsonFile = open(src, 'r+')
        jsonData = json.load(jsonFile, object_pairs_hook=collections.OrderedDict)
        iDs = jsonData[key]
        if type(iDs[0]) is list:
            for x in range(len(iDs)):
                if value in iDs[x]:
                    iDs.pop(x)
                    break
        else:
            if value in iDs:
                iDs.remove(value)
        jsonData[key] = iDs
        jsonFile.seek(0)
    except IOError:
        print("file missing")
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
                elecs.pop(x)
                break
        jsonData["elections"] = elecs
        jsonFile.seek(0)
    except IOError:
        print("file missing")
    json.dump(jsonData, jsonFile, indent = 4)
    jsonFile.truncate()
    jsonFile.close()

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
            elif(key == jsonData["masterpass"]):    #if no masterpass been chosen, this will throw an error
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
               
electionConfig = "/ElectionConfigFile.json"
nginxConf = "/nginx_select.conf"
passList = "/ElectionHandler/_data_/pass.json"

srcfile = os.path.realpath(__file__)
srcdir = os.path.split(os.path.split(srcfile)[0])[0]

#get ElectionID
electionID = sys.argv[1]
password = sys.argv[2]

matchPass(srcdir + passList, password, electionID)
#kill processes
nPIDs = getProcIDs(srcdir + electionConfig, "processIDs", electionID)
for x in nPIDs:
    try:
        os.kill(x, SIGKILL)
    except:
        pass
#alternative using ports, no PID required, needs sudo
#procs = getProcIDs(srcdir + electionConfig, "used-ports", electionID)
#procs.remove(electionID)
#for ports in procs:
#    for proc in process_iter():
#        for conns in proc.get_connections(kind='inet'):
#            if conns.laddr[1] == ports:
#                proc.send_signal(SIGKILL)
#                continue

#modify electionconfig File
jRemElec(srcdir + electionConfig, electionID)

#modify nginx File
nginxFile = open(srcdir + nginxConf, 'r+')
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
    for y in [2,3,4,5]:
        if "}" in nginxData[lineStart[x]+y]:
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
subprocess.call(["/usr/sbin/nginx", "-c", srcdir + nginxConf,"-s", "reload"], stderr=open(os.devnull, 'w'))
subprocess.call([srcdir + "/ElectionHandler/refreshConfig.sh"], cwd=(srcdir+"/ElectionHandler"))
removePass(srcdir + passList, electionID)