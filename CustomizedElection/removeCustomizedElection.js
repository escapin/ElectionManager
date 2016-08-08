var bcrypt = require("bcryptjs");
var fs = require('fs');
var child_process = require("child_process");
var spawn = child_process.spawn;

var passList = JSON.parse(fs.readFileSync("../ElectionHandler/_data_/pwd.json"));
var value = process.argv[2];
var pass = process.argv[3]

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


var match = passList[value];
if(!passList.hasOwnProperty(value)){
	//means the election already has been removed by another request,
	//therefore browser should act as if it had been removed by 
	//its own request.
	console.log("Election does not exist or has already been removed.");
	process.exit();
}
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

session = spawn('python', ['../src/removeElection.py', value, pass, hidden]);
session.stderr.on('data', function (data) {
	console.log("STDERR: "+data);
});