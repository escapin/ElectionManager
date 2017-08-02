var bcrypt = require("bcryptjs");
var fs = require('fs');
var child_process = require("child_process");
var spawn = child_process.spawn;


/**
The script can be called with 2 to 4 arguments

SYNOPSIS
	node removeCustomizedElection.js -e <atLeast7charOfElectionID> -p <pwdInsertedWhenElectionCreated> [-h]

OPTIONS:
	-e <atLeast7charOfElectionID>
	    The electionID of the election to be removed (at least 7 digits of the electionID are required)
	-p <pwdInsertedWhenElectionCreated>
	    The password inserted at creation time, which can also be used to close the election before the pre-set closing time
	-h 
	    Optional argument: the election to be removed is among the elections not shown in the election handler web interface, if any
	    (such elections are referred to as 'hidden elections').
	    If this argument is not provided, in case the election is not among the election displayed in the election handler, 
	    it will anyway check whether such an election is among the 'hidden elections'.
**/


var passList = JSON.parse(fs.readFileSync("../ElectionHandler/_data_/pwd.json"));

var eleID;
var pass;
var hide = false;
for(var i = 0; i < process.argv.length; i++){
	if(process.argv[i] === '-e'){
		eleID = process.argv[i+1].slice(0,7).toLowerCase();
		i++;
	}
	else if(process.argv[i] === '-p'){
		pass = process.argv[i+1];
		i++;
	}
	else if(process.argv[i] === '-h'){
		hide = true;
	}
}

if(!passList.hasOwnProperty(eleID)){
	//means the election already has been removed by another request,
	//therefore browser should act as if it had been removed by 
	//its own request.
	console.log("Election does not exist or has already been removed.");
	process.exit();
}
var match = passList[eleID];
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

session = spawn('python', ['../src/removeElection.py', eleID, pass, hide]);
session.stderr.on('data', function (data) {
	console.log("STDERR: "+data);
});
