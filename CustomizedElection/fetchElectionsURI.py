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
    
def printTotals(transferred, toBeTransferred):
    print "Transferred: {0} bytes\tOut of: {1} bytes".format(transferred, toBeTransferred)

electionURIserverPath = "/home/select/ElectionManager/_configFiles_/electionsURI.json"
localFilePath = "electionsURI.json"

try:
    ssh = paramiko.SSHClient()
except:
    paramiko.util.log_to_file("log/paramikoCreate.log")
    ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect("select.uni-trier.de", username="select", password="teA3votinG1dartS#randoM")
sftp = ssh.open_sftp()

print "Transferring the file with the elections' URIs to the current directory..."
sftp.get(electionURIserverPath, localFilePath, callback=printTotals);
#jsonFile = sftp.open(electionURIserverPath)
sftp.close()
with open(localFilePath) as jsonFile:
    jsonData = json.load(jsonFile, object_pairs_hook=collections.OrderedDict)

#jsonFile = sftp.open(electionURIserverPath)
#jsonData = json.load(jsonFile, object_pairs_hook=collections.OrderedDict)
#jsonFile.close()
#sftp.close()

print("Elections currently running:")

for electionID in jsonData.keys():
    votingBooth = jsonData[electionID][1]
    collectingAdmin = jsonData[electionID][2]
    bulletinBoard = jsonData[electionID][3]
    hidden = jsonData[electionID][4]
    #jwrite(localFilePath, electionID, [votingBooth, collectingAdmin, hidden])

    print("------------------------------\n")
    print("Election ID:")
    print(str(electionID)+" ("+hidden+")\n")
    print("Voting Booth:")  
    print(votingBooth+"\n")
    print("Collecting Server Admin:")
    print(collectingAdmin+"\n")
print("------------------------------")


