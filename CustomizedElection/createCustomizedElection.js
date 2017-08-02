var bcrypt = require("bcryptjs");
var fs = require('fs');
var child_process = require("child_process");
var spawn = child_process.spawn;

/**
The script can be called with 2 to 4 arguments

SYNOPSIS
	node createCustomizedElection.js -m <path/to/manifest.json> -p <pwdToCloseTheElection> [-v <path/to/confidentialVoters.json>] [-s <subdomain>] [-h] [-r]

OPTIONS:
	-m <path/to/manifest.json>
	            Provide the election manifest file
	-p <pwdToCloseTheElection>
	            Set password to close and remove the election to <pwdToCloseTheElection>
	-s <subdomain>
	            Optional argument: instead of using the Election Lookup String (ELS) in the URI, the election will be displayed 
		    at localhost:[port]/<subdomain> if the system run in localhost, <subdomain>.serverdomain otherwise.
	-v <path/to/confidentialVoters.json 
	            Optional argument: instead of making the list of voters' email addresses publicly available in the election manifest, 
		    provide them only to the collecting server.
	-h: 
	            Optional argument: the election will be hidden from the ElectionHandler web interface, if any
	-r: 
	            Optional argument: the user has to provide part of the verification code which will later be used to verify 
		    that her vote has been properly counted. This would weaker the assumption on the voting booth's honesty.

**/

var parameters;
var hash;
var sdomain = "";
var rand = false;
var hide = false;
var manifestParsed = false;
var passwordHashed = false;
var votersPath = "";
for(var i = 0; i < process.argv.length; i++){
	if(process.argv[i] === '-m'){
		var manifestPath = process.argv[i+1];
		try{
			var electionManifest = JSON.parse(fs.readFileSync(manifestPath));
		} catch (err) {
			if (err.code !== 'ENOENT') throw err;
			// handling file not found
			console.log("ERROR: file '" + manifestPath + "' not found!");
			process.exit(1);
		}
		parameters = JSON.stringify(electionManifest);
		manifestParsed=true;
		i++;
	}
	else if(process.argv[i] === '-p'){
		var salt = bcrypt.genSaltSync(10);
		hash = bcrypt.hashSync(process.argv[i+1], salt);
		passwordHashed=true;
		i++;
	}
	else if(process.argv[i] === '-s'){
		sdomain = process.argv[i+1];
		i++;
	}
	else if(process.argv[i] === '-v'){
		votersPath = process.argv[i+1];
		try{
			var confidentialVoters = JSON.parse(fs.readFileSync(votersPath));
			if(!confidentialVoters.hasOwnProperty("voters")){
				console.log("ERROR: file '" + votersPath + "' does not have property 'voters'!");
				process.exit(1);
			}
		} catch (err) {
			if (err.code !== 'ENOENT') throw err;
			// handling file not found
			console.log("ERROR: file '" + votersPath + "' not found!");
			process.exit(1);
		}
	}
	else if(process.argv[i] === '-r'){
		rand = true;
	}
	else if(process.argv[i] === '-h'){
		hide = true;
	}
}

if(!manifestParsed){
	console.log('ERROR: no manifest provided.');
	console.log('Usage:\n\t node createCustomizedElection -m PATH/TO/MANIFEST -p PASSWORD [-s SUBDOMAIN] [-v PATH/TO/VOTERS] [-h] [-r]');
	process.exit(1);
}
if(!passwordHashed){
	console.log('ERROR: no password to close/remove the election provided.');
	console.log('Usage:\n\t node createCustomizedElection -m PATH/TO/MANIFEST -p PASSWORD [-s SUBDOMAIN] [-v PATH/TO/VOTERS] [-h] [-r]');
	process.exit(1);
}

var additionalParam = {userChosenRandomness: rand, password: hash, subdomain: sdomain, hidden: hide, confidentialVotersFile: votersPath}
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

