var request = require('request-json');
var java = require('java');
var config = require('../config');
var voter = require('../protocol/voter');

var colServ = request.newClient(config.colServURI);

///////////////////////////////////////////////////////////////////////////////////////////
// Helper functions

function renderError(res, error) {
    res.render('error',   {error: error} );
}

///////////////////////////////////////////////////////////////////////////////////////////

exports.welcome = function welcome(req, res) 
{
    res.render('welcome', {title: "sElect Welcome", manifest: config.manifest});
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
            renderError(res, " ...No otp responce from the collecting server");
        }
        else if (!body.ok) {
            renderError(res, " ...ERROR otp responce from the collecting server");
        }
        else {
            console.log(' ...The collecting server accepted an otp reqest');
            // Render the page (prompting for the otp):
            res.render('otp', {title: "sElect Welcome", email:email, manifest: config.manifest});
        }
    });
}

exports.select = function select(req, res) 
{
    res.render('select', { title: "sElect Welcome", 
                           email: req.body.email, 
                           otp:   req.body.otp,
                           manifest: config.manifest});
}

exports.cast = function cast(req, res) 
{
    var email = req.body.email;
    var otp   = req.body.otp;
    var choice_nr = +req.body.choice; // conversion to int
    if (!choice_nr) {
        renderError(res, "No candidate chosen");
        return;
    }
    var choice = config.manifest.choicesList[choice_nr];
    if (!choice) {
        renderError(res, "Wrong candidate number");
        return;
    }
    if (!email || !otp || !choice ) {
        renderError(res, "Internal Error"); // this should not happen
        return;
    }

    // Create the ballot (async Java call)
    voter.createBallot(choice_nr, function (err, ballot) {
        if (err) {
            console.log('Internal error:', err)
            renderError(res, "Internal error: cannot create a ballot.");
            return;
        }

        // Send the ballot to the collecting server (and obtain a receipt):
        var data = { ballot:ballot, email:email, otp:otp };
        console.log('Sending: ', data);
        colServ.post('cast', data, function(err, otp_res, body) {
            if (err) {
                renderError(res, "No responce from the collecting server. Ballot might have been not cast.");
                return;
            }
            if (!body.ok) {
                renderError(res, "Ballot not accepted by the collecting server");
                console.log('body: ', body);
                return
            }
            
            var receipt = body.receipt;
            console.log('The collecting server accepted a ballot reqest. Receipt = ', receipt);

            // Check the receipt (async Java call):
            voter.validateReceipt(receipt, config.manifest.electionID, ballot, function(err, recOK) {

                if (err) {
                    console.log('Internal error:', err)
                    renderError(res, "Internal error: no receipt validated.");
                    return;
                }

                if (!recOK) {
                    console.log('Receipt not valid!');
                    renderError(res, "Invalid receipt");
                }
                else {
                    console.log('Receipt ok');
                    res.render('cast', { title: "sElect Welcome", email: req.body.email, 
                                         choice: choice, manifest: config.manifest });
                }
            });
        });
    });
}

