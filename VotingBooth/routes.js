var request = require('request-json');
var java = require('java');
var voterClient = require('voterClient');
var config = require('./config');
var manifest = require('./manifest');

///////////////////////////////////////////////////////////////////////////////////////////
// Voter Client object

var voter = voterClient.create( manifest.hash, 
                                manifest.collectingServer.encryption_key, 
                                manifest.collectingServer.verification_key, 
                                manifest.finalServer.encryption_key );

///////////////////////////////////////////////////////////////////////////////////////////
// Collecting server object

var colserv_options = {};
if (config.ignore_col_serv_cert)
    colserv_options = {rejectUnauthorized: false};

var colServ = request.newClient(manifest.collectingServer.URI, colserv_options);

///////////////////////////////////////////////////////////////////////////////////////////
// Helper functions

function renderError(res, error) {
    res.render('error',   {error: error} );
}

///////////////////////////////////////////////////////////////////////////////////////////

exports.welcome = function welcome(req, res) 
{
    res.render('welcome', {title: "sElect Welcome", manifest: manifest});
};

exports.prompt_for_otp = function prompt_for_otp(req, res) 
{
    var email = req.body.email;

    // TODO check if the e-mail is eligible, if not, redirect to the welcome page.

    // Send the otp request to the collecting server:
    var data = { email:email };
    console.log('Sending an otp request: ', data);
    colServ.post('otp', data, function(err, otp_res, body){
        if(err) {
            console.log('Error:', err);
            renderError(res, "No responce from the collecting server");
        }
        else if (!body.ok) {
            renderError(res, body.descr);
        }
        else {
            console.log(' ...The collecting server accepted an otp reqest');
            // Render the page (prompting for the otp):
            res.render('otp', {title: "sElect Welcome", email:email, manifest: manifest});
        }
    });
}

///////////////////////////////////////////////////////////////////////////////////////////

exports.select = function select(req, res) 
{
    res.render('select', { title: "sElect Welcome",
                           email: req.body.email,
                           otp:   req.body.otp,
                           manifest: manifest});
}

///////////////////////////////////////////////////////////////////////////////////////////

exports.cast = function cast(req, res) 
{
    var email = req.body.email;
    var otp   = req.body.otp;
    if (req.body.choice == null) {
        renderError(res, "No candidate chosen");
        return;
    }
    var choice_nr = +req.body.choice; // conversion to int
    var choice = manifest.choices[choice_nr];
    if (!choice) {
        renderError(res, "Wrong candidate number");
        return;
    }
    if (!email || !otp || !choice ) {
        renderError(res, "Internal Error"); // this should not happen
        return;
    }

    // Create the ballot (async Java call)
    console.log('Create ballot for %s with choice %d', email, choice_nr);
    var ballot_info = voter.createBallot(choice_nr);
    if (!ballot_info.ballot) {
        console.log('Internal error: cannot create a ballot');
        renderError(res, "Internal error: cannot create a ballot.");
        return;
    }

    // Send the ballot to the collecting server (and obtain a receipt (signature)):
    var data = { ballot:ballot_info.ballot, email:email, otp:otp };
    console.log('Sending: ', data);
    colServ.post('cast', data, function(err, otp_res, body) {
        if (err) {
            renderError(res, "No responce from the collecting server. Ballot might have been not cast.");
            return;
        }
        if (!body.ok) {
            renderError(res, body.descr);
            console.log('body: ', body);
            return;
        }

        var receipt = body.receipt;
        console.log('The collecting server accepted the ballot reqest. Receipt = ', receipt);

        // Check the receipt (async Java call):
        console.log('Validate receipt for', email);
        var recOK = voter.validateReceipt(receipt, ballot_info.innerBallot )
        if (!recOK) {
            console.log('Receipt not valid!');
            renderError(res, "Invalid receipt");
        }
        else {
            console.log(' ...Receipt ok');
            res.render('cast', { title: "sElect Welcome",
                                 email: req.body.email,
                                 choice: choice,
                                 receipt_id: ballot_info.nonce,
                                 inner_ballot: ballot_info.innerBallot,
                                 manifest: manifest });
        }
    });
}

