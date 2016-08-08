import os
import sys
import paramiko

try:
    electionID = sys.argv[1]
    password = sys.argv[2]
except:
    sys.exit("Script is called with arguments: \n python script.py password [hidden/visible]")

hidden = "hidden"

if(len(sys.argv)>3):
    hidden = sys.argv[3]
    if(hidden <> 'hidden' and hidden <> 'visible'):
        sys.exit("Script is called with arguments: \n python script.py password [hidden/visible]")

paramiko.util.log_to_file("paramikoRemove.log")
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect("select.uni-trier.de", username="select", password="teA3votinG1dartS#randoM")

stdin, stdout, stderr = ssh.exec_command('cd /home/select/ElectionManager/CustomizedElection; node removeCustomizedElection.js '+electionID+' '+password+' '+hidden)
for line in stdout:
    print (line.strip('\n'))
for line in stderr:
    print (line.strip('\n'))
ssh.close()