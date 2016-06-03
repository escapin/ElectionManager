node ../sElect/tools/config2js.js config.json > webapp/js/config.js configRaw
node ../sElect/tools/config2js.js ../_handlerConfigFiles_/handlerConfigFile.json > webapp/js/ElectionConfigFile.js electionConfigRaw
node ../sElect/tools/config2js.js ../deployment/serverAddresses.json > webapp/js/serverAddresses.js sAddressesRaw 2>/dev/null
node server.js 2>&1 | tee -a terminal.log
