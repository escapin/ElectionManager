import os
import sys
import paramiko
import keyring
import getpass

remotepath = "/home/select/ElectionManager/CustomizedElection/manifests/manifest.json"
try:
    localpath = sys.argv[1]
    password = sys.argv[2]
except:
    sys.exit("Script is called with arguments: \n python script.py Path/To/Manifest.json password (hidden/visible) [random]")
hidden = "hidden"

if not os.path.isfile(localpath):
    sys.exit("File "+localpath+" does not exist.")

if(len(sys.argv)>3):
    hidden = sys.argv[3]
    if(hidden <> 'hidden' and hidden <> 'visible'):
        sys.exit("Script is called with arguments: \n python script.py Path/To/Manifest.json password (hidden/visible) [random]")
    if(len(sys.argv)>4):
        rand = sys.argv[4]
        if(len(sys.argv)>5):
            remotepath = sys.argv[5]


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
    # if the entry is not there we are going to set it up
    # to avoid it keeps on asking it
    try:
        keyring.set_password(hostname, user, pwd);
        print("Password stored in the OS keyring")
    except keyring.errors.PasswordSetError:
        print("Failed to store password in the OS keyring")

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
sftp.put(localpath, remotepath)
sftp.close()
stdin, stdout, stderr = ssh.exec_command('cd /home/select/ElectionManager/CustomizedElection; node createCustomizedElection.js '+remotepath+' '+password+' '+hidden+' '+rand)

terminate = False
for line in stdout:
    print (line.strip('\n'))
    if terminate:
        break
    if "Collecting Server Admin:" in line:
        terminate = True
ssh.close()