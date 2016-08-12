import os
import sys
import paramiko
import json
import collections
import keyring
import getpass
from paramiko import ssh_exception

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
    print "{0} bytes /out of {1} bytes".format(transferred, toBeTransferred)

electionURIserverPath = "/home/select/ElectionManager/_configFiles_/electionsURI.json"
localFilePath = "electionsURI.json"
hostname = 'select.uni-trier.de'
user = 'select'

# try to retrieve the pwd from the keyring or prompt the user for it
pwd = keyring.get_password(hostname, user)
if (pwd is None):
    print 'Password for "' + user + "@" + hostname + '" not found in the OS keyring.'
    #print('Password for "' + user + "@" + hostname + '": ')
    #for line in sys.stdin:
    #    pwd = line
    pwd = getpass.getpass()
    
try:
    ssh = paramiko.SSHClient()
except:
    paramiko.util.log_to_file("log/paramikoCreate.log")
    ssh = paramiko.SSHClient()
    
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
try:
    ssh.connect(hostname, username=user, password=pwd)
except ssh_exception.AuthenticationException as e:
    print 'Authentication failed for "' + user + "@" + hostname + '": Probably wrong credentials!'
    sys.exit(1)
except:
    print 'Something went wrong while establishing the ssh connection:'
    print str(sys.exc_info())
    sys.exit(1)

sftp = ssh.open_sftp()

sys.stdout.write("Transferring the file with the elections' URIs to the current directory... ")
sftp.get(electionURIserverPath, localFilePath, callback=printTotals);
#jsonFile = sftp.open(electionURIserverPath)
sftp.close()
with open(localFilePath) as jsonFile:
    jsonData = json.load(jsonFile, object_pairs_hook=collections.OrderedDict)

#jsonFile = sftp.open(electionURIserverPath)
#jsonData = json.load(jsonFile, object_pairs_hook=collections.OrderedDict)
#jsonFile.close()
#sftp.close()

#print("Elections currently running:")
print 
for electionID in jsonData.keys():
    votingBooth = jsonData[electionID][1]
    collectingAdmin = jsonData[electionID][2]
    bulletinBoard = jsonData[electionID][3]
    hidden = jsonData[electionID][4]
    #jwrite(localFilePath, electionID, [votingBooth, collectingAdmin, hidden])

    print("------------------------------")
    print("Election ID: " + str(electionID)+" ("+hidden+")")
    print("Voting Booth:\t\t\t" + votingBooth+"")
    print("Collecting Server Admin:\t" + collectingAdmin+"")
print("------------------------------")


