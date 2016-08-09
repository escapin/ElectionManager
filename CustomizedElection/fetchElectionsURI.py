import os
import sys
import paramiko
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

electionURI = "/home/select/ElectionManager/_configFiles_/electionsURI.json"
localFile = "electionsURI.json"

#paramiko.util.log_to_file("log/paramikoRemove.log")
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect("select.uni-trier.de", username="select", password="teA3votinG1dartS#randoM")
sftp = ssh.open_sftp()
jsonFile = sftp.open(electionURI)
jsonData = json.load(jsonFile, object_pairs_hook=collections.OrderedDict)
jsonFile.close()
sftp.close()

for electionID in jsonData.keys():
    votingBooth = jsonData[electionID]["VotingBooth"]
    collectingAdmin = jsonData[electionID]["CollectingServer"]+"/admin/panel"
    hidden = jsonData[electionID]["hidden"]
    hidden = "hidden" if hidden == True else "visible"
    jwrite(localFile, electionID, [votingBooth, collectingAdmin, hidden])