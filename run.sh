#!/bin/bash

./startNginx.sh

echo Start the ElectionHandler
cd ElectionHandler/ ; ./run.sh
