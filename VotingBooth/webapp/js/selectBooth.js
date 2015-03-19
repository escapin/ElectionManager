
function selectBooth() {


    //////////////////////////////////////////////////////////////////////////////
    /// PARAMETERS

    var FADE_TIME = 260;

    //////////////////////////////////////////////////////////////////////////////
    /// STATE


    // For navigation
    var activeTabId = "#welcome";

    // Manifest
    var manifest = JSON.parse(electionManifestRaw);
    manifest.hash = cryptofunc.hash(electionManifestRaw).toLowerCase();
    console.log('Election hash =', manifest.hash);

    // Voter and status
    var email = null;
    var otp = null;
    var choice = null;

    var electionID = manifest.hash;
    var shortenedElectionID = electionID.slice(0,6) + '...';
    var colServVerifKey = manifest.collectingServer.verification_key;
    // retrieve the encryption and verification keys of the mix servers from the manifest
    var mixServEncKeys = manifest.mixServers.map(function (ms) { return ms.encryption_key; })
    var mixServVerifKeys = manifest.mixServers.map(function (ms) { return ms.verification_key; })
    // create the voter object
    var voter = voterClient.create(electionID, colServVerifKey, mixServEncKeys, mixServVerifKeys);
 // var voter = voterClient.create(electionID, colServEncKey, colServVerifKey, mixServEncKeys);



    //////////////////////////////////////////////////////////////////////////////
    /// AUXILIARY FUNCTIONS

    function optionsAsHTML() {
        var options = '';
        var choices = manifest.choices;
        for (var i=0; i<choices.length; ++i) {
            var choice = choices[i];
            // console.log(choice);
            var slabel = '<label for="option-' +i+ '" class="pure-radio">\n';
            // console.log(slabel);
            var sinput = '<input id="option-' +i+ '" type="radio" name="choice" value="option' +1+ 
                         '"> ' +choice+ '</label>\n';
            // console.log(sinput);
            options += slabel;
            options += sinput;
        }
        return options;
    }

    // Returns a promise of the data from the given url.
    //
    function fetchData(url) {
        return new Promise(function (resolve, reject) {
            console.log('Fetching data from', url);
            $.get(url).done(resolve).fail(reject);
        });
    }

    // Runs tasks (functions creating promises) sequentially.
    // More precisely, composes the promises and returns the
    // sequential promise.
    function sequentially(tasks) {
        return tasks.reduce(
                  function (promise, task) { return promise.then(task); }, 
                  Promise.accept(null) // the initial (null) promise
               );
    }

    //////////////////////////////////////////////////////////////////////////////
    /// INITIATE BOOTH

    function initiateBooth() {
        // Detemine the status of the system: (not-yet) open/closed, 
        // by quering the final mix server.
        // Depending on the state, either the voting tab or the
        // verification tab will be opened.
        //
        // The state is detemined in a (too?) simple way, by
        // checking if the final server has ready result.
        //
        resultOfFinalServerReady()
        .then(function (resultReady) {  
            if (resultReady) {
                console.log('Result ready. We should verify now');
                doVerification();
            }
            else {
                console.log('Result not ready. Go to the voting.');
                showTab('#welcome');
            }
        })
        .catch(function (err) {
            console.log('Problem with the final server:', err)
            // TODO: what to do in this case (the final server is
            // done or it works for a different election ID)
            showTab('#welcome'); // for now, we just go to voting
        });

    }


    // Returns a promise of the state of the final mix server
    // The promise resolves to true if the result is ready and
    // to false otherwise.
    // The promise is rejected if the final server is down of
    // works for a different election.
    //
    function resultOfFinalServerReady() {
        return new Promise(function (resolve, reject) {
            var url = manifest.mixServers[manifest.mixServers.length-1].URI+'/status';
            $.get(url)
             .fail(function () { 
                reject('Server down');
              })
             .done(function (result) {  // we have some response
                if (result.electionID.toUpperCase() !== electionID.toUpperCase()) 
                    reject('Wrong election ID')
                else resolve (result.status==='result ready');
              });
        });
    }


    //////////////////////////////////////////////////////////////////////////////
    /// RECEIPTS

    // Saves receipt in the local storage. If there are already
    // some receipt stored, it adds the new receipt to these.
    //
    function storeReceipt(receipt) {
        console.log('Save receipt');
        var receipts, receiptsJSON;

        if ( localStorage.getItem('receipts') !== null ) {
            receiptsJSON = localStorage.getItem('receipts');
            receipts = JSON.parse(receiptsJSON);
            console.log('Old:', receipts);
            receipts.push(receipt);
        }
        else
            receipts = [receipt];
        receiptsJSON = JSON.stringify(receipts);
        console.log('Saving:', receiptsJSON);
        localStorage.setItem('receipts', receiptsJSON);
    }

    // Get the list of receipts (from the local storage)
    // Receipts with different election id are filtered out.
    function getReceipts() {
        var receiptJSON = localStorage.getItem('receipts');
        if (receiptJSON === null)
            return [];
        else {
            var rr = JSON.parse(receiptJSON);
            return rr.filter(function(r){ return r.electionID===electionID; });
        }
    }

    //////////////////////////////////////////////////////////////////////////////
    /// VERIFICATION

    // Does the verification of all the stored receipts.
    //
    function doVerification() {
        // Get the receipts
        var receipts = getReceipts();
        console.log('There is/are', receipts.length, 'receipts to verify:');
        for (var i=0; i<receipts.length; ++i) {
            console.log('  ', receipts[i].receiptID);
        }

        // If there is no receipts, there is nothing to do
        if (receipts.length == 0) { 
            console.log('No receipts, nothing to verify.');
            return;
        }

        // Fetch the result of the final mix server and run the
        // verification procedure on it
        var nlast = manifest.mixServers.length - 1;
        var url = manifest.mixServers[nlast].URI+'/result.msg';
        fetchData(url)
        .catch(function (err) {
            console.log('Cannot get the result from the final server:', err);
        })
        .then(function (data) {
            console.log('Result of the final mix server fetched:');
            verifyReceiptsAgainstFinalServer(receipts, data);
        });
    }

    // Check if the result of the final server contains is
    // correct w.r.t. all the receipts. If not, the blaming
    // procedure is initiated.
    function verifyReceiptsAgainstFinalServer(receipts, finalServResult) {
        var k = manifest.mixServers.length-1; // the index of the final sever
        var ok = true;
        for (var i=0; i<receipts.length; ++i) {
            var res = voter.checkMixServerResult(k, finalServResult, receipts[i]);
            if (res.ok) {
                console.log('Receipt', i, 'verified successfully.')
            }
            else {
                console.log('WARNING: Receipt', i, 'not verified:', res.descr);
                ok =false;
            }
        }

        if (!ok) { // Something went wrong. Assign the blame.
            blame(receipts);
        }
    }

    // Checks which server is to blame.
    //
    function blame(receipts) {
        console.log('BLAME');
        checkCollectingServer(receipts)
        .then(function() {
            checkMixServers(receipts);
        });
    }


    function checkCollectingServer(receipts) {
        console.log('CHECK COLLECTING SERVER');
        return fetchData(manifest.collectingServer.URI+'/result.msg').then(function (data) {
                console.log('The result of the collecting server fetched.');
                console.log('Verifying the result');
                for (var i=0; i<receipts.length; ++i) {
                    var res = voter.checkColServerResult(data, receipts[i])
                    console.log('Result for', receipts[i].receiptID, ':', res.descr);
                    // TODO: produce blaming info
                }
            })
            .catch(function (err) {
                console.log('Cannot fetch the result of the collecting server:', err);
            });
    }

    function checkMixServers(receipts) {
        // For each mix server create a task, which is a function
        // that creates a promise of the result of verification
        // of the i-th mix server 
        var tasks = manifest.mixServers.map(function (ms,i) { 
            return function () { return checkMixServer(i, receipts); } 
        });        
        sequentially(tasks); // run the tasks sequentially
    }


    // Returns a promise of the result of verification of the
    // k-th mix server.
    function checkMixServer(k, receipts) {
        console.log('CHECK MIX SERVER' , k);
        return fetchData(manifest.mixServers[k].URI+'/result.msg')
        .then(function (data) {
            console.log('The result of the mixing server fetched.');
            console.log('Verifying the result');
            for (var i=0; i<receipts.length; ++i) {
                var res = voter.checkMixServerResult(k, data, receipts[i])
                console.log('Result for', receipts[i].receiptID, ':', res.descr);
                // TODO: produce blaming info
            }
        })
        .catch(function (err) {
            console.log('Cannot fetch the result of the mixing server:', err);
        });
    }




    //////////////////////////////////////////////////////////////////////////////
    /// HANDLERS FOR SUMBITTING DATA 

    function showError(errorMessage) {
        $('#processing').hide();
        $('#errorMsg').text(errorMessage);
        activeTabId = '#error';
        $(activeTabId).fadeIn(FADE_TIME);
    }

    function showTab(tabId) {
        $('#processing').hide();
        activeTabId = tabId;
        $(tabId).fadeIn(FADE_TIME);
    }

    function showProgressIcon() {
        $('#processing').fadeIn(FADE_TIME*2);
    }

    function onSubmitWelcome(event) 
    {
        if (activeTabId!=='#welcome') return false;
        activeTabId=''; 

        // Fetching the email from the form
        var e = $('#inp-email').val();
        if( !e || e==='' ) // it should not happen
            return false;
        email = e;

        // Make the active tab disappear
        $('#welcome').fadeOut(FADE_TIME, function() {

            // show processing icon
            showProgressIcon();
            // Make an (ajax) otp request:
            $.post(manifest.collectingServer.URI+"/otp", {'email': email})
             .done(function otpRequestDone(result) {
                if (!result) {
                    showError('Unexpected error');
                }
                else if (!result.ok) {
                    showError("Server's responce: " + result.descr);
                }
                else {
                    // Show the next window (OTP)
                    $('#inp-otp').val(''); // emtpy the otp input field
                    showTab('#otp');
                    $('#inp-otp').focus();
                }
              })
             .fail(function otpRequestFailed() {
                showError('Cannot connect with the server');
              });
        });
        return false; // prevents any further submit action
    };

    function onSubmitOTP(event) {
        if (activeTabId!=='#otp') return false;
        activeTabId=''; 

        // Fetching the otp from the form
        var o = $('#inp-otp').val();
        if( !o || o==='' ) // it should not happen
            return false;
        otp = o;

        $('#otp').fadeOut(FADE_TIME, function() {
            showTab('#choice');
        });
        return false; // prevents any further submit action
    }

    function onSubmitChoice(event) {
        if (activeTabId!=='#choice') return false;
        activeTabId=''; 

        // Fetch the choice from the form
        var option = $('input[name="choice"]:checked').attr('id');
        choice = + option.slice('option-'.length);

        // Make the active tab disappear
        $('#choice').fadeOut(FADE_TIME, function() {

            // Create the ballot
            console.log('CREATING BALLOT FOR:', email, otp, choice);
            var receipt = voter.createBallot(choice);
            console.log('RECEIPT:', receipt);

            showProgressIcon();
            // Make an (ajax) cast request:
            $.post(manifest.collectingServer.URI+"/cast", {'email': email, 'otp': otp, 'ballot': receipt.ballot})
             .fail(function otpRequestFailed() {  // request failed
                showError('Cannot connect with the server');
              })
             .done(function castRequestDone(result) {  // we have some response
                if (!result) {  // but for some reason this is not set!
                    showError('Unexpected error');
                }
                else if (!result.ok) {  // server has not accepted the ballot
                    showError("Server's responce: " + result.descr);
                }
                else {
                    // Ballot accepted (result.ok is true). Verify the receipt.
                    // Add the obtained signature to the receipt
                    receipt.signature = result.receipt;
                    // and validate it
                    var receiptValid = voter.validateReceipt(receipt); 
                    if (receiptValid) {
                        // TODO Save the receipt
                        storeReceipt(receipt);

                        // show the "ballot accepted" tab
                        showTab('#result');
                        $('#receipt-id').text(receipt.receiptID.toUpperCase());
                    }
                    else { // receipt not valid
                        showError('Invalid receipt');
                    }
                }
              });
        });

        return false; // prevents any further submit action
    }

    function onSubmitError(event) {
        if (activeTabId!=='#error') return false;
        activeTabId=''; 

        // make the active tab disappear
        $('#error').fadeOut(FADE_TIME, function() {
            // show the welcome tab
            $('#inp-email').focus();
            showTab('#welcome');
        });
        return false; // prevents any further submit action
    }

    //////////////////////////////////////////////////////////////////////////////
    /// OTHER HANDLERS 

    function enableWhenNotEmpty(button, input) {
        return function() {
            var v = input.val();
            if( v==='' ) 
                button.prop('disabled', true);
            else 
                button.prop('disabled', null);
        };
    }

    function whenChoiceChanges() {
        // The selected item should be displayed in a stronger way. So:
        // Reset 'checked' class and add notchecked class for all the labels in the form
        $("#choice-form label").addClass('notchecked').removeClass('checked');
        // And do the oposite for the selected one
        $("#choice-form label[for='" + this.id + "']").addClass('checked').removeClass('notchecked');

        // Update the status of the submit button (active only when something is selected)
        if($('input[name="choice"]:checked').length == 0) { // no choice selected 
            $('#submit-choice').prop('disabled', true);
        }
        else { // some choice selected
            $('#submit-choice').prop('disabled', null);
        }
    }

    //////////////////////////////////////////////////////////////////////////////
    /// INITIALISATION AND BINDING
    
    // Election data
    $('h1.title').html(manifest.title + '<div class="electionid">(election identifier: ' +shortenedElectionID+ ')</div>');
    $('h3.subtitle').text(manifest.description);
    $('#choice-list').html(optionsAsHTML());

    // Event handlers binding
    $('#welcome form').submit(onSubmitWelcome);
    $('#otp form').submit(onSubmitOTP);
    $('#choice form').submit(onSubmitChoice);
    $('#error form').submit(onSubmitError);
    $('#inp-email').on('input', enableWhenNotEmpty($('#submit-email'), $('#inp-email')));
    $('#inp-otp').on('input', enableWhenNotEmpty($('#submit-otp'), $('#inp-otp')));
    $('input[name="choice"]').change(whenChoiceChanges);
    
    // Focus on the email input
    $('#inp-email').focus();

    initiateBooth(); // checks the status and opens the voting or verification tab
}

