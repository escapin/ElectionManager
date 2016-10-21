var bcrypt = require("bcryptjs");
var fs = require('fs');
var child_process = require("child_process");
var spawn = child_process.spawn;


var manifestPath = process.argv[2];
var electionManifest = JSON.parse(fs.readFileSync(manifestPath));
var parameters = JSON.stringify(electionManifest);

var salt = bcrypt.genSaltSync(10);
var hash = bcrypt.hashSync(process.argv[3], salt);

var hidden = process.argv[4]
if (hidden === 'hidden'){
	hidden = true;
}
else if(hidden === 'visible'){
	hidden = false;
}
else{
	console.log("wrong parameters: last argument should be 'hidden' or 'visible'");
	process.exit()
}
var rand = false;
if(process.argv.length > 5 && process.argv[5] === "random"){
	rand = true;
}
var additionalParam = {userChosenRandomness: rand, password: hash, hidden}
if(process.argv.length > 6){
	additionalParam.subdomain = process.argv[6];
}
var additionalParam = JSON.stringify(additionalParam);

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

