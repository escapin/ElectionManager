#!/bin/bash
node ../tools/config2js.js config.json > webapp/config.js configRaw
node ../tools/config2js.js ElectionManifest.json > webapp/ElectionManifest.js electionManifestRaw
node ../tools/config2js.js ../CollectingServer/trustedDomains.json > ../CollectingServer/webapp/trustedDomains.js trustedDomainsRaw
node ../tools/config2js.js ../Authenticator/trustedDomains.json > ../Authenticator/webapp/trustedDomains.js trustedDomainsRaw
