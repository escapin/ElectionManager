var express = require("express");
var bodyParser = require("body-parser");
var bcrypt = require("bcryptjs");
var read = require('read');
var fs = require('fs');
var http = require('http');
var mkdirp = require('mkdirp');
var net = require('net');

//var https = require('https');
//var certificate = fs.readFileSync("../deployment/cert/select.chained.crt", 'utf8');
//var certificate_key = fs.readFileSync("../deployment/cert/select.key", 'utf8');
//var credentials = {key: certificate_key, cert: certificate};
var cors = require('cors');
var child_process = require("child_process");
var config = require('./src/config');
var port = config.port;
var app = express();
app.use(cors());
app.use(bodyParser.urlencoded({ extended : false }));
var spawn = child_process.spawn;
var path = 'webapp/';
//var httpsserver = https.createServer(credentials, app);

//create '_data_' dir, if it doesn't exist
DATA_DIR = './_data_';
mkdirp.sync(DATA_DIR);

var numMix = 0;

/**Resume previous elections **/
var oldSession = spawn('python', ['src/resumeElection.py']);
oldSession.stdout.on('data', function (data) {
	if(String(data).indexOf("OTP")>-1){
		console.log('resume stdout: ' + data);
	}
	else if(String(data).indexOf("TLS")>-1){
		console.log('resume mix stdout: ' + data);
	}
});
oldSession.stderr.on('data', function (data) {
    console.log('resume stderr: ' + data);
	if(String(data).indexOf("EADDRINUSE")>-1){
		var errorPort = String(data).split(":::");
		errorPort = parseInt(errorPort[1].split("\n")[0]);
		respawnServer(errorPort);
	}
});

app.post('/election', function(req, res) {
	var task = req.body.task;
	var value = req.body.ID;
	var pass = req.body.password;
	
	
	var session = null;
	if (task === "complete"){
		
		// get increment in case of dublicate names
		var handlerConfigFile = JSON.parse(fs.readFileSync("../_handlerConfigFiles_/handlerConfigFile.json"));
		var incr = handlerConfigFile["electionsCreated"]+1;
		handlerConfigFile["electionsCreated"] = incr;
	    fs.writeFileSync("../_handlerConfigFiles_/handlerConfigFile.json", JSON.stringify(handlerConfigFile, null, 4), {spaces:4});
		
		// get available ports and mark them as used, sync 
		var rangePorts = handlerConfigFile["available-ports"];
	    var usingPorts = handlerConfigFile["usedPorts"];
	    var newPorts = [];
		
	    /**
	    for(var i = rangePorts[0]; i <= rangePorts[1]; i++){
			if(usingPorts.indexOf(i) < 0){
				usingPorts.push(i);
				newPorts.push(i);
			}
			if(newPorts.length >= 3+numMix){
				break;
			}
		}
		**/
	    for(var i = rangePorts[0]; i <= rangePorts[1]; i++){
	    	if(usingPorts.indexOf(i) < 0 && !portInUse(i)){
    			usingPorts.push(i);
				newPorts.push(i);
	    	}
	    	if(newPorts.length >= 3+numMix){
				break;
			}
	    }
	    
	    if (newPorts.length < 3+numMix)
	        res.end("Not enough ports available.");
	    else{
	    	//store new ports
	    	handlerConfigFile["usedPorts"] = usingPorts;
	    	fs.writeFileSync("../_handlerConfigFiles_/handlerConfigFile.json", JSON.stringify(handlerConfigFile, null, 4), {spaces:4});
	    }
	    var ports = JSON.stringify({usedPorts: newPorts, electionsCreated: incr});
	 
	    
	    
	    //hash password
		var salt = bcrypt.genSaltSync(10);
		var hash = bcrypt.hashSync(pass, salt);
		req.body.password = hash;
		var parameters = JSON.stringify(req.body);

		//call the python script to start the servers
		session = spawn('python', ['src/createElection.py', ports, parameters]);
		session.stdout.on('data', function (data) {
			if(String(data).indexOf("OTP")>-1){
				console.log('complete stdout: ' + data);
			}
			else if(String(data).indexOf("TLS")>-1){
				console.log('complete mix stdout: ' + data);
			}
		});
		session.stderr.on('data', function (data) {
		    console.log('complete stderr: ' + data);
			if(String(data).indexOf("EADDRINUSE")>-1){
				var errorPort = String(data).split(":::");
				errorPort = parseInt(errorPort[1].split("\n")[0]);
				respawnServer(errorPort);
			}
		    res.end(data);
		});

		session.on('exit', function (code) {
		    console.log('complete child process exited with code ' + code);
		    if(code === 0){
		    	res.end("created");
		    }
		    else{
		    	res.end("error code" + code)
		    }
		});
	}
	else if (task === "simple") {
		
		// get increment in case of dublicate names
		var handlerConfigFile = JSON.parse(fs.readFileSync("../_handlerConfigFiles_/handlerConfigFile.json"));
		var incr = handlerConfigFile["electionsCreated"]+1;
		handlerConfigFile["electionsCreated"] = incr;
	    fs.writeFileSync("../_handlerConfigFiles_/handlerConfigFile.json", JSON.stringify(handlerConfigFile, null, 4), {spaces:4});
		
		// get available ports and mark them as used, sync 
		var rangePorts = handlerConfigFile["available-ports"];
	    var usingPorts = handlerConfigFile["usedPorts"];
	    var newPorts = [];
	    for(var i = rangePorts[0]; i <= rangePorts[1]; i++){
	    	if(usingPorts.indexOf(i) < 0 && !portInUse(i)){
    			usingPorts.push(i);
				newPorts.push(i);
	    	}
	    	if(newPorts.length >= 3+numMix){
				break;
			}
	    }
	    if (newPorts.length < 3+numMix)
	        res.end("Not enough ports available.");
	    else{
	    //store new ports
	    handlerConfigFile["usedPorts"] = usingPorts;
	    fs.writeFileSync("../_handlerConfigFiles_/handlerConfigFile.json", JSON.stringify(handlerConfigFile, null, 4), {spaces:4});
	    }
	    var ports = JSON.stringify({usedPorts: newPorts, electionsCreated: incr});

		//call the python script to start the servers
	    session = spawn('python', ['src/createElection.py', ports]);
		session.stdout.on('data', function (data) {
			if(String(data).indexOf("OTP")>-1){
				console.log('simple stdout: ' + data);
			}
			else if(String(data).indexOf("TLS")>-1){
				console.log('simple mix stdout: ' + data);
			}
		});
		session.stderr.on('data', function (data) {
		    console.log('simple stderr: ' + data);
			if(String(data).indexOf("EADDRINUSE")>-1){
				var errorPort = String(data).split(":::");
				errorPort = parseInt(errorPort[1].split("\n")[0]);
				respawnServer(errorPort);
			}
		    res.end(data);
		});

		session.on('exit', function (code) {
		    console.log('simple child process exited with code ' + code);
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
		
		//call the python script to shutdown the servers
		session = spawn('python', ['src/removeElection.py', value, pass]);
		session.stdout.on('data', function (data) {
			console.log('remove stdout: ' + data);
		});
		session.stderr.on('data', function (data) {
		    console.log('remove stderr: ' + data);
		    res.end(data);
		});

		session.on('exit', function (code) {
		    console.log('remove child process exited with code ' + code);
		    if(code === 0){
		    	res.end("removed");
		    }
		    else{
		    	res.end("error code" + code)
		    }
		});
	}
});

var portInUse = function(port){
	var ghost = net.createServer();
	ghost.listen(port, function(err){
		ghost.once('close', function(){
			return false;
		});
		ghost.close();
	});
	ghost.on('error', function(err){
		if(err.code !== 'EADDRINUSE'){
			return err;
		}
		return true;
	})
	ghost.close()
	return false;
};


function respawnServer(errPort){
	console.log("\nPort " + errPort + " in use, attempting to start server on different port:")

	// get available ports and mark them as used, sync 
	var handlerConfigFile = JSON.parse(fs.readFileSync("../_handlerConfigFiles_/handlerConfigFile.json"));
	var rangePorts = handlerConfigFile["available-ports"];
    var usingPorts = handlerConfigFile["usedPorts"];
    var newPort = -1;
    for(var i = rangePorts[0]; i <= rangePorts[1]; i++){
    	if(usingPorts.indexOf(i) < 0 && !portInUse(i)){
    		newPort = i;
    		break;
    	}
    }
	if(newPort < 0){
		console.log("Not enough ports available.");
		return;
	}
	//remove blocked Port from list of ports being used
	usingPorts.push(newPort);
	handlerConfigFile["usedPorts"] = usingPorts;
	fs.writeFileSync("../_handlerConfigFiles_/handlerConfigFile.json", JSON.stringify(handlerConfigFile, null, 4), {spaces:4});
	console.log("Trying port " + newPort)

	//start new server with different port
    var reSession = spawn('python', ['src/restartServer.py', errPort, newPort]);
    reSession.stdout.on('data', function (data) {
    	console.log('reSpawn stdout: ' + data);
		if(String(data).indexOf("OTP")>-1){
			console.log('reSpawn stdout: ' + data);
		}
		else if(String(data).indexOf("TLS")>-1){
			console.log('mix stdout: ' + data);
		}
	});
    reSession.stderr.on('data', function (data) {
		if(String(data).indexOf("EADDRINUSE")>-1){
			var errorPort = String(data).split(":::");
			errorPort = parseInt(errorPort[1].split("\n")[0]);
			respawnServer(errorPort);
		}
	    console.log('reSpawn stderr: ' + data);
	});
}

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
	    console.log('Serving on, port :%d', server.address().port);
	});
	try{
		var manifest = JSON.parse(fs.readFileSync("../_handlerConfigFiles_/ElectionManifest.json"));
		var mixServers = manifest["mixServers"];
		numMix = mixServers.length;
	}
	catch(e){
		console.log("../_handlerConfigFiles_/ElectionManifest.json is missing or corrupt ([mixServers] field not found)");
	}
	try{
		var handlerConfigFile = JSON.parse(fs.readFileSync("../_handlerConfigFiles_/handlerConfigFile.json"));
		var usePorts = handlerConfigFile["available-ports"];
		console.log("\nPort range usable by the sElect servers: [" + usePorts[0] + " - " + usePorts[1] + "]\n" +
				"Each election needs at least 3 different servers: a collecting server, a bulletin board, and a mix server.\n" +
			    "However, the number of mix servers is not fixed: we suggest to use 3 to 5 mix servers for each elections.\n" +
			    "Assuming you use 3 mix servers, you can run up to *" + Math.floor((usePorts[1]-usePorts[0])/6) + "* elections at the same time " + 
			    "(if your hardware supports them).\n");
	}
	catch(e){
		console.log("../_handlerConfigFiles_/handlerConfigFile.json is missing or corrupt ([available-ports] field not found)");
	}
}
