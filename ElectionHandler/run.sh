node ../sElect/tools/config2js.js config.json > webapp/js/config.js configRaw
node ../sElect/tools/config2js.js ../_configFiles_/handlerConfigFile.json > webapp/js/ElectionConfigFile.js electionConfigRaw
node ../sElect/tools/config2js.js ../_configFiles_/serverAddresses.json > webapp/js/serverAddresses.js sAddressesRaw

echo Starting the Election Handler...
node server.js
