import os
import sys
import paramiko

remotepath = "/home/select/ElectionManager/CustomizedElection/manifests/manifest.json"
try:
    localpath = sys.argv[1]
    password = sys.argv[2]
except:
    sys.exit("Script is called with arguments: \n python script.py Path/To/Manifest.json password [hidden/visible]")
hidden = "hidden"

if not os.path.isfile(localpath):
    sys.exit("File "+localpath+" does not exist.")

if(len(sys.argv)>3):
    hidden = sys.argv[3]
    if(hidden <> 'hidden' and hidden <> 'visible'):
        sys.exit("Script is called with arguments: \n python script.py Path/To/Manifest.json password [hidden/visible]")
    if(len(sys.argv)>4):
        remotepath = sys.argv[4]

paramiko.util.log_to_file("paramikoCreate.log")
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect("select.uni-trier.de", username="select", password="teA3votinG1dartS#randoM")
sftp = ssh.open_sftp()
sftp.put(localpath, remotepath)
sftp.close()
stdin, stdout, stderr = ssh.exec_command('cd /home/select/ElectionManager/CustomizedElection; node createCustomizedElection.js '+remotepath+' '+password+' '+hidden)

terminate = False
for line in stdout:
    print (line.strip('\n'))
    if terminate:
        break
    if "Collecting Server Admin:" in line:
        terminate = True
ssh.close()