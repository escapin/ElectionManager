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

app.post('/election', function(req, res) {
	var task = req.body.task;
	var value = req.body.ID;
	if (task === "create") {
		child_process.exec('python ../ElectionSetup/NewSession.py', function(err, stdout, stderr) {
			if (err) {
				console.log(err.code);
			}
			console.log(stdout);
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
