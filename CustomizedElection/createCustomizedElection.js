var bcrypt = require("bcryptjs");
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

var hidden = process.argv[5]
if (hidden === 'hidden'){
	hidden = true;
}
else{
	hidden = false;
}

session = spawn('python', ['../src/createElection.py', hidden, parameters]);
