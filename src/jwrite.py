import json
import collections

#write a value to a key in a json file
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
   
#write a value in a list or multi-layered json objects
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

#add value to existing list
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
        jsonData = {key: [value]}
    json.dump(jsonData, jsonFile, indent = 4)
    jsonFile.truncate()
    jsonFile.close()

#add value to existing list and return the whole list
def jAddListAndReturn(src, key, value):
    try:
        jsonFile = open(src, 'r+')
        jsonData = json.load(jsonFile, object_pairs_hook=collections.OrderedDict)
        iDs = jsonData[key]
        iDs.append(value)
        jsonData[key] = iDs
        jsonFile.seek(0)
    except IOError:
        jsonFile = open(src, 'w')
        jsonData = {key: [value]}
    json.dump(jsonData, jsonFile, indent = 4)
    jsonFile.truncate()
    jsonFile.close()
    return jsonData

#remove value from list
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

#remove and election with specific ID
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
        for x in range(len(remPorts)):
            portsInUse.remove(remPorts[x])
        jsonFile.seek(0)
    except IOError:
        print("file missing")
    json.dump(jsonData, jsonFile, indent = 4)
    jsonFile.truncate()
    jsonFile.close()

#remove and election with specific ID and return remaining elections   
def jRemElecAndReturn(src, value):
    try:
        jsonFile = open(src, 'r+')
        jsonData = json.load(jsonFile, object_pairs_hook=collections.OrderedDict)
        elecs = jsonData["elections"]
        for x in range(len(elecs)):
            if elecs[x]["electionID"] == value:
                remElec = elecs.pop(x)
                break
        jsonData["elections"] = elecs
        jsonFile.seek(0)
    except IOError:
        print("file missing")
    json.dump(jsonData, jsonFile, indent = 4)
    jsonFile.truncate()
    jsonFile.close()
    return jsonData

def jRemHidden(src, src2, value):
    remPorts = []
    portsInUse = []
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
        jsonFile.seek(0)
    except IOError:
        print("file missing")
    json.dump(jsonData, jsonFile, indent = 4)
    jsonFile.truncate()
    jsonFile.close()
    try:
        jsonFile = open(src2, 'r+')
        jsonData = json.load(jsonFile, object_pairs_hook=collections.OrderedDict)
        portsInUse = jsonData["usedPorts"]
        for x in range(len(remPorts)):
            portsInUse.remove(remPorts[x])
        jsonFile.seek(0)
    except IOError:
        print("file missing")
    json.dump(jsonData, jsonFile, indent = 4)
    jsonFile.truncate()
    jsonFile.close()
    
