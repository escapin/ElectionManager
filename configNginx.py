import os
import sys


def writeDirec(src, dest):
    nginxFile = open(src, 'r+')
    nginxData = nginxFile.readlines()
    for line in nginxData:
        if "/PATH/TO/DIREC" in line:
            nginxData[counter] = line.replace("/PATH/TO/DIREC", dest)
        if "/PATH/TO/ELECTIONMANAGER" in line:
            nginxData[counter] = line.replace("/PATH/TO/ELECTIONMANAGER", srcdirec)
    nginxFile.seek(0)
    nginxFile.writelines(nginxData)
    nginxFile.close()

def writePort(src, port):
    nginxFile = open(src, 'r+')
    nginxData = nginxFile.readlines()
    for line in nginxData:
        if "DEFAULT:PORT" in line:
            nginxData[counter] = line.replace("DEFAULT:PORT", dest)
    nginxFile.seek(0)
    nginxFile.writelines(nginxData)
    nginxFile.close()


srcfile = os.path.realpath(__file__)
srcdirec = os.path.split(srcfile)[0]
nginxRootLog = srcdirec + "/nginx_config/root/log"
nginxLog = srcdirec + "/nginx_config/handler/log"
nginxRootFile = srcdirec + "/nginx_config/root/nginx_root.conf"
nginxFile = srcdirec + "/nginx_config/handler/nginx_select.conf"

electionConfig = rootDirProject + "/_handlerConfigFiles_/handlerConfigFile.json"

nginxPort = 0
try:
    jsonFile = open(electionConfig, 'r')
    jsonData = json.load(jsonFile, object_pairs_hook=collections.OrderedDict)
    nginxPort = jsonData["nginx-port"]
except IOError:
    nginxPort = 8443

writeDirec(nginxRootFile, nginxRootLog)
writeDirec(nginxFile, nginxLog)

writePort(nginxRootFile, nginxPort)
writePort(nginxFile, nginxPort)

