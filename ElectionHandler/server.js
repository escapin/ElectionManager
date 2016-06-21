var express = require("express");
var bodyParser = require("body-parser");
var bcrypt = require("bcryptjs");
var read = require('read');
var fs = require('fs');
var http = require('http');
var mkdirp = require('mkdirp');
var net = require('net');
var async = require('async');

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



// parameter keeping track of the number of mix servers
var numMix = 0;
var handlerConfigFile = JSON.parse(fs.readFileSync("../_handlerConfigFiles_/handlerConfigFile.json"));
var maxElections = handlerConfigFile.maxNumberOfElections;
var createdElections = handlerConfigFile.electionsCreated;

ERRLOG_FILE = DATA_DIR + '/err.log';

app.post('/election', function(req, res) {
	var task = req.body.task;
	
	if((task === "complete" || task === "simple") && createdElections < maxElections) {
		// add the the async queue the task to be performed
		pythonQueue.push(req, function(data){
			res.end(data);
		});
	}
	else if(task === "complete" || task === "simple"){
		 res.end("Max Number of Elections handled by the server reached. Remove an election (if possible) or wait until an authorized user does it.");
	}
	else if(task === "remove"){
		// add the the async queue the task to be performed
		pythonQueue.push(req, function(data){
			res.end(data);
		});
	}
	else{
		res.end("Specify wether to create a mock Election or a ccustomized Election");
	}
	
});
app.get('/election', function(req, res) {
	console.log('accessing');
	res.send({ready: true});
});
		
/**
 * Create a ghost server and let it listen
 * to a port to check if the port is in use.
 */
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

var prevTime = new Date();
var prevProc = "";
function logError(data, callback){
	var time =  new Date();
	if(time.getTime() - prevTime.getTime() > 1000 || data.proc != prevProc){
		prevTime = time;
		prevProc = data.proc;
		data.err = "\n[ " + time + " ]:\n" + "error  at process: " + data.proc + "\n\n" + data.err; 
		console.log("[ " + time + " ]:\n an error occured, logged in " + ERRLOG_FILE + "\n");
	}
	fs.appendFile(ERRLOG_FILE, data.err, {encoding:'utf8'}, function(error){
		if(error){
			console.log("writing to "+ERRLOG_FILE+" failed while trying to write: " + data);
			callback(error);
		}
		else{
			callback();
		}
	});
}
var logErrQueue = async.queue(logError, 1);


/**
 * Dispatcher which calls the proper python script depending on the task to perform.
 * Each task has to be run sequentially (asynchronously).
 */

function spawnServer(req, callback){
	var task = req.body.task;
	if((task === "complete" || task === "simple") && createdElections >= maxElections){
		 callback("Max Number of Elections handled by the server reached. Remove an election (if possible) or wait until an authorized user does it.");
		 return;
	}
	/**
	 * the "retry" task is only called in case "EADDRINUSE" error
	 * happens during the spawning of a servers.
	 * In the old version of nodejs, there exists a documented bug where nodejs
	 * return "EADDRINUSE" even if the port is actually free.
	 * This method copes with this issue.
	 */
	if(task === "retry"){
		var errPort = req.errPort
		
		console.log("\nPort " + errPort + " in use, attempting to start server on different port:")
		var newPort = "placeholder";
		//start new server with different port
	    var reSession = spawn('python', ['src/restartServer.py', errPort, newPort]);
	    reSession.stdout.on('data', function (data) {
	    	//console.log('reSpawn STDOUT:\n\t' + data);
	    	if(String(data).indexOf("OTP")>-1){
	    		var time =  new Date();
	    		console.log('[' + time +  '] Collecting Server STDOUT:\n\t' + data);
	    	}
	    	else if(String(data).indexOf("TLS")>-1){
	    		var time =  new Date();
	    		console.log('[' + time +  '] Mix Server STDOUT:\n\t' + data);
	    	}
			else if(String(data).indexOf("Attempting to replace")>-1){
				console.log('' + data);
			}
			else if(String(data).indexOf("Reconfigurating")>-1){
				console.log('' + data);
			}
			if(String(data).indexOf("...done.")>-1){
				callback();
			}
		});
	    reSession.stderr.on('data', function (data) {
	    	//log the error in ERRLOG_FILE, async queue
	    	//to make sure it's not being written to 
	    	//simultaneously
	    	var dat = {err: data, proc: 'respawn'};
	    	logErrQueue.push(dat);

	    	if(String(data).indexOf("EADDRINUSE")>-1){
				var errorPort = String(data).split(":::");
				errorPort = parseInt(errorPort[1].split("\n")[0]);
				pythonQueue.push({body: {task: "retry"}, errPort: errorPort});
			}
			else if(String(data).indexOf("handlerConfigFile")>-1){
				callback();
			}
			else if(String(data).indexOf(".py")>-1){
				callback();
			}
		});
	}
	else if(task === "resume"){
		var oldSession = spawn('python', ['src/resumeElection.py']);
		oldSession.stdout.on('data', function (data) {
			if(String(data).indexOf("OTP")>-1){
				var time =  new Date();
				console.log('[' + time +  '] Collecting Server STDOUT:\n\t' + data);
			}
			else if(String(data).indexOf("TLS")>-1){
				var time =  new Date();
				console.log('[' + time +  '] Mix Server STDOUT:\n\t' + data);
			}
			else if(String(data).indexOf("Resuming elections")>-1){
				console.log('' + data);
			}
			if(String(data).indexOf("...done.")>-1){
				callback();
			}
		});
		oldSession.stderr.on('data', function (data) {
			//log the error in ERRLOG_FILE, async queue
	    	//to make sure it's not being written to 
	    	//simultaneously
			var dat = {err: data, proc: 'resume'};
	    	logErrQueue.push(dat);
	    	
			if(String(data).indexOf("EADDRINUSE")>-1){
				var errorPort = String(data).split(":::");
				errorPort = parseInt(errorPort[1].split("\n")[0]);
				pythonQueue.push({body: {task: "retry"}, errPort: errorPort});
			}
			else if(String(data).indexOf("handlerConfigFile")>-1){
				callback();
			}
			else if(String(data).indexOf(".py")>-1){
				callback();
			}
		});
	}
	else if(task === "complete"){
		var value = req.body.ID;
		var pass = req.body.password;
		var ports = "placeholder";
	    
	    
	    //hash password
		var salt = bcrypt.genSaltSync(10);
		var hash = bcrypt.hashSync(pass, salt);
		req.body.password = hash;
		var parameters = JSON.stringify(req.body);

		//call the python script to start the servers
		session = spawn('python', ['src/createElection.py', ports, parameters]);
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
			//log the error in ERRLOG_FILE, async queue
	    	//to make sure it's not being written to 
	    	//simultaneously
			var dat = {err: data, proc: 'complete'};
	    	logErrQueue.push(dat);

	    	if(String(data).indexOf("EADDRINUSE")>-1){
				var errorPort = String(data).split(":::");
				errorPort = parseInt(errorPort[1].split("\n")[0]);
				pythonQueue.push({body: {task: "retry"}, errPort: errorPort});
			}
		});

		session.on('exit', function (code) {
		    console.log('complete child process exited with code ' + code);
		    if(code === 0){
		    	createdElections = createdElections + 1;
		    	callback("created");
		    }
		    else{ // an error in createElection.py occurred
		    	callback("An error occurred while creating an election. Try again!");
			//res.end("error code" + code) //only for debugging
		    }
		});
	}
	else if(task === "simple"){
		var value = req.body.ID;
		var pass = req.body.password;
		var ports = "placeholder";

		//call the python script to start the servers
	    var session = spawn('python', ['src/createElection.py', ports]);
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
			//log the error in ERRLOG_FILE, async queue
	    	//to make sure it's not being written to 
	    	//simultaneously
			var dat = {err: data, proc: 'simple'};
	    	logErrQueue.push(dat);

	    	if(String(data).indexOf("EADDRINUSE")>-1){
				var errorPort = String(data).split(":::");
				errorPort = parseInt(errorPort[1].split("\n")[0]);
				pythonQueue.push({body: {task: "retry"}, errPort: errorPort});
			}
		});

		session.on('exit', function (code) {
		    console.log('simple child process exited with code ' + code);
		    if(code === 0){
		    	createdElections = createdElections + 1;
		    	callback("created");
		    }
		    else{ // an error in createElection.py occurred
		    	callback("An error occurred while creating an election: error code " + code + ". Try again!");
			//res.end("error code" + code) //only for debugging
		    }
		});
	}
	else if(task === "remove"){
		var value = req.body.ID;
		var pass = req.body.password;
		
		var passList = JSON.parse(fs.readFileSync("_data_/pwd.json"));
		if(!passList.hasOwnProperty(value)){
			//means the election already has been removed by another request,
			//therefore browser should act as if it had been removed by 
			//its own request.
			callback("removed");
			return;
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
		
		//call the python script to shutdown the servers
		session = spawn('python', ['src/removeElection.py', value, pass]);
		session.stdout.on('data', function (data) {
			console.log('remove stdout: ' + data);
		});
		session.stderr.on('data', function (data) {
			//log the error in ERRLOG_FILE, async queue
	    	//to make sure it's not being written to 
	    	//simultaneously
			var dat = {err: data, proc: 'remove'};
	    	logErrQueue.push(dat);
		});

		session.on('exit', function (code) {
		    console.log('remove child process exited with code ' + code);
		    if(code === 0){
		    	createdElections = createdElections - 1;
		    	callback("removed");
		    }
		    else{
		    	callback("error code" + code)
		    }
		});
	}
}

// the async queue with the dispatcher (worker) function as parameter.
// Since no tasks can be performed in parallel, only one
// dispatcher can run at any time
var pythonQueue = async.queue(spawnServer, 1);

/////////////////////////////////////////////////////////////////////////////////////////////
////////Start the server up

// Resume running/closed (not removed) elections
pythonQueue.push({body: {task: "resume"}, errPort: -1});


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
			    "Assuming you use 3 mix servers, you can run up to *" + Math.floor((usePorts[1]-(usePorts[0]+1))/6) + "* elections at the same time " + 
			    "(if your hardware supports them).\n");
	}
	catch(e){
		console.log("../_handlerConfigFiles_/handlerConfigFile.json is missing or corrupt ([available-ports] field not found)");
	}
}
