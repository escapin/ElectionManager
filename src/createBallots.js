var exports = {};
//////////////////////////////////////////////////////////////////////////////////////////////
var fs = require('fs');
var crypto = require('../sElect/node_modules/cryptofunc');
var strHexConversion = require('../sElect/node_modules/strHexConversion');
var unpair = crypto.deconcatenate;
var verif = crypto.verifsig;

var receiptID_LENGTH=10; // length of the verification code in case 'userChosenRandomness' is false 
// (if this number is odd, the next even integer is taken)

//SHORTCUTS
var pair = crypto.concatenate;
var enc  = crypto.pke_encrypt;
var dec  = crypto.pke_decrypt;

//TAGS (in hex encoding)

exports.TAG_ACCEPTED = "00";
exports.TAG_BALLOTS = '01';

exports.TAG_VERIFCODEAUTO = '02';
exports.TAG_VERIFCODEUSER = '03';

var acceptedBallotsFile = process.argv[2];
var userEmail = process.argv[3];
var userRandomCode = process.argv[4];
var choices = process.argv[5];
var userChoices = (choices.substring(1,choices.length-1)).split(",");
var electionID = process.argv[6];
var temp = process.argv[7];
var mixServEncKeys = (temp.substring(1,temp.length-1)).split(",");

/////////////////////////////////////////////////////////////////
function createBallot (choices, userCode) {
	// TODO choice now is an integer. It could be an arbitrary message
	
    // sort choices by number
	choices.sort(function(a,b){return a-b})
	var choiceMsg = "ffffffff"; // "ffffffff" is used in front of the concatenated choices as a delimiter
	for(var i=0; i < choices.length; i++){
		choices[i] = crypto.int32ToHexString(choices[i]);
		choiceMsg = pair(choiceMsg, choices[i]);
	}
    var N = mixServEncKeys.length; // the number of mix servers
    var ciphertexts = new Array(N+1); // array with the chain of ciphertexts 
    var randomCoins = new Array(N); // array with the used random coins

    
    
    
    if(userCode && userCode !== ''){ // verificationCode := (TAG_VERIFCODEUSER, receiptID, userCodeHex)
    	var userCodeHex = strHexConversion.hexEncode(userCode);
    	var receiptID = crypto.nonce().slice(0,8);
    	// only the first 8 digit of the receiptID are part of the verification code
    	var verificationCode = pair(exports.TAG_VERIFCODEUSER, pair(receiptID, userCodeHex));
    
    } else {	// verificationCode := (TAG_VERIFCODEAUTO, receiptID)
    	var userCode = ''; // NOTE: if userCode doesn't exist, it is set to the empty string
    	if(receiptID_LENGTH%2 == 0)
        	var receiptID = crypto.nonce().slice(0, receiptID_LENGTH);
        else
        	var receiptID = crypto.nonce().slice(0, receiptID_LENGTH+1);
    	
    	var verificationCode = pair(exports.TAG_VERIFCODEAUTO, receiptID);
    }
    
    
    ciphertexts[N] = pair(electionID, pair(choiceMsg, verificationCode));
    
    // encrypt the message for the chain of mix servers
    for (var i=N-1; i>=0; --i) {
        var r = crypto.pke_generateEncryprionCoins();
    	ciphertexts[i] = enc(mixServEncKeys[i], pair(electionID, ciphertexts[i+1]), r);
        randomCoins[i] = r;
    }

    ballot = ciphertexts[0];

    return { electionID: electionID, 
             ballot: ballot, 
             choice: choices, 
             userCode: userCode,
             receiptID: receiptID, 
             ciphertexts: ciphertexts,
             randomCoins: randomCoins};
}

var voted = createBallot(userChoices, userRandomCode);

var log = fs.createWriteStream(acceptedBallotsFile, {flags:'a', encoding:'utf8'});
log.write(JSON.stringify({ email:userEmail, ballot:voted.ballot })+'\n', null,
		function whenFlushed(e,r) {
			//console.log("Ballot for "+userEmail+": "+voted.ballot);
});

