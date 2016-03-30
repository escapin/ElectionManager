var exports = {};
//////////////////////////////////////////////////////////////////////////////////////////////

var crypto = require('./cryptofunc');
var strHexConversion = require('./strHexConversion');
var unpair = crypto.deconcatenate;
var verif = crypto.verifsig;


//SHORTCUTS

var pair = crypto.concatenate;
var enc  = crypto.pke_encrypt;
var dec  = crypto.pke_decrypt;

//TAGS (in hex encoding)

exports.TAG_ACCEPTED = "00";
exports.TAG_BALLOTS = '01';

exports.TAG_VERIFCODEAUTO = '02';
exports.TAG_VERIFCODEUSER = '03';

var electionID = process.argv[2];
var mixServEncKeys = ["30819f300d06092a864886f70d010101050003818d0030818902818100cb284b1a88cada6bd932c35dcbe4ebbc1cd898ac42f70d78957b8ea7474c9970f78668f7290f37013cb1d3c4af415b9e089bb0941a3ce5e68d95be4adb16828e439943313fb82e8a1db34922cc0366aefb7c047332a3c1c4f9b4d5706ad0237b8552ecda113c8c23ee087a82ee2bc9b41635f454fbb444457ffa89fe28a7ece10203010001",
                      "30819f300d06092a864886f70d010101050003818d003081890281810084201e93ef882abe4a5ba8ccc7700cc181b19c564074b796de4295cc771d92a835478bd1359170f1b65fa8aa76591cd23722d345f8dd6b47d524a8fb21c165d3d378017c9d70bf86b857092f227f8d9ea8d8f6c23751c249e78ebab05a582d261af8b657fde9bcad8ff8796205570e298f626a112e137e3732ab0fc99dbb17350203010001",
                      "30819f300d06092a864886f70d010101050003818d00308189028181008fb23c73e75d2a47be9cdb91ebf6541e6ec7cdc896120d4c7572d1bb0174d56e3c4772315d510ad56ef9ef7e0a640a249553baa9bb4b3aa62fa08cc7cc6ade4783d26574e46a30cc47982402629c76afdb9df2ffad3c7d33c2fc8f552ce5f351be66da64d0690ffd691757046399090e0c6b66f72ee942c4cab92ae95c8eb5270203010001"
                      ];
//var userEmail = process.argv[3];
//var userChoice = process.argv[4];
//var userRandomCode = process.argv[5];

/////////////////////////////////////////////////////////////////
function createBallot (choice, userCode) {
	// TODO choice now is an integer. It could be an arbitrary message
    var choiceMsg = crypto.int32ToHexString(choice);
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
    	var receiptID = crypto.nonce().slice(0,18);
    	
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
             choice: choice, 
             userCode: userCode,
             receiptID: receiptID, 
             ciphertexts: ciphertexts,
             randomCoins: randomCoins};
}
console.log(createBallot(2, "12345678").ballot);
		/**
        // Create the voter
        var voter = voterClient.create(electionID, colServVerifKey, mixServEncKeys);

        // Create a ballot: [choice, userCode]
        var choice = 3;
        var userCode = "k43fa/ei";
        var receipt = voter.createBallot(choice, userCode);

        // Create the signature of the collecting server
        var message = pair(TAG_ACCEPTED, pair(electionID, receipt.ballot));
        var signature = crypto.sign(colServerKey.signingKey, message);

        // Complete the receipt by the signature
        receipt.signature = signature;

        // Verify the receipt
        var receiptOK = voter.validateReceipt(receipt);
        expect(receiptOK).toBe(true);

        // Re-create the ballot using the randomness in the receipt:
        var choiceMsg = crypto.int32ToHexString(choice);
        var userCodeMsg = strHexConversion.hexEncode(userCode);
        var N = mixServEncKeys.length;
        var verifCode = pair(TAG_VERIFCODEUSER, pair(receipt.receiptID, userCodeMsg));
        var x = pair(electionID, pair(choiceMsg, verifCode));
        for (var i=N-1; i>=0; --i) {
        	x = enc(mixServEncKeys[i], pair(electionID, x), receipt.randomCoins[i]);
            expect(x).toBe(receipt.ciphertexts[i]);
        }

        // Fake the decryption process (done by the mix servers)
        x = receipt.ballot;
        for (var i=0; i<N; ++i) {
            expect(x).toBe(receipt.ciphertexts[i]);
            x = dec(mixServKeys[i].decryptionKey, x);
            expect(x).not.toBe(null);
            var p = crypto.deconcatenate(x);
            expect(p.first).toBe(electionID);
            x = p.second;
        }
        // Check the plaintexts
        p = crypto.deconcatenate(x);
        expect(p.first).toBe(electionID);
        p = crypto.deconcatenate(p.second);
        expect(crypto.hexStringToInt(p.first)).toBe(choice);
        p = crypto.deconcatenate(p.second);
        expect(p.first).toBe(TAG_VERIFCODEUSER);
        p = crypto.deconcatenate(p.second);
        expect(p.first).toBe(receipt.receiptID);
        expect(strHexConversion.hexDecode(p.second)).toBe(userCode);

        console.log(receipt);
        **/
    /**
    it( ' without user code works as expected', function()
    	    {
    	        // Create the voter
    	        var voter = voterClient.create(electionID, colServVerifKey, mixServEncKeys);

    	        // Create a ballot: [choice, userCode]
    	        var choice = 3;
    	        
    	        var receipt = voter.createBallot(choice);

    	        expect(receipt.userCode).toBe('');
    	        
    	        // Create the signature of the collecting server
    	        var message = pair(TAG_ACCEPTED, pair(electionID, receipt.ballot));
    	        var signature = crypto.sign(colServerKey.signingKey, message);

    	        // Complete the receipt by the signature
    	        receipt.signature = signature;

    	        // Verify the receipt
    	        var receiptOK = voter.validateReceipt(receipt);
    	        expect(receiptOK).toBe(true);

    	        // Re-create the ballot using the randomness in the receipt:
    	        var choiceMsg = crypto.int32ToHexString(choice);
    	        var N = mixServEncKeys.length;
    	        var verifCode = pair(TAG_VERIFCODEAUTO, receipt.receiptID);
    	        var x = pair(electionID, pair(choiceMsg, verifCode));
    	        for (var i=N-1; i>=0; --i) {
    	        	x = enc(mixServEncKeys[i], pair(electionID, x), receipt.randomCoins[i]);
    	            expect(x).toBe(receipt.ciphertexts[i]);
    	        }

    	        // Fake the decryption process (done by the mix servers)
    	        x = receipt.ballot;
    	        for (var i=0; i<N; ++i) {
    	            expect(x).toBe(receipt.ciphertexts[i]);
    	            x = dec(mixServKeys[i].decryptionKey, x);
    	            expect(x).not.toBe(null);
    	            var p = crypto.deconcatenate(x);
    	            expect(p.first).toBe(electionID);
    	            x = p.second;
    	        }
    	        // Check the plaintexts
    	        p = crypto.deconcatenate(x);
    	        expect(p.first).toBe(electionID);
    	        p = crypto.deconcatenate(p.second);
    	        expect(crypto.hexStringToInt(p.first)).toBe(choice);
    	        p = crypto.deconcatenate(p.second);
    	        expect(p.first).toBe(TAG_VERIFCODEAUTO);
    	        expect(p.second).toBe(receipt.receiptID);

    	        //console.log(receipt);
    	    });
});**/


