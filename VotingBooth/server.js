var express = require('express');
var morgan = require('morgan');

var config = require('./src/config');

var port = config.port;
var path = 'webapp/';

var app = express();

app.use( morgan(':remote-addr [:date] :method :url :status / :referrer [:response-time ms]', {}) ); // logging
app.use(express.static(path)); // static content

var server = app.listen(port, function() {
    console.log('Serving %s on %s, port %d', path, server.address().address, server.address().port);
});
