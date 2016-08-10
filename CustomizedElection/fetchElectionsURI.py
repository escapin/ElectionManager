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
    print "Transferred: {0}\tOut of: {1}".format(transferred, toBeTransferred)

electionURIserverPath = "/home/select/ElectionManager/_configFiles_/electionsURI.json"
localFilePath = "./electionsURI.json"

paramiko.util.log_to_file("log/paramikoFetchURI.log")
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


print("Elections currently running:")

for electionID in jsonData.keys():
    votingBooth = jsonData[electionID]["VotingBooth"]
    collectingServerAdmin = jsonData[electionID]["CollectingServer"]
    hidden = jsonData[electionID]["hidden"]
    hidden = "hidden" if hidden == True else "visible"
    jwrite(localFilePath, electionID, [votingBooth, collectingServerAdmin, hidden])

    print("------------------------------\n")
    print("Election ID:")
    print(str(electionID)+" ("+hidden+")\n")
    print("Voting Booth:")
    print(votingBooth+"\n")
    print("Collecting Server Admin:")
    print(collectingServerAdmin+"\n")
print("------------------------------")


