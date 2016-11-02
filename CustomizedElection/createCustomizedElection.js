var bcrypt = require("bcryptjs");
var fs = require('fs');
var child_process = require("child_process");
var spawn = child_process.spawn;

/**
The script can be called with 2 to 4 arguments

SYNOPSIS
	node createCustomizedElection.js -m PATH/TO/MANIFEST-p PASSWORD [-h [-r]]

OPTIONS:
	-m PATH/TO/MANIFEST: PATH/TO/MANIFEST will be used as the election manifest for the election
	-p PASSWORD: set password to close and remove the election to PASSWORD
	[-s SUBDOMAIN: the election will be displayed at SUBDOMAIN.serverdomain 
		(server domain is set in deployment/serverAddresses.json), no ELS will be used, optional argument]
	[-h: the election will be hidden from the ElectionManager, optional argument]
	[-r: user has to enter part of the verification code, userchosenRandomness set to true, optional argument]

**/

var parameters;
var hash;
var sdomain = "";
var rand = false;
var hide = false;
for(var i = 0; i < process.argv.length; i++){
	if(process.argv[i] === '-m'){
		var manifestPath = process.argv[i+1];
		var electionManifest = JSON.parse(fs.readFileSync(manifestPath));
		parameters = JSON.stringify(electionManifest);
		i++;
	}
	else if(process.argv[i] === '-p'){
		var salt = bcrypt.genSaltSync(10);
		hash = bcrypt.hashSync(process.argv[i+1], salt);
		i++;
	}
	else if(process.argv[i] === '-s'){
		sdomain = process.argv[i+1];
		i++;
	}
	else if(process.argv[i] === '-r'){
		rand = true;
	}
	else if(process.argv[i] === '-h'){
		hide = true;
	}
}

var additionalParam = {userChosenRandomness: rand, password: hash, subdomain: sdomain, hidden: hide}
additionalParam = JSON.stringify(additionalParam);

session = spawn('python', ['../src/createElection.py', "completeElection", parameters, additionalParam]);
session.stdout.on('data', function (data) {
	if(String(data).indexOf("OTP")>-1){
		var time =  new Date();
		console.log('[' + time +  '] Collecting Server STDOUT:\n\t' + data);
	}
	else if(String(data).indexOf("TLS")>-1){
		var time =  new Date();
		console.log('[' + time +  '] Mix Server STDOUT:\n\t' + data);
	}
	else if(String(data).indexOf("electionUrls.json:\n")>-1){
		eleInfo = String(data).split("electionUrls.json:\n")
		eleInfo = eleInfo[eleInfo.length-1];
		eleInfo = eleInfo.split("electionInfo.json:\n")[0];
		eleInfo = JSON.parse(eleInfo);
		console.log("\nFull Election ID: \n"+(eleInfo.ElectionIdentifier).toUpperCase());
		console.log("(use first "+(eleInfo.electionID).length+" characters ["+eleInfo.electionID+"] to remove the election)"+"\n")
		console.log("Voting Booth: \n"+eleInfo.VotingBooth+"\n");
		console.log("Collecting Server Admin: \n"+eleInfo.CollectingServer);
	}
});
session.stderr.on('data', function (data) {
	console.log("STDERR: "+data);
});
session.on('exit', function (code) {
	if(code !== 0){
		console.log('simple child process exited with code ' + code);
	}
});

