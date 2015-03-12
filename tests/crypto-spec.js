var forge = require('node-forge');
var crypto = require('cryptofunc');

var hexToBytes = forge.util.hexToBytes;
var bytesToHex = forge.util.bytesToHex;

describe( 'Int/hex conversion', function()
{
    it( 'works as expected', function()
    {
        var n = 123467789;
        var hex = crypto.int32ToHexString(n);
        var r = crypto.hexStringToInt(hex);
        expect (r).toBe(n);
    });
});


describe( 'Conatenation and deconcatenation', function()
{
    it( 'are consistent', function()
    {
        var a = 'ffaa77';
        var b = 'cc9911227733';
        var p = crypto.deconcatenate(crypto.concatenate(a, b));
        expect (p.first) .toBe(a);
        expect (p.second).toBe(b);
    });
});


describe( 'Symmetric encryption', function()
{
    it( 'encrypts and then decrypts correctly', function()
    {
        var m = bytesToHex(forge.random.getBytesSync(1000)); // a random 1000-byte message
        var k = crypto.symkeygen();
        var c = crypto.symenc(k, m);
        var d = crypto.symdec(k, c);
        expect(d).toBe(m);
    });
});


describe( 'RSA Encryption', function()
{
    it( 'encrypts and then decrypts correctly', function()
    {
        var m = bytesToHex(forge.random.getBytesSync(60)); // a random 60-byte message
        var k = crypto.rsa_keygen();
        var c = crypto.rsa_encrypt(k.encryptionKey, m);
        var d = crypto.rsa_decrypt(k.decryptionKey, c);
        expect(d).toBe(m);
    });

    it( 'works correctly for some fixtures', function()
    {
        var encryption_key = "30819F300D06092A864886F70D010101050003818D0030818902818100B21E1FA56085DFEF9DA015A731CA2243FFF2A6354CD6C3AC5210C9D047702908A876F4E822A35A097BF0D8E0397A1B9C3F7BB4A055239E3F67500A707A3B5659FBCA35A1CEFFC251D72BE04F313A4B11451845E01F3A30B18546A521B268772051BC2ADC22EBDA6B9ECE530460A6DFE8818B1F53363E5C91BB7BA450C21AFCE90203010001";
        var decryption_key = "30820278020100300D06092A864886F70D0101010500048202623082025E02010002818100B21E1FA56085DFEF9DA015A731CA2243FFF2A6354CD6C3AC5210C9D047702908A876F4E822A35A097BF0D8E0397A1B9C3F7BB4A055239E3F67500A707A3B5659FBCA35A1CEFFC251D72BE04F313A4B11451845E01F3A30B18546A521B268772051BC2ADC22EBDA6B9ECE530460A6DFE8818B1F53363E5C91BB7BA450C21AFCE902030100010281807401E2A297671A1EBA0ED58B7B8627231AC433346BC344D62AECFC444702E9F6D5A204885C66FFF14563EC1CBDD2A5C0F227E3D0B922E5A26DEB57A1423AFB55B128D0A4289E27D0510CDCCAF268EC471B2FDC8F8A2C270B82BB0FD115A5DF1AFECE4680A64F6F62E64BA515F03E9C5FF891F0832DC2F6103DE02D1915C1DCF1024100E53FC931375907C421471E9A02518543AC4A521E56346586C8D4E7BC3C22F55E6F485781AE23F8A6C904D936147D3EE78FC0674D275D833ED5C1E3E9BA323CEB024100C6E6EB5184781CF25E5273FAFFE9C39EACD7B1986F0356DD3CA8226B1D6AF9A1A77A0E22CB3DBC60C920FEF75C6071643C07BE59B2D09BCB292F05A79E99287B024100BF8255B483A42054BBE809AC669B6B54692D7D0452C75AB90A34B192123AB1F7BDC71533042290A9E3EBE4F8C48D0C6BAD2EF21D05F19C9E753B9005C4C20B19024100B7D0B46C5376059A5F5CE7DE711F022FE42039FA5BADC45B1531750D74D465FAE521C16A9A55658034A00FC15E57AAB32D5F22A516C1FF1893E8E6DAEF912F7D024100BA4216E24F08F731F0DAF2566CB538954148CAEB9DA3F9667A0A421F7D5739B39FD8E0CA8FD41FA1F28559783AAFB15CC542BBC29ACD955D4F02A1F30C90A007";

        var m = '3f33';
        var c = "8a410a36675b34c778280dc892ed3c8a40626aceaa9991fe1888a2b5a77da45d84363372f496495c1f8dfa636b42fc92eb5f1e507f989e6f27cd827623dbf4c25cd1f42fff930b64082d04a8ad14402feb49761dd96644d7ebfea4f508f483eeeda6bf3da1a5691a29a51f87e41774d1dfdcac577b4417f73ce4e73b0d3ae559";

        var cc = crypto.rsa_encrypt(encryption_key, m);

        var d = crypto.rsa_decrypt(decryption_key, c);
        expect(d).toBe(m);

        var c1 = "61B3E404FF62F1EB2B0F435864B8CDA860D1ADB087CB9680B9317B6F8B4D25F844B860656CAADA7F997A5415DA7FAAB89F5D5D8D499E62898A70630C56CDCF74DC65DD34460446D3AFFA233854743F111D5032B4F01E12CFB7CD1271A7120D8D093441D26AD8544F991994D96A3F176B99817FF0305A442C02E872FDA3DFA040";
        var d1 = crypto.rsa_decrypt(decryption_key, c1);
        expect(d1).toBe(m);
    });

    it( 'works correctly with explicitly provided randomness', function ()
    {
        var randomness = '123456789a123456789a123456789012';
        var encryption_key = "30819F300D06092A864886F70D010101050003818D0030818902818100B21E1FA56085DFEF9DA015A731CA2243FFF2A6354CD6C3AC5210C9D047702908A876F4E822A35A097BF0D8E0397A1B9C3F7BB4A055239E3F67500A707A3B5659FBCA35A1CEFFC251D72BE04F313A4B11451845E01F3A30B18546A521B268772051BC2ADC22EBDA6B9ECE530460A6DFE8818B1F53363E5C91BB7BA450C21AFCE90203010001";
        var decryption_key = "30820278020100300D06092A864886F70D0101010500048202623082025E02010002818100B21E1FA56085DFEF9DA015A731CA2243FFF2A6354CD6C3AC5210C9D047702908A876F4E822A35A097BF0D8E0397A1B9C3F7BB4A055239E3F67500A707A3B5659FBCA35A1CEFFC251D72BE04F313A4B11451845E01F3A30B18546A521B268772051BC2ADC22EBDA6B9ECE530460A6DFE8818B1F53363E5C91BB7BA450C21AFCE902030100010281807401E2A297671A1EBA0ED58B7B8627231AC433346BC344D62AECFC444702E9F6D5A204885C66FFF14563EC1CBDD2A5C0F227E3D0B922E5A26DEB57A1423AFB55B128D0A4289E27D0510CDCCAF268EC471B2FDC8F8A2C270B82BB0FD115A5DF1AFECE4680A64F6F62E64BA515F03E9C5FF891F0832DC2F6103DE02D1915C1DCF1024100E53FC931375907C421471E9A02518543AC4A521E56346586C8D4E7BC3C22F55E6F485781AE23F8A6C904D936147D3EE78FC0674D275D833ED5C1E3E9BA323CEB024100C6E6EB5184781CF25E5273FAFFE9C39EACD7B1986F0356DD3CA8226B1D6AF9A1A77A0E22CB3DBC60C920FEF75C6071643C07BE59B2D09BCB292F05A79E99287B024100BF8255B483A42054BBE809AC669B6B54692D7D0452C75AB90A34B192123AB1F7BDC71533042290A9E3EBE4F8C48D0C6BAD2EF21D05F19C9E753B9005C4C20B19024100B7D0B46C5376059A5F5CE7DE711F022FE42039FA5BADC45B1531750D74D465FAE521C16A9A55658034A00FC15E57AAB32D5F22A516C1FF1893E8E6DAEF912F7D024100BA4216E24F08F731F0DAF2566CB538954148CAEB9DA3F9667A0A421F7D5739B39FD8E0CA8FD41FA1F28559783AAFB15CC542BBC29ACD955D4F02A1F30C90A007";
        var m = '3f33';
        var c0 = crypto.rsa_encrypt(encryption_key, m);
        var c1 = crypto.rsa_encrypt(encryption_key, m, randomness);
        var c2 = crypto.rsa_encrypt(encryption_key, m, randomness);
        var d = crypto.rsa_decrypt(decryption_key, c1);

        expect(c1).toBe(c2);
        expect(c1).toBe('a540e006482a8b8e5c5f4c64ed8ac93ff0ee19cd9413202326af336f3fa0942cc5e92faa95b7b5f05907e8dcefb190acd9a46672736cdae9727912bec073dfbfd8c9ba1bd99d355fd4839f0c4d501e008dd80392ff8428bc0235ef8330abc0766f1a8d8ffe6fd1e518963c110dd4b0c107dafb121265b742b504aa8de43a6681');
        expect(c0).not.toBe(c1);
        expect(d).toBe(m);
    });

});

describe( 'Hybrid encryption', function()
{
    it( 'encrypts and then decrypts correctly messages', function()
    {
        var m = bytesToHex(forge.random.getBytesSync(1000)); // a random message
        var k = crypto.pke_keygen();
        var c = crypto.pke_encrypt(k.encryptionKey, m);
        var d = crypto.pke_decrypt(k.decryptionKey, c);
        var res = (d===m)
        expect(res).toBe(true);
    });

    it( 'works correctly for some fixtures', function()
    {
        var encryption_key = "30819F300D06092A864886F70D010101050003818D0030818902818100B21E1FA56085DFEF9DA015A731CA2243FFF2A6354CD6C3AC5210C9D047702908A876F4E822A35A097BF0D8E0397A1B9C3F7BB4A055239E3F67500A707A3B5659FBCA35A1CEFFC251D72BE04F313A4B11451845E01F3A30B18546A521B268772051BC2ADC22EBDA6B9ECE530460A6DFE8818B1F53363E5C91BB7BA450C21AFCE90203010001";
        var decryption_key = "30820278020100300D06092A864886F70D0101010500048202623082025E02010002818100B21E1FA56085DFEF9DA015A731CA2243FFF2A6354CD6C3AC5210C9D047702908A876F4E822A35A097BF0D8E0397A1B9C3F7BB4A055239E3F67500A707A3B5659FBCA35A1CEFFC251D72BE04F313A4B11451845E01F3A30B18546A521B268772051BC2ADC22EBDA6B9ECE530460A6DFE8818B1F53363E5C91BB7BA450C21AFCE902030100010281807401E2A297671A1EBA0ED58B7B8627231AC433346BC344D62AECFC444702E9F6D5A204885C66FFF14563EC1CBDD2A5C0F227E3D0B922E5A26DEB57A1423AFB55B128D0A4289E27D0510CDCCAF268EC471B2FDC8F8A2C270B82BB0FD115A5DF1AFECE4680A64F6F62E64BA515F03E9C5FF891F0832DC2F6103DE02D1915C1DCF1024100E53FC931375907C421471E9A02518543AC4A521E56346586C8D4E7BC3C22F55E6F485781AE23F8A6C904D936147D3EE78FC0674D275D833ED5C1E3E9BA323CEB024100C6E6EB5184781CF25E5273FAFFE9C39EACD7B1986F0356DD3CA8226B1D6AF9A1A77A0E22CB3DBC60C920FEF75C6071643C07BE59B2D09BCB292F05A79E99287B024100BF8255B483A42054BBE809AC669B6B54692D7D0452C75AB90A34B192123AB1F7BDC71533042290A9E3EBE4F8C48D0C6BAD2EF21D05F19C9E753B9005C4C20B19024100B7D0B46C5376059A5F5CE7DE711F022FE42039FA5BADC45B1531750D74D465FAE521C16A9A55658034A00FC15E57AAB32D5F22A516C1FF1893E8E6DAEF912F7D024100BA4216E24F08F731F0DAF2566CB538954148CAEB9DA3F9667A0A421F7D5739B39FD8E0CA8FD41FA1F28559783AAFB15CC542BBC29ACD955D4F02A1F30C90A007";
        var ciphertext = "0000008071cbe711e2d086f6ff589db11da84685f2d1d10105d75c5fd2683642399fdd3fb5ddce8750ffc4464b124ef94dedf238b19e24fbefee37d00fe498e464faffb687b7a473718802d4de8e8cd6da0189937ddb63b728d2e1645b6b8ead8510520ef6ccf80950427255804c370ab5294c0489c850850790c013d75e205e86dc5bb17d31558be8dcd0d32991f5201d8c1bbf61854c26a17dba89e6d00c93d4b7";
        var plaintext = "3f37";

        var d = crypto.pke_decrypt(decryption_key, ciphertext);
        expect(d).toBe(plaintext);
    });

    it( 'works correctly with explicit randomness', function()
    {
        var m = '0123456789abcdef';
        var k = crypto.pke_keygen();

        var r = crypto.pke_generateEncryprionCoins();
        var c0 = crypto.pke_encrypt(k.encryptionKey, m);
        var c1 = crypto.pke_encrypt(k.encryptionKey, m, r);
        var c2 = crypto.pke_encrypt(k.encryptionKey, m, r);

        var d0 = crypto.pke_decrypt(k.decryptionKey, c0);
        var d1 = crypto.pke_decrypt(k.decryptionKey, c1);
        var d2 = crypto.pke_decrypt(k.decryptionKey, c2);

        expect(d0).toBe(m);
        expect(d1).toBe(m);
        expect(d2).toBe(m);

        expect(c1).toBe(c2);
        expect(c1).not.toBe(c0);
    });

});


describe( 'Digital signatures scheme', function()
{
    it( 'signs and verifies correctly', function()
    {
        var k = crypto.sig_keygen();
        var message  = 'ff008833';
        var message1 = 'ff008831';
        var signature = crypto.sign(k.signingKey, message);
        expect (crypto.verifsig(k.verificationKey, message, signature)).toBe(true);
        expect (crypto.verifsig(k.verificationKey, message1, signature)).toBe(false);
    });

    
    it( 'works correctly for some fixtures', function()
    {
	    var verificationKey = "30819f300d06092a864886f70d010101050003818d0030818902818100a09f0260f2ff296537887f04f2b78f7cf6ab1ca9ec613b5793d0e0a2420ef54727675a8348a486d04defc2e7eb14a34477b9946cf3355e937c9d7efd0fd4f9ad12ce24667ef148c0a5cd1bbdff183cf111e9adae4d5a836b13301c345a458877d7a7f9e47ec69b642d5ca0bd73f05f3f180f375d2c3274c1b670e505dde8ee4f0203010001";
	    var signingKey = "3082025d02010002818100a09f0260f2ff296537887f04f2b78f7cf6ab1ca9ec613b5793d0e0a2420ef54727675a8348a486d04defc2e7eb14a34477b9946cf3355e937c9d7efd0fd4f9ad12ce24667ef148c0a5cd1bbdff183cf111e9adae4d5a836b13301c345a458877d7a7f9e47ec69b642d5ca0bd73f05f3f180f375d2c3274c1b670e505dde8ee4f02030100010281801181029b5a1fe07cfd4e4cb9575215bb028ea73305659b37f20de34d0b71e1dcfd38502eda6dc39b53c2fb3496f3cacf1d55060dd17b517135355caf6b58445521ab0a900931ff5797c8fb58628370480b146e544a0a2b863f82cb0e04831f46e803e224664a9737b9f676fb3b1b082f918fef2286e9bb16a316c6bc3c968e31024100e2fe87e07b0bdac2ecaf0ad45a6995e9fc8ed5e3edfd3f82ab48a4d7caff19cfbf924040fc3261ab7212f3517b182bf4e78fedb5f2d9ed2a32719e28326e6245024100b52545621b9fbaa4126bbc6a1d44cfc3ef20b98319cf56637545c9c63e834dadc86917e62a392079d181216cc1ebf0ab6880fbb60fd43143fdf5e45456b6e183024100bbf76392eab175546663c886f1db6f0d945abf1980506e5009001da8a7eb387784be59c0b6560df4c78093c60c3586e8c4fbb52f2ecb710db939c66aa8e029350240410bb21f6985f0b22bbf2df7f8ac95e268829ababdd0dad779ebe6695e572dd4824b627e8e98d6d5876a5403469b1f5f9d75fb6cc3c0513476040eca4e1cfb5b02410097f2bfda3c5423122e3713c700166c8208f01eb8fe3d2a6ec694e69f2bb4ceb42d7e15b01e5b3f6dbece4c985d8bb09aa4c4e19f25bdf1be86ed72bde2b05efc";
        var signature = "109EA4F43C7B7517A4C957B23F083C06313F64E4B74FC7C860ABB94E4F06C37EA33133293BC44CB445833DA515B272F8DD8785E016F9573E3180A572EA0B52A54E2109BDD3BFC1BE5751D683ECE44F5512EA3D42AB9A0AB95D18E7BA55DBFCBEA3DCC5AD0714855A6F8E450A18CB59FFC0785278F3B1E057C73ACB778C48853B";


        var message  = '3f221f';
        var message1 = '3f221e';
        var signature1 = crypto.sign(signingKey, message);
        
        expect (crypto.verifsig(verificationKey, message, signature)).toBe(true);
        expect (crypto.verifsig(verificationKey, message1, signature)).toBe(false);

        // var signature1 = "62B0A89386126CD02FA293F50E2F783F170FF8ACCE69773186B3D0EBDAE17D86C319650A5DC1C491C4F5B122E88DC1E067C29B5597A0718AEF2024663C9AA4D5F6F66CB045ED8734361CB2DCAECE49CDB5D616124FF1249B9F226955640407F56D674730E0ECF75267E6486E175B3A2D01DF372430A098362F6452DA50E797CD";
        // expect (crypto.verifsig(verificationKey, message, signature1)).toBe(true);
    });
});


/*
describe( '', function()
{
    it( '', function()
    {

    });
});
*/

