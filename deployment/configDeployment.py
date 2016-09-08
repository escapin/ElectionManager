import os
import sys
import json
import collections

srcfile = os.path.realpath(__file__)
deployDir = os.path.split(srcfile)[0]
rootDirProject = os.path.split(deployDir)[0]

electionConfig = rootDirProject + "/_configFiles_/handlerConfigFile.json"

try:
    jsonFile = open(electionConfig, 'r+')
    jsonData = json.load(jsonFile, object_pairs_hook=collections.OrderedDict)
    jsonData["deployment"] = True
    jsonFile.seek(0)
    json.dump(jsonData, jsonFile, indent = 4)
    jsonFile.truncate()
    jsonFile.close()
except IOError:
    print('Handler configuration file missing or corrupted ("deployment" field not found)')
