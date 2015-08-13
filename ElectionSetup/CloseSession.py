import json
import os
import collections
import sys
import subprocess

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

def remLines(src, lines):
    if lines[-1]-lines[0] == 26:
        del src[lines[0]:lines[-1]+3]
    else:
        for x in range(len(lines)):
            del src[lines[-x-1]:lines[-x-1]+3]

electionConfig = "/ElectionConfigFile.json"
nginxConf = "/nginx_select.conf"

srcfile = os.path.realpath(__file__)
srcdir = os.path.split(os.path.split(srcfile)[0])

#modify electionconfig File
electionID = sys.argv[1]
jRemList(srcdir[0] + electionConfig, "electionIDs", electionID)
jRemList(srcdir[0] + electionConfig, "used-ports", electionID)

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