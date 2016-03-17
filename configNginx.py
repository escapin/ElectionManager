import os
import sys
import json
import collections


def writeDirec(src, dest):
    nginxFile = open(src, 'r+')
    nginxData = nginxFile.readlines()
    counter = 0
    for line in nginxData:
        if "/PATH/TO/DIREC" in line:
            nginxData[counter] = line.replace("/PATH/TO/DIREC", dest)
        if "/PATH/TO/ELECTIONMANAGER" in line:
            nginxData[counter] = line.replace("/PATH/TO/ELECTIONMANAGER", rootDirProject)
        counter = counter + 1
    nginxFile.seek(0)
    nginxFile.writelines(nginxData)
    nginxFile.truncate()
    nginxFile.close()

def writePort(src, port):
    nginxFile = open(src, 'r+')
    nginxData = nginxFile.readlines()
    counter = 0
    for line in nginxData:
        if "DEFAULT:PORT" in line:
            nginxData[counter] = line.replace("DEFAULT:PORT", str(port))
        counter = counter + 1
    nginxFile.seek(0)
    nginxFile.writelines(nginxData)
    nginxFile.truncate()
    nginxFile.close()


srcfile = os.path.realpath(__file__)
rootDirProject = os.path.split(srcfile)[0]
nginxLog = rootDirProject + "/nginx_config/log"
nginxFile = rootDirProject + "/nginx_config/nginx_select.conf"

electionConfig = rootDirProject + "/_handlerConfigFiles_/handlerConfigFile.json"

nginxPort = -1
try:
    jsonFile = open(electionConfig, 'r')
    jsonData = json.load(jsonFile, object_pairs_hook=collections.OrderedDict)
    nginxPort = jsonData["nginx-port"]
except IOError:
    print 'Handler configuration file missing or corrupted ("nginx-port" field not found)'


writeDirec(nginxFile, nginxLog)
writePort(nginxFile, nginxPort)

