#!/bin/bash
node ../sElect/tools/config2js.js config.json > webapp/js/config.js configRaw
node ../sElect/tools/config2js.js ../ElectionConfigFile.json > webapp/js/ElectionConfigFile.js electionConfigRaw
