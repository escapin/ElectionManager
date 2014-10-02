var fs = require('fs');

// where to find files with the result

exports.index = function(manifest, RESULT_DIR) {
    var FINAL_RESULT  = RESULT_DIR + 'FinalResult.txt';
    var SIGNED_RESULT = RESULT_DIR + 'SignedFinalResult.msg';
    var PARTIAL_RESULT= RESULT_DIR + 'SignedPartialResult.msg';
    var candidates = manifest.choicesList;
    console.log(candidates);

    return function(req, res) {

        // check if file with the result exists
        if (fs.existsSync(FINAL_RESULT) && fs.existsSync(SIGNED_RESULT)) {
            // read the file:
            fs.readFile(FINAL_RESULT, {encoding:'utf8'}, function(err,data) {
                if (err) throw err;
                // split it into lines
                lines = data.split('\n')
                // and transform into a list of objects of the form {vote: ..., nonce ...}
                tt = lines
                     .filter( function(line) {
                        return line !== '';
                     })
                     .map( function (line) {
                              t = line.split(/ \t+/);
                              var vote = candidates[t[0]];
                              return {vote:vote, nonce:t[1]};
                      })
                // render the response
                res.render('result', {  manifest: manifest,
                                        title: 'TrustVote Result', 
                                        finalResult: SIGNED_RESULT,
                                        partialResult: PARTIAL_RESULT,
                                        result: tt 
                                     });
            })
        }
        else { // there is no file with result
            res.render('no_result', { title: 'TrustVote: No result', manifest: manifest }); 
        }
    }
};
