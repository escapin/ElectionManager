#!/bin/bash

echo
echo Remove all nginx processes \(requires *superuser* privileges\)
sudo killall nginx

# start nginx redirecting the traffic to the port 8433
./startNginx.sh
echo

# Run the Election Manager
cd ..
./run.sh
