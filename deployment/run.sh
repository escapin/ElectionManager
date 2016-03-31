#!/bin/bash

echo \* Removing all nginx processes...
sudo killall nginx
echo done!

# start nginx redirecting the traffic to the port 8433
./startNginx.sh

# Run the Election Manager
cd ..
./run.sh
