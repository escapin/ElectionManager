import json
import os
import collections
import sys
import subprocess
from psutil import process_iter
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
        print("no such file")
    json.dump(jsonData, jsonFile, indent = 4)
    jsonFile.truncate()
    jsonFile.close()

def getProcIDs(src, key, value):
    procID = []
    try:
        jsonFile = open(src, 'r+')
        jsonData = json.load(jsonFile, object_pairs_hook=collections.OrderedDict)
        pidList = jsonData[key]
        for x in range(len(pidList)):
            if value in pidList[x]:
                procID = pidList.pop(x)
                break
        jsonData[key] = pidList
        jsonFile.seek(0)
        json.dump(jsonData, jsonFile, indent = 4)
        jsonFile.truncate()
        jsonFile.close()
        return procID
    except IOError:
        sys.exit("cannot find process ID.")

electionConfig = "/ElectionConfigFile.json"
nginxConf = "/nginx_select.conf"

srcfile = os.path.realpath(__file__)
srcdir = os.path.split(os.path.split(srcfile)[0])

#get ElectionID
electionID = sys.argv[1]

#kill processes
nPIDs = getProcIDs(srcdir[0] + electionConfig, "processIDs", electionID)
nPIDs.remove(electionID)
for x in nPIDs:
    os.kill(x, SIGKILL)

#alternative using ports, no PID required, needs sudo
#procs = getProcIDs(srcdir[0] + electionConfig, "used-ports", electionID)
#procs.remove(electionID)
#for ports in procs:
#    for proc in process_iter():
#        for conns in proc.get_connections(kind='inet'):
#            if conns.laddr[1] == ports:
#                proc.send_signal(SIGKILL)
#                continue

#modify electionconfig File
jRemList(srcdir[0] + electionConfig, "electionIDs", electionID)
jRemList(srcdir[0] + electionConfig, "used-ports", electionID) #if using ports to kill process, already doing this with getProcIDs

#modify nginx File
nginxFile = open(srcdir[0] + nginxConf, 'r+')
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

os.system("nginx -s reload")
subprocess.call([srcdir[0] + "/ElectionHandler/refreshConfig2.sh"], cwd=(srcdir[0]+"/ElectionHandler"))