var fs = require('fs');
var request = require('request-json');
var winston = require('winston');
var config = require('./config');
var manifest = require('./manifest');
var server = require('./server');
var sendEmail = require('./sendEmail');
var crypto = require('cryptofunc');

///////////////////////////////////////////////////////////////////////////////////////
// State

var otp_store = {};

var resultReady = fs.existsSync(config.RESULT_FILE);
var active = !resultReady; // active = accepts ballots


if (fs.existsSync(config.ACCEPTED_BALLOTS_LOG_FILE)) {
    console.log('Resuming (reading already accepted ballots)');
    var log_data = fs.readFileSync(config.ACCEPTED_BALLOTS_LOG_FILE, {flags:'r', encoding:'utf8'});
    log_data.split('\n').forEach(function (entry) { // for each entry in the log file
        if (entry==='') return;
        entry = JSON.parse(entry);
        console.log('  - processing a ballot of', entry.email);
        server.collectBallotSync(entry.email, entry.ballot);
    });
}

var log = fs.createWriteStream(config.ACCEPTED_BALLOTS_LOG_FILE, {flags:'a', encoding:'utf8'});

///////////////////////////////////////////////////////////////////////////////////////
// ROUTE otp
//

exports.otp = function otp(req, res) 
{
    var email = req.body.email;

    if (!active) {
        winston.info('OTP request (%s) ERROR: election closed.', email)
        res.send({ ok: false, descr: 'Election closed' }); 
        return;
    }

    if (email) {
        if (!server.eligibleVoters[email]) // Check if the voter is eligible
        {
            winston.info('OTP request (%s) ERROR: Voter not eligible', email);
            res.send({ ok: false, descr: 'Invalid voter identifier (e-mail)' }); 
        }
        else // eligible voter create a fresh OTP and send it
        {
            // Generate a fresh otp
            var otp = crypto.nonce();
            winston.info('OTP request (%s) accepted. Fresh OTP = %s', email, otp);
            otp_store[email] = otp // store the opt under the voter id (email)
            // schedule reset of the otp
            setTimeout( function(){ otp_store[email]=null; }, 10*60000); // 10 min

            // Send an email
            /*
            winston.info('Sending an emal with otp to', email, otp);
            sendEmail(email, 'Your One Time Password for sElect', otp, function (err,info) {
                if (err) {
                    winston.info(' ...Error:', err);
                }else{
                    winston.info(' ...E-mail sent: ' + info.response);
                }
                res.send({ ok: true }); 
            })
            */
            res.send({ ok: true }); // TODO: this is nestead of tha above
        }
    }
    else 
        res.send({ ok: false, descr: 'Empty e-mail address' }); 
};

///////////////////////////////////////////////////////////////////////////////////////
// ROUTE cast
//

exports.cast = function cast(req, res) 
{
    var email = req.body.email;
    var otp = req.body.otp;
    var ballot = req.body.ballot;

    // make sure that we have all the pieces:
    if (!email || !otp || !ballot ) {
        winston.info('Cast request (%s) ERROR: election closed.', email)
        res.send({ ok: false, descr: 'Wrong request' }); 
        return;
    }

    // is the server active?
    if (!active) {
        winston.info('Cast request (%s) ERROR: election closed.', email)
        res.send({ ok: false, descr: 'Election closed' }); 
        return;
    }

    // Check the otp (and, implicitly, the identifier)
    if (otp_store[email] === otp) {
        // Cast the ballot:
        server.collectBallot(email, ballot, function(err, response) {
            if (err) {
                winston.info('Cast request (%s) INTERNAL ERROR %s', email, err);
                res.send({ ok: false, descr: 'Internal error' }); 
            }
            else if (!response.ok) {
                winston.info('Cast request (%s) BALLOT REJECTED. Response = %s', email, response.data);
                res.send({ ok: false, descr: response.data }); 
            }
            else { // everything ok
                winston.info('Cast request (%s) accepted', email);
                res.send({ ok: true, receipt: response.data }); 
                // log the accepted ballot
                log.write(JSON.stringify({ email:email, ballot:ballot })+'\n', null,
                          function whenFlushed(e,r) {
                    winston.info('Ballot for %s logged', email);
                });
                // TODO: how to make sure that this stream is flushed right away
            }
        });
    }
    else // otp not correct
    {
        winston.info('Cast request ERROR: Invalid OTP');
        res.send({ ok: false, descr: 'Invalid OTP (one time password)' }); 
        // if an invalid otp is given, we require that a new otp be generated (reset otp):
        otp_store[email] = null;
    }
};



///////////////////////////////////////////////////////////////////////////////////////
// ROUTE info
//
exports.info = function info(req, res)  {
    res.render('info', {manifest:manifest, active: active, resultReady: resultReady});
}

///////////////////////////////////////////////////////////////////////////////////////
// ROUTE close
//

var finserv_options = {};
if (config.ignore_fin_serv_cert)
    finserv_options = {rejectUnauthorized: false};


// Save result in a file
function saveResult(result) {
    fs.writeFile(config.RESULT_FILE, result, function (err) {
        if (err) 
            winston.info('Problems with saving result', config.RESULT_FILE);
        else {
            winston.info('Result saved in', config.RESULT_FILE);
            resultReady = true;
        }
    });
}

// Send result to the final server
function sendResult(result) {
    winston.info('Sending result to the final server');
    var finServ = request.newClient(manifest.finalServer.URI, finserv_options);
    var data = {data: result}
    finServ.post('data', data, function(err, otp_res, body) {
        if (err) {
            winston.info(' ...Error: Cannot send the result to the final server: ', err);
        }
        else {
            winston.info(' ...Result sent to the final server.');
            winston.info(' ...Response:', body);
        }
    });
    // TODO: should we somewhow close the connection to the final server?
}

exports.close = function close(req, res)  {
    if (!active) {
        res.send({ ok: false, info: "election already closed" }); 
        return;
    }
    active = false;
    res.send({ ok: true, info: "triggered to close the election" }); 
    winston.info('Closing election.');
    server.getResult(function(err, result) {
        if (err) {
            winston.info(' ...INTERNAL ERROR. Cannot fetch the result: ', err);
        }
        else { 
            sendResult(result);
            saveResult(result);
        }
    });
}

///////////////////////////////////////////////////////////////////////////////////////
// Serve a particular static file
exports.serveFile = function serveFile(path) {
    return function (req, res) {
        fs.exists(path, function(exists) {
            if (exists) {
                fs.createReadStream(path).pipe(res);
            } else {
                res.status(404).send('404: Not found');
            }
        });
    }
}


