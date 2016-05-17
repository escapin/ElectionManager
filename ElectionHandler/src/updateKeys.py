import os
import sys
import re
import subprocess

pattern="[0-9]+"
keyGeneratorMix_file="genKeys4mixServer.js"
keyGeneratorCS_file="genKeys4collectingServer.js"

# sElect (partial) files path
manifest = "_sElectConfigFiles_/ElectionManifest.json"
collectingConf = "CollectingServer/config.json"



# absolute paths
dstroot = sys.argv[1]
tools_path = dstroot + "/tools"


# to be run after the 'config_mix[0-9]+.json' files are in the current folder
def updateMixKeys():
    files = os.listdir(dstroot+"/mix")
    p=re.compile(pattern)
    configMix_files=filter(p.search, files);
    for file in configMix_files:
        #print "***\t" + file + "/config.json" + "\t***\n";
        subprocess.call(["node", os.path.join(tools_path,keyGeneratorMix_file),
                os.path.join(dstroot,manifest), os.path.join(dstroot,"mix/"+file+"/config.json")]);
        #print;
        
def updateCSKeys():
    #print "***\t" + collectingConf + "\t***\n";
    subprocess.call(["node", os.path.join(tools_path,keyGeneratorCS_file),
        os.path.join(dstroot,manifest), os.path.join(dstroot,collectingConf)]);
    #print;


updateMixKeys()
updateCSKeys()

