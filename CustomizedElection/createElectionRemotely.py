import os
import sys
import paramiko

remotepath = "/home/select/ElectionManager/CustomizedElection/manifests/manifest.json"
try:
    localpath = sys.argv[1]
    password = sys.argv[2]
except:
    sys.exit("Script is called with arguments: \n python script.py Path/To/Manifest.json password [random [hidden]] \nwhereas random and hidden are optional boolean values (true/false)")
random = "true"
hidden = "true"

if(len(sys.argv)>3):
    random = sys.argv[3]
    if(len(sys.argv)>4):
        hidden = sys.argv[4]
        if(len(sys.argv)>5):
            remotepath = sys.argv[5]

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect("select.uni-trier.de", username="select", password="teA3votinG1dartS#randoM")
sftp = ssh.open_sftp()
sftp.put(localpath, remotepath)
sftp.close()
stdin, stdout, stderr = ssh.exec_command('cd /home/select/ElectionManager/CustomizedElection; node createCustomizedElection.js '+remotepath+' '+password+' '+random+' '+hidden)

terminate = False
for line in stdout:
    print (line.strip('\n'))
    if terminate:
        break
    if "Collecting Server Admin:" in line:
        terminate = True
for line in stderr:
    print (line.strip('\n'))
ssh.close()