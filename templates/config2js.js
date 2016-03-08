var fs = require('fs');
var selectUtils = require('selectUtils');

if (process.argv.length !==  4) {
    console.log('ERROR: Call the script with two arguments, a file name with an election manifest and name:');
    console.log('node config2js <manifest-file-name.json> <var name for json>');
    process.exit(1);
}

var manifestFileName = process.argv[2];
var varname = process.argv[3];

var ms = fs.readFileSync(manifestFileName, 'utf8');
var norm = selectUtils.normalizeManifest(ms);
var norm = norm.replace(/"/g, '\\"')
console.log('var %s = "%s";', varname,norm);