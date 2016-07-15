var bcrypt = require("bcryptjs");
var read = require('read');
var fs = require('fs');
var child_process = require("child_process");
var spawn = child_process.spawn;


var manifestPath = process.argv[2];
var salt = bcrypt.genSaltSync(10);
var hash = bcrypt.hashSync(process.argv[4], salt);

var electionManifest = JSON.parse(fs.readFileSync(manifestPath));
electionManifest.random = process.argv[3];
electionManifest.password = hash
var parameters = JSON.stringify(electionManifest);

var hidden = process.argv[4]
if (hidden === 'hidden'){
	hidden = true;
}
else{
	hidden = false;
}

session = spawn('python', ['createElection.py', hidden, parameters]);
session.stdout.on('data', function (data) {
	if(String(data).indexOf("OTP")>-1){
		var time =  new Date();
		console.log('[' + time +  '] Collecting Server STDOUT:\n\t' + data);
	}
	else if(String(data).indexOf("TLS")>-1){
		var time =  new Date();
		console.log('[' + time +  '] Mix Server STDOUT:\n\t' + data);
	}
});
session.stderr.on('data', function (data) {
	var time =  new Date();
	console.log('[' + time +  '] Collecting Server STDERR:\n\t' + data)
});
session.on('exit', function (code) {
    console.log('complete child process exited with code ' + code);
});
