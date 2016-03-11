#!/bin/bash

SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ]; do # resolve $SOURCE until the file is no longer a symlink
  DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"
  SOURCE="$(readlink "$SOURCE")"
  [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE" # if $SOURCE was a relative symlink, we need to resolve it relative to the path where the symlink file was located
done
DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"

echo Stopping nginx services managing the sElect servers...
/usr/sbin/nginx -c $DIR/nginx_config/handler/nginx_select.conf -s quit 2>/dev/null
echo Stopping nginx services redirecting ports...
sudo /usr/sbin/nginx -c $DIR/nginx_config/root/nginx_root.conf -s quit
