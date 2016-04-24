#!/bin/bash

# getting the file location of this file i.e., run.sh
SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ]; do # resolve $SOURCE until the file is no longer a symlink
  DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"
  SOURCE="$(readlink "$SOURCE")"
  [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE" 
# if $SOURCE was a relative symlink, we need to resolve it relative to the path where the symlink file was located
done
DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"



echo Starting the nginx services managing the sElect servers...
/usr/sbin/nginx -c $DIR/nginx_config/nginx_select.conf 2>/dev/null


echo Starting the ElectionHandler...
cd ElectionHandler/ ; ./run.sh
