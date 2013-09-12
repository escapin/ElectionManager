package de.uni.trier.infsec.targetRS3System;

import de.uni.trier.infsec.functionalities.pkienc.Decryptor;
import de.uni.trier.infsec.functionalities.pkisig.RegisterSig;
import de.uni.trier.infsec.functionalities.pkisig.RegisterSig.PKIError;
import de.uni.trier.infsec.functionalities.pkisig.Signer;
import de.uni.trier.infsec.functionalities.pkisig.Verifier;
import de.uni.trier.infsec.lib.network.NetworkError;
import de.uni.trier.infsec.targetRS3System.Utils.MessageSplitIter;
import de.uni.trier.infsec.utils.MessageTools;

public class FinalServer 
{	
	// Cryptographic functionalities
	private final Signer signer;
	private final Decryptor decryptor;
	private final Verifier collectingServerVerif;
	
	
	// CLASSES
	/**
	 * Error thrown if the input data is ill-formed.
	 */
	public static class Error extends Exception 
	{
		private static final long serialVersionUID = -7774319355577426610L;
		private String description;
		public Error(String description) {
			this.description = description;
		}
		public String toString() {
			return "Final Server Error: " + description;
		}
	}

	
	// CONSTRUCTORS
	
	public FinalServer(Signer signer, Decryptor decryptor) throws PKIError, NetworkError {
		this.signer = signer;
		this.decryptor = decryptor;
		// fetch the functionalities of the collecting server
		this.collectingServerVerif = RegisterSig.getVerifier(Params.SERVER1ID, Params.SIG_DOMAIN);
		
	}
	
	// PUBLIC METHODS
	
	/**
	 * Process data that supposed to be the input tally prepared and signed 
	 * by the collecting server. Returns the signed result of the election 
	 * (to be publicly posted). 
	 */
	public byte[] processInputTally(byte[] data) throws Error {
		// verify the signature of server1
		byte[] publicData = MessageTools.first(data);
		byte[] signature = MessageTools.second(data);
		if (!collectingServerVerif.verify(signature, publicData))
			throw new Error("Wrong signature");

		// create array to collect entries (votes with nonces)
		byte[][] entries = new byte[Params.NumberOfVoters][];
		int nextEntry = 0;
		
		// retrieve and process ballots (store decrypted entries in 'entries')
		byte[] ballotsAsAMessage = MessageTools.first(publicData);
		for( MessageSplitIter iter = new MessageSplitIter(ballotsAsAMessage); iter.notEmpty(); iter.next() ) {
			byte[] voteWithNonce = decryptor.decrypt(iter.current());
			if (voteWithNonce == null) // decryption failed
				throw new Error("Wrong data (decryption failed)");
			entries[nextEntry] = voteWithNonce;
			++nextEntry;
		}
		
		// format entries as one message
		byte[] entriesAsAMessage = Utils.concatenateMessageArray(entries, nextEntry);
		
		// sign them
		byte[] signatureOnEntries =  signer.sign(entriesAsAMessage);
		byte[] signedEntries = MessageTools.concatenate(entriesAsAMessage, signatureOnEntries);
		
		return signedEntries;
	}
}
