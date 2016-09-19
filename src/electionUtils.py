import os
import hashlib
import codecs
import json
import collections
import socket

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
            jsonAddress["authenticator"] = "http://localhost:"+str(nginxPort)+"/auth/"
            jsonAddress["csframe"] = "http://localhost:"+str(nginxPort)+"/csframe/"
            jsonFile.close()
        else:
            jsonFile.close()
            jsonFile = open(serverAddr, 'r')
            jsonData = json.load(jsonFile, object_pairs_hook=collections.OrderedDict)
            addresses = jsonData["server-address"]
            jsonAddress["collectingserver"] = addresses["collectingserver"]+"/"+str(ELS)+"/"
            jsonAddress["bulletinboard"] = addresses["bulletinboard"]+"/"+str(ELS)+"/"
            jsonAddress["votingbooth"] = addresses["votingbooth"]+"/"+str(ELS)+"/"
            jsonAddress["authenticator"] = addresses["authenticator"]
            jsonAddress["csframe"] = addresses["csframe"]
            for x in range(numMix):
                jsonAddress["mix"+str(x)] = addresses["mix"+str(x)]+"/"+str(ELS)+"/"
            
            onSSL = jsonData["ssl"]
            if onSSL:
                sslKey = jsonData["ssl-key"]
                sslCrt = jsonData["ssl-crt"]
                
        jsonFile.close()
    except IOError:
        sys.exit("serverAddresses.json missing or corrupt")
    return jsonAddress

def getID(src, num):
    manifestHash = hashManifest(src)
    elecID = manifestHash[:num]
    print(manifestHash)
    return elecID

def hashManifest(src):
    manifest_raw = codecs.open(src, 'r', encoding='utf8').read()
    manifest_raw = manifest_raw.replace("\n", '').replace("\r", '').strip()
    m = hashlib.sha256()
    m.update(manifest_raw)
    return m.hexdigest()

def link(dstroot, manifest, votingManifest):
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

