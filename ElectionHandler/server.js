var express = require("express");
var bodyParser = require("body-parser");
var bcrypt = require("bcryptjs");

var read = require('read');
var fs = require('fs');
var http = require('http');
//var https = require('https');
//var certificate = fs.readFileSync("../sElect/_sElectConfigFiles_/select.chained.crt", 'utf8');
//var certificate_key = fs.readFileSync("../sElect/_sElectConfigFiles_/select.key", 'utf8');
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
//var basicAuth = require('basic-auth-connect');
//app.use('/election/*', basicAuth('admin', '888')); // authentication for the admin panel only

/**process.stdin.resume();
process.stdin.setEncoding('utf8');
var util = require('util');
var adminpw = "";
var verify = 0;
process.stdin.on('data', function (text) {
	if (text == ""){
		console.log('password cannot be empty, try again:');
	}
	else if (verify == 0){
		verify = 1;
		adminpw = text;
		console.log('reenter password:');
	}
	else if (text == adminpw){
		console.log('successfully entered password');
	}
	else {
		verify = 0;
		adminpw = "";
		console.log('passwords do not match, try again:');
	}
});**/

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
	
	var direc = "";
	
	if (rand === "true"){
		direc = "sElectRandom/"
	}
	
	var session = null;
	if (task === "complete"){
		var salt = bcrypt.genSaltSync(10);
		var hash = bcrypt.hashSync(pass, salt);
		
		session = spawn('python', ['../'+direc+'ElectionSetup/NewSession.py', startingTime, endingTime, etitle, edesc, equestion, echoices, hash, listVoters]);
		
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
	else if (task === "advanced") {
		session = spawn('python', ['../'+direc+'ElectionSetup/NewSession.py', startingTime, endingTime, etitle, edesc]);
		
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
		session = spawn('python', ['../'+direc+'ElectionSetup/NewSession.py']);
		
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
		var passList = JSON.parse(fs.readFileSync("_data_/pass.json"));
		var match = passList[value];
		var hash = match;
		if(match !== ""){
			var salt = bcrypt.getSalt(match);
			hash = bcrypt.hashSync(pass, salt);
			if(match !== hash){
				match = passList["masterpass"];
				salt = bcrypt.getSalt(match);
				hash = bcrypt.hashSync(pass, salt);
			}
		}
		pass = hash;
		
		session = spawn('python', ['../'+direc+'ElectionSetup/CloseSession.py', value, pass]);
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
	var passFile = JSON.parse(fs.readFileSync("_data_/pass.json"));
	start();
}
catch(e){	//if not, remove (if existing but broken json file) and ask for an admin password
	try{
		fs.unlinkSync('_data_/pass.json');
	}
	catch(e){
	}
	read({ prompt: 'Enter an administrator password to remove any election:', silent: true }, function(er, password) {
	    console.log('You entered: %s', password);
	    verify(password);
	 })
}

// call when user couldn't confirm the password
function askPw(){
	read({ prompt: 'passwords do not match, try again:', silent: true }, function(er, password) {
	    verify(password);
	  })
}
 
// confirm the entered password
function verify(passwd){
    read({ prompt: 'confirm password: ', silent: true }, function(er, password) {
        if (password !== passwd){
        	askPw();
        }
        else {
      	  console.log('successfully entered password');
      	  var salt = bcrypt.genSaltSync();
      	  var adminpw = bcrypt.hashSync(password, salt);
      	  var obj = {adminpassword: adminpw}
      	  fs.writeFileSync('_data_/pass.json', JSON.stringify(obj, null, 4), {spaces:4});
      	  start();
        }
      })
}

// start the services
function start(){
	var server = app.listen(port, function() {
	    console.log('Serving %s on %s, port %d', path, server.address().address, server.address().port);
	});
}
