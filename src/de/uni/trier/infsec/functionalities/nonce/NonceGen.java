package de.uni.trier.infsec.functionalities.nonce;

import de.uni.trier.infsec.lib.crypto.CryptoLib;

public class NonceGen {
	public NonceGen() {
	}

	public byte[] newNonce() {
		return CryptoLib.generateNonce();
	}
}