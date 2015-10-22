var express = require("express");
var bodyParser = require("body-parser");
var app = express();
var cors = require('cors');
var child_process = require("child_process");

var config = require('./src/config');

var port = config.port;
var path = 'webapp/';

app.use(cors());
app.use(bodyParser.urlencoded({
	extended : false
}));

//var basicAuth = require('basic-auth-connect');
//app.use('/election/*', basicAuth('admin', '888')); // authentication for the admin panel only

app.post('/election', function(req, res) {
	var task = req.body.task;
	var value = req.body.ID;
	var etitle = req.body.title;
	var edesc = req.body.description;
	var startingTime = req.body.startTime;
	var endingTime = req.body.endTime;
	if (task === "create" && etitle === "") {
		child_process.exec('python ../ElectionSetup/NewSession.py', function(err, stdout, stderr) {
			if (err) {
				console.log(err.code);
			}
			console.log(stdout);
			if(stdout === "done"){
				res.end("created");
			}
			if (stderr) {
				console.log(stderr);
				res.end(stderr);
			}
			else{
				console.log("created");
				res.end("created");
			}
		});
	}
	else if (task === "create" && etitle !== "") {
		child_process.exec('python ../ElectionSetup/NewSession.py '+'"'+etitle+'"'+' '+'"'+edesc+'"'+' '+'"'+startingTime+'"'+' '+'"'+endingTime+'"', function(err, stdout, stderr) {
			if (err) {
				console.log(err.code);
			}
			console.log(stdout);
			if(stdout === "done"){
				res.end("created");
			}
			if (stderr) {
				console.log(stderr);
				res.end(stderr);
			}
			else{
				console.log("created");
				res.end("created");
			}
		});
	}
	else if (task === "remove") {
		child_process.exec('python ../ElectionSetup/CloseSession.py '+value, function(err, stdout, stderr) {
			if (err) {
				console.log(err.code);
			}
			console.log(stdout);
			if (stderr) {
				console.log(stderr);
				res.end(stderr);
			}
			else{
				console.log("removed");
				res.end("removed");
			}
		});
	}
});

var server = app.listen(port, function() {
    console.log('Serving %s on %s, port %d', path, server.address().address, server.address().port);
});
