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

electionURIserverPath = "/home/select/ElectionManager/_configFiles_/electionsURI.json"
localFile = "electionsURI.json"

paramiko.util.log_to_file("log/paramikoFetchURI.log")
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect("select.uni-trier.de", username="select", password="teA3votinG1dartS#randoM")
sftp = ssh.open_sftp()
jsonFile = sftp.open(electionURIserverPath)
jsonData = json.load(jsonFile, object_pairs_hook=collections.OrderedDict)
jsonFile.close()
sftp.close()

print("Elections currently running:")

for electionID in jsonData.keys():
    votingBooth = jsonData[electionID]["VotingBooth"]
    collectingAdmin = jsonData[electionID]["CollectingServer"]
    hidden = jsonData[electionID]["hidden"]
    hidden = "hidden" if hidden == True else "visible"
    jwrite(localFile, electionID, [votingBooth, collectingAdmin, hidden])

    print("------------------------------\n")
    print("Election ID:")
    print(str(electionID)+" ("+hidden+")\n")
    print("Voting Booth:")
    print(votingBooth+"\n")
    print("Collecting Server Admin:")
    print(collectingAdmin+"\n")
print("------------------------------")


