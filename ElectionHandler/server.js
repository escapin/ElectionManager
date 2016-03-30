var express = require("express");
var bodyParser = require("body-parser");
var bcrypt = require("bcryptjs");

var read = require('read');
var fs = require('fs');
var http = require('http');
//var https = require('https');
//var certificate = fs.readFileSync("../deployment/cert/select.chained.crt", 'utf8');
//var certificate_key = fs.readFileSync("../deployment/cert/select.key", 'utf8');
//var credentials = {key: certificate_key, cert: certificate};
var app = express();

var cors = require('cors');
var child_process = require("child_process");
var spawn = child_process.spawn;

var config = require('./src/config');

var port = config.port;
var path = 'webapp/';

app.use(cors());
app.use(bodyParser.urlencoded({
	extended : false
}));
//var httpsserver = https.createServer(credentials, app);

/**Resume previous elections **/
var oldSession = spawn('python', ['src/resumeElection.py']);
oldSession.stdout.on('data', function (data) {
	if(String(data).indexOf("OTP")>-1){
		console.log('stdout: ' + data);
	}
	else if(String(data).indexOf("TLS")>-1){
		console.log('mix stdout: ' + data);
	}
});
oldSession.stderr.on('data', function (data) {
    console.log('stderr: ' + data);
});

app.post('/election', function(req, res) {
	var task = req.body.task;
	var value = req.body.ID;
	var etitle = req.body.title;
	var edesc = req.body.description;
	var startingTime = req.body.startTime;
	var endingTime = req.body.endTime;
	var equestion = req.body.question;
	var echoices = req.body["choices[]"];
	var pass = req.body.password;
	var rand = req.body.random;
	var listVoters = req.body.publishVoters;

	var session = null;
	if (task === "complete"){
		var salt = bcrypt.genSaltSync(10);
		var hash = bcrypt.hashSync(pass, salt);
		
		session = spawn('python', ['src/createElection.py', startingTime, endingTime, etitle, edesc, equestion, echoices, hash, listVoters, rand]);
		
		session.stdout.on('data', function (data) {
			if(String(data).indexOf("OTP")>-1){
				console.log('stdout: ' + data);
			}
			else if(String(data).indexOf("TLS")>-1){
				console.log('mix stdout: ' + data);
			}
		});
		session.stderr.on('data', function (data) {
		    console.log('stderr: ' + data);
		    res.end(data);
		});

		session.on('exit', function (code) {
		    console.log('child process exited with code ' + code);
		    if(code === 0){
		    	res.end("created");
		    }
		    else{
		    	res.end("error code" + code)
		    }
		});
	}
	else if (task === "simple") {
		session = spawn('python', ['src/createElection.py']);
		
		session.stdout.on('data', function (data) {
			if(String(data).indexOf("OTP")>-1){
				console.log('stdout: ' + data);
			}
			else if(String(data).indexOf("TLS")>-1){
				console.log('mix stdout: ' + data);
			}
		});
		session.stderr.on('data', function (data) {
		    console.log('stderr: ' + data);
		    res.end(data);
		});

		session.on('exit', function (code) {
		    console.log('child process exited with code ' + code);
		    if(code === 0){
		    	res.end("created");
		    }
		    else{
		    	res.end("error code" + code)
		    }
		});
	}
	else if (task === "remove") {
		var passList = JSON.parse(fs.readFileSync("_data_/pwd.json"));
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
		
		session = spawn('python', ['src/removeElection.py', value, pass]);
		session.stdout.on('data', function (data) {
			console.log('stdout: ' + data);
		});
		session.stderr.on('data', function (data) {
		    console.log('stderr: ' + data);
		    res.end(data);
		});

		session.on('exit', function (code) {
		    console.log('child process exited with code ' + code);
		    if(code === 0){
		    	res.end("removed");
		    }
		    else{
		    	res.end("error code" + code)
		    }
		});
	}
});


// Test if the file with stored passwords exists and is a valid json file
try{
	var passFile = JSON.parse(fs.readFileSync("_data_/pwd.json"));
	start();
}
catch(e){	//if not, remove (if existing but broken json file) and ask for an admin password
	try{
		fs.unlinkSync('_data_/pwd.json');
	}
	catch(e){
	}
	console.log();
	console.log('Administrator password not set.');
	console.log('Setting up an administrator password to manage the elections...');
	read({ prompt: 'Enter a password:', silent: true }, function(er, password) {
	    verify(password);
	 })
}

// call when user couldn't confirm the password
function askPw(){
	read({ prompt: 'Passwords do not match, try again:', silent: true }, function(er, password) {
	    verify(password);
	  })
}
 
// confirm the entered password
function verify(passwd){
    read({ prompt: 'Retype the password:', silent: true }, function(er, password) {
        if (password !== passwd){
        	askPw();
        }
        else {
      	  var salt = bcrypt.genSaltSync();
      	  var adminpw = bcrypt.hashSync(password, salt);
      	  var obj = {adminpassword: adminpw}
      	  fs.writeFileSync('_data_/pwd.json', JSON.stringify(obj, null, 4), {spaces:4});
      	  console.log('Password stored');
      	  console.log();
      	  start();
        }
      })
}

// start the services
function start(){
	//var server = httpsserver.listen(port, function() {
	var server = app.listen(port, function() {
	    console.log('Serving %s on %s, port %d', path, server.address().address, server.address().port);
	});
}
