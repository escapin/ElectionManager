import os
import hashlib
import codecs
import json
import collections
import socket
import sys

'''
checks whether a port is free or in use
'''
def portOpen(port):
    host = "127.0.0.1"
    captive_dns_addr = ""
    host_addr = ""

    try:
        host_addr = socket.gethostbyname(host)

        if (captive_dns_addr == host_addr):
            return False

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        s.bind((host, port))
        s.close()
    except:
        return False

    return True

'''
returns an array of ports that are
not used by running elections
'''
def usePorts(src, num):
    newPorts = []
    try:
        jsonFile = open(src, 'r')
        jsonData = json.load(jsonFile, object_pairs_hook=collections.OrderedDict)
        rangePorts = jsonData["available-ports"]
        usingPorts = jsonData["usedPorts"]
        newPorts = []
        for openPort in range(rangePorts[0], rangePorts[1]):
            if openPort in usingPorts:
                continue
            if portOpen(openPort):
                newPorts.append(openPort)
            if len(newPorts) >= num:
                break
        if len(newPorts) < num:
            sys.exit("Maximum number of elections reached.")
        jsonFile.close()
    except IOError:
        sys.exit("handlerConfigFile.json missing or corrupt")
    return newPorts


'''
returns a string between "00" and "99" (included),
that is not already used by another election
'''
def getELS(src):
    usedELS = []
    newELS = -1
    try:
        jsonFile = open(src, 'r')
        jsonData = json.load(jsonFile, object_pairs_hook=collections.OrderedDict)
        maxElections = jsonData["maxNumberOfElections"]
        elections = jsonData["elections"]
        for x in range(len(elections)):
            usedELS.append(elections[x]["ELS"])
        if len(usedELS) >= maxElections:
            sys.exit("Maximum number of elections reached.")
        else:
            for x in range(maxElections):
                testELS = str(x)
                if len(testELS) < 2:
                    testELS = "0"+testELS
                if testELS in usedELS:
                    continue
                else:
                    newELS = testELS
                    break
        jsonFile.close()
    except IOError:
        sys.exit("handlerConfigFile.json missing or corrupt")
    newELS = str(newELS)
    if len(newELS) < 2:
        newELS = "0"+newELS
    return newELS

'''
returns an array containing the URI's of the
sElect servers, read from serverAddresses.json
(if deployment is set to false, uses localhost)
'''
def getsAddress(src, deployment, numMix, nginxPort, ELS, serverAddr):
    sAddress = []
    try:
        jsonFile = open(src, 'r')
        jsonData = json.load(jsonFile, object_pairs_hook=collections.OrderedDict)
        jsonAddress = {}
        if not deployment:
            for x in range(numMix):
                jsonAddress["mix"+str(x)] = "http://localhost:"+str(nginxPort)+"/m"+str(x)+"/"+str(ELS)+"/"
            jsonAddress["collectingserver"] = "http://localhost:"+str(nginxPort)+"/cs/"+str(ELS)+"/"
            jsonAddress["bulletinboard"] = "http://localhost:"+str(nginxPort)+"/bb/"+str(ELS)+"/"
            jsonAddress["votingbooth"] = "http://localhost:"+str(nginxPort)+"/"+str(ELS)+"/"
            jsonAddress["authenticator"] = "http://localhost:"+str(nginxPort)+"/auth/"+str(ELS)+"/"
            jsonAddress["authchannel"] = "http://localhost:"+str(nginxPort)+"/cs/"+str(ELS)+"/authChannel.html"
            jsonFile.close()
        else:
            jsonFile.close()
            jsonFile = open(serverAddr, 'r')
            jsonData = json.load(jsonFile, object_pairs_hook=collections.OrderedDict)
            addresses = jsonData["server-address"]
            jsonAddress["collectingserver"] = addresses["collectingserver"].replace(".", str(ELS)+".", 1)+"/"
            jsonAddress["bulletinboard"] = addresses["bulletinboard"].replace(".", str(ELS)+".", 1)+"/"
            jsonAddress["votingbooth"] = addresses["votingbooth"].replace(".", str(ELS)+".", 1)+"/"
            jsonAddress["authenticator"] = addresses["authenticator"].replace(".", str(ELS)+".", 1)+"/"
            jsonAddress["authchannel"] = addresses["authchannel"].replace(".", str(ELS)+".", 1)
            jsonAddress["tlspath"] = jsonData["tls_cert_path"]
            for x in range(numMix):
                jsonAddress["mix"+str(x)] = addresses["mix"+str(x)].replace(".", str(ELS)+".", 1)+"/"

                
        jsonFile.close()
    except IOError:
        sys.exit("serverAddresses.json missing or corrupt")
    return jsonAddress

'''
returns a part of the hashed ElectinoManifest
'''
def getID(src, num):
    manifestHash = hashManifest(src)
    elecID = manifestHash[:num]
    print(manifestHash)
    return elecID

'''
returns the hash of the ElectinoManifest
'''
def hashManifest(src):
    manifest_raw = codecs.open(src, 'r', encoding='utf8').read()
    manifest_raw = manifest_raw.replace("\n", '').replace("\r", '').strip()
    m = hashlib.sha256()
    m.update(manifest_raw)
    return m.hexdigest()

'''
creates symlinks for the servers
'''
def link(dstroot, manifest, votingManifest, authManifest):
    os.mkdir(dstroot+"/mix/00")
    os.mkdir(dstroot+"/mix/01")
    os.mkdir(dstroot+"/mix/02")
    os.symlink(dstroot+"/MixServer/run.sh", dstroot+"/mix/00/run.sh")
    os.symlink(dstroot+"/MixServer/cleanData.sh", dstroot+"/mix/00/cleanData.sh")
    os.symlink(dstroot+"/MixServer/mixServer.js", dstroot+"/mix/00/mixServer.js")
    os.symlink(dstroot+"/templates/config_mix00.json", dstroot+"/mix/00/config.json")
    
    os.symlink(dstroot+"/MixServer/run.sh", dstroot+"/mix/01/run.sh")
    os.symlink(dstroot+"/MixServer/cleanData.sh", dstroot+"/mix/01/cleanData.sh")
    os.symlink(dstroot+"/MixServer/mixServer.js", dstroot+"/mix/01/mixServer.js")
    os.symlink(dstroot+"/templates/config_mix01.json", dstroot+"/mix/01/config.json")
    
    os.symlink(dstroot+"/MixServer/run.sh", dstroot+"/mix/02/run.sh")
    os.symlink(dstroot+"/MixServer/cleanData.sh", dstroot+"/mix/02/cleanData.sh")
    os.symlink(dstroot+"/MixServer/mixServer.js", dstroot+"/mix/02/mixServer.js")
    os.symlink(dstroot+"/templates/config_mix02.json", dstroot+"/mix/02/config.json")
    
    os.remove(dstroot + votingManifest)
    os.symlink(dstroot + manifest, dstroot + votingManifest)
    os.remove(dstroot + authManifest)
    os.symlink(dstroot + manifest, dstroot + authManifest)
