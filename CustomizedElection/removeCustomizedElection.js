var bcrypt = require("bcryptjs");
var read = require('read');
var fs = require('fs');
var child_process = require("child_process");
var spawn = child_process.spawn;

var passList = JSON.parse(fs.readFileSync("../ElectionHandler/_data_/pwd.json"));
var electionID = process.argv[2];
var pass = process.argv[3]

var hidden = process.argv[4]
if (hidden === 'hidden'){
	hidden = true;
}
else{
	hidden = false;
}


var match = passList[value];
var hash = match;
if(match !== ""){
	var salt = bcrypt.getSalt(match);
	hash = bcrypt.hashSync(pass, salt);
	if(match !== hash){
		match = passList["adminpassword"];
		salt = bcrypt.getSalt(match);
		hash = bcrypt.hashSync(pass, salt);
	}
}
pass = hash;

var session = spawn('python', ['removeElection.py', electionID, pass, hidden]);
session.on('exit', function (code) {
    console.log('remove child process exited with code ' + code);
    if(code === 0){
    	createdElections = createdElections - 1;
    	callback("removed");
    }
    else{
    	callback("An error occurred while removing an election: error code " + code + ". Try again!");
    }
});