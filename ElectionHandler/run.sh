#!/bin/bash

./refreshConfig.sh

echo 
echo Starting the Election Handler...
node server.js
