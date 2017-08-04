#!/bin/bash

echo Refreshing the Election Handler\'s config files... 
./refreshConfig.sh

echo 
echo Starting the Election Handler...
node server.js
