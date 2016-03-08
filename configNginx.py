import os
import sys


def writeDirec(src, dest):
    nginxFile = open(src, 'r+')
    nginxData = nginxFile.readlines()
    counter = 0
    for line in nginxData:
        if "/PATH/TO/DIREC" in line:
            nginxData[counter] = line.replace("/PATH/TO/DIREC", dest)
        if "/PATH/TO/ELECTIONMANAGER" in line:
            nginxData[counter] = line.replace("/PATH/TO/ELECTIONMANAGER", srcdirec)
        counter = counter + 1
    nginxFile.seek(0)
    nginxFile.writelines(nginxData)
    nginxFile.close()




srcfile = os.path.realpath(__file__)
srcdirec = os.path.split(srcfile)[0]
nginxRootLog = srcdirec + "/nginx/root/log"
nginxLog = srcdirec + "/nginx/handler/log"
nginxRootFile = srcdirec + "/nginx/root/nginx.conf"
nginxFile = srcdirec + "/nginx/handler/nginx_select.conf"


writeDirec(nginxRootFile, nginxRootLog)
writeDirec(nginxFile, nginxLog)