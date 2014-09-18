/**
 * 
 */
package de.uni.trier.infsec.tests;

import junit.framework.TestCase;

import org.json.JSONObject;
import org.json.XML;
import org.junit.Before;
import org.junit.Test;


import de.uni.trier.infsec.eVotingSystem.parser.ElectionManifest;
import de.uni.trier.infsec.eVotingSystem.parser.ElectionManifestParser;
import de.uni.trier.infsec.eVotingSystem.parser.ElectionManifest.CapacityOverflowError;
import de.uni.trier.infsec.eVotingSystem.parser.ElectionManifest.CollectingServerID;
import de.uni.trier.infsec.eVotingSystem.parser.ElectionManifest.ElectionAlreadyArranged;
import de.uni.trier.infsec.eVotingSystem.parser.ElectionManifest.ElectionBoardError;
import de.uni.trier.infsec.eVotingSystem.parser.ElectionManifest.FinalServerID;
import de.uni.trier.infsec.eVotingSystem.parser.ElectionManifest.NotInElectionArranged;
import de.uni.trier.infsec.eVotingSystem.parser.ElectionManifest.URI;
import de.uni.trier.infsec.eVotingSystem.parser.ElectionManifest.VoterID;
import de.uni.trier.infsec.functionalities.digsig.Signer;
import de.uni.trier.infsec.functionalities.pkenc.Decryptor;

/**
 * @author scapin
 *
 */
public class TestElectionBoard extends TestCase
{

	public String electionID;
	
	public String title;
	public String description;		// of the election
	public String headline;			// the question to submit
	public String[] choicesList;	
	
	// public VoterID[] votersList;		
	// public ServerID[] collectingServers;
	// public ServerID[] finalServers;
	
	
	public long startTime, endTime;	// milliseconds time value since January 1, 1970, 00:00:00 GMT

	/**
	 * @throws java.lang.Exception
	 */
	@Before
	public void setUp() throws Exception
	{
		electionID="TestElectionBoard";
		title="Test of the Election Board";
		description="It is just a JSON generated by a Tested Class for the Election Board";
		headline="Please check whether everything is fine";
		choicesList=new String[]{"First Candidate", "Second Candidate", "Third Candidate", "And so on..."};
		startTime=System.currentTimeMillis();
		endTime=startTime + (3600*1000); // + 1h

	}

	@Test
	public void test() throws Exception
	{
		// ADD VOTERS
		VoterID[] votersList= new VoterID[3];
		
		int voterUniqueID = 0;
		byte[] encryption_key = new Decryptor().getEncryptor().getPublicKey();
		byte[] verification_key = new Signer().getVerifier().getVerificationKey();
		votersList[0]=new VoterID(voterUniqueID, encryption_key, verification_key);
		
		voterUniqueID = 1;
		encryption_key = new Decryptor().getEncryptor().getPublicKey();
		verification_key = new Signer().getVerifier().getVerificationKey();
		votersList[1]=new VoterID(voterUniqueID, encryption_key, verification_key);
		
		voterUniqueID = 2;
		encryption_key = new Decryptor().getEncryptor().getPublicKey();
		verification_key = new Signer().getVerifier().getVerificationKey();
		votersList[2]=new VoterID(voterUniqueID, encryption_key, verification_key);
		
		URI uriCollectingServer = new URI("localhost", 2000);
		encryption_key = new Decryptor().getEncryptor().getPublicKey();
		verification_key = new Signer().getVerifier().getVerificationKey();
		CollectingServerID colServer = new CollectingServerID(uriCollectingServer, encryption_key, verification_key);
		
		URI uriFinalServer = new URI("localhost", 3000);
		encryption_key = new Decryptor().getEncryptor().getPublicKey();
		verification_key = new Signer().getVerifier().getVerificationKey();
		FinalServerID finServer = new FinalServerID(uriFinalServer, encryption_key, verification_key);
		
		URI[] bulletinBoard = new URI[2];
		bulletinBoard[0] = new URI("localhost", 2500);
		bulletinBoard[1] = new URI("localhost", 3500);
		
		ElectionManifest elBoard = new ElectionManifest(electionID, 
				startTime, endTime,
				headline, choicesList, 
				votersList, colServer, 
				finServer, bulletinBoard);
		elBoard.setTitle(title);
		elBoard.setDescription(description);
		
		// generate manifest
		String stringJSON = ElectionManifestParser.generateJSON(elBoard);
		// PRINT THE MANIFEST in JSON
		System.out.println(stringJSON);
		
		// recreate the electionBoard from the JSON
		ElectionManifest newElBoard=ElectionManifestParser.parseJSONString(stringJSON);
		
		
		assertTrue(elBoard.equals(newElBoard)); // && newElBoard.equals(elBoard)
				
/*		ElectionManifest elBoard1 = new ElectionManifest(electionID, 
				startTime, endTime,
				headline, choicesList, 
				eligibleVoters, eligibleCollectingServers, 
				eligibleFinalServers, eligibleBulletinBoards);
		ElectionManifest elBoard2 = new ElectionManifest(electionID, 
				startTime, endTime,
				headline, choicesList, 
				eligibleVoters, eligibleCollectingServers, 
				eligibleFinalServers, eligibleBulletinBoards);
		
		assertTrue(elBoard.equals(elBoard1) && elBoard.equals(elBoard2));
		elBoard1.setElectionArranged();
		assertFalse(elBoard1.equals(elBoard) || elBoard1.equals(elBoard2));
		
		assertTrue(elBoard.equals(elBoard2));
		// ADD SERVERS
		int cServerUniqueID=-10;
		URI cServerURI = new URI("localhost", 2000);
		Decryptor cServerDec = new  Decryptor();
		Signer cServerSig = new Signer();
		elBoard.addCollectingServer(cServerUniqueID, cServerURI, 
				cServerDec.getEncryptor(), cServerSig.getVerifier());
		
		// now they must be false
		assertFalse(elBoard.equals(elBoard2));
		
		
		
		
		
		cServerUniqueID=-11;
		cServerURI = new URI("localhost", 2001);
		cServerDec = new  Decryptor();
		cServerSig = new Signer();
		elBoard.addCollectingServer(cServerUniqueID, cServerURI, 
				cServerDec.getEncryptor(), cServerSig.getVerifier());
		
		// try to add another collecting server
		try{ 
			elBoard.addCollectingServer(cServerUniqueID, cServerURI, 
					cServerDec.getEncryptor(), cServerSig.getVerifier());
			fail("Max number of collecting servers overflows " +
					"-- exception expected");
		} catch(ElectionBoardError e){} 		
		
		
		int fServerUniqueID=-20;
		URI fServerURI = new URI("localhost", 1789);
		Decryptor fServerDec = new  Decryptor();
		Signer fServerSig = new Signer();
		elBoard.addFinalServer(fServerUniqueID, fServerURI, 
				fServerDec.getEncryptor(), fServerSig.getVerifier());
		
		// ADD BULLETIN BOARDS
		URI bulletinBoard=new URI("localhost", 3000);
		elBoard.addBulletinBoards(bulletinBoard);
		// try to add another bulletin boards
		try{
			elBoard.addBulletinBoards(bulletinBoard);
			fail("Max number of bulletin boards overflows " +
					"-- exception expected");
		} catch(ElectionBoardError e){} 
		
		// ADD VOTERS
		int voterUniqueID = 0;
		Decryptor fVoterDec = new  Decryptor();
		Signer fVoterSig = new Signer();
		elBoard.addVoter(voterUniqueID, fVoterDec.getEncryptor(), fVoterSig.getVerifier());
		
		voterUniqueID = 1;
		fVoterDec = new  Decryptor();
		fVoterSig = new Signer();
		elBoard.addVoter(voterUniqueID, fVoterDec.getEncryptor(), fVoterSig.getVerifier());
		
		voterUniqueID = 2;
		fVoterDec = new  Decryptor();
		fVoterSig = new Signer();
		elBoard.addVoter(voterUniqueID, fVoterDec.getEncryptor(), fVoterSig.getVerifier());
		// try to add another voter
		try{
			elBoard.addVoter(voterUniqueID, fVoterDec.getEncryptor(), fVoterSig.getVerifier());
			fail("Max number of bulletin boards overflows " +
					"-- exception expected");
		} catch(CapacityOverflowError e){}
		
		
		try{
			ElectionManifestParser.generateJSON(elBoard);
			ElectionManifestParser.generateXML(elBoard);
			fail("Not in ELECTION_ARRANGED mode" +
					"-- exception expected");
		} catch(NotInElectionArranged e) {}
		
		elBoard.setElectionArranged();
		// try to add the second final server
		try{
			elBoard.addFinalServer(fServerUniqueID, fServerURI, 
			fServerDec.getEncryptor(), fServerSig.getVerifier());
			fail("Already in ELECTION_ARRANGED mode" +
				"-- exception expected");
		} catch(ElectionAlreadyArranged e){}
		
		// generate manifest
		String stringJSON = ElectionManifestParser.generateJSON(elBoard);
		// PRINT THE MANIFEST in JSON
		System.out.println(stringJSON);
		
		// now they should be in the same mode
		assertTrue(elBoard.getMode().equals(elBoard.getMode()));
		
		
		// recreate the electionBoard from the JSON
		ElectionManifest newElBoard=ElectionManifestParser.parseJSONString(stringJSON);
		
//		assertTrue(elBoard!=null && newElBoard!=null);
//		assertTrue(newElBoard.electionID.equals(elBoard.electionID) &&
//						newElBoard.headline.equals(elBoard.headline));
//		assertTrue(	newElBoard.eligibleVoters==elBoard.eligibleVoters &&
//					newElBoard.eligibleCollectingServers==elBoard.eligibleCollectingServers &&
//					newElBoard.eligibleFinalServers==elBoard.eligibleFinalServers &&
//					newElBoard.eligibleBulletinBoards==elBoard.eligibleBulletinBoards);
//		assertTrue(elBoard.startTime==newElBoard.startTime);
//		assertTrue(elBoard.endTime==newElBoard.endTime);
//		assertTrue(elBoard.getMode().equals(newElBoard.getMode()));
//		assertTrue(Utilities.arrayEqual(elBoard.choicesList,newElBoard.choicesList));
//		
//		assertTrue(Utilities.arrayEqual(elBoard.getVotersList(),newElBoard.getVotersList()));
//		assertTrue(Utilities.arrayEqual(elBoard.getCollectingServers(),newElBoard.getCollectingServers()));
//		assertTrue(Utilities.arrayEqual(elBoard.getFinalServers(),newElBoard.getFinalServers()));
//		assertTrue(Utilities.arrayEqual(elBoard.getBulletinBoards(),newElBoard.getBulletinBoards()));
		
		
		assertTrue(elBoard.equals(newElBoard)); // && newElBoard.equals(elBoard)
		
		// TEST XML
	
		// generate manifest in XML
		String stringXML=ElectionManifestParser.generateXML(elBoard);
		// PRINT THE MANIFEST IN XML
		System.out.println("\n");
		System.out.println(stringXML);

		 
		 * FIXME: the library method XML.toJSONObject(stringXML) do not create
		 * a new JSONObject properly when there is an array with just one 
		 * element:
		 * it produces a JOSNObject element instead of an
		 * JSONArray with only one element inside!
		 * 
		 * e.g. FinalServers in our case
		 	
		JSONObject manifest=XML.toJSONObject(stringXML);
		System.out.println("\n");
		System.out.println(manifest.toString(1));
		//newElBoard = ElectionManifest.parseXMLString(stringXML);
*/		//assertTrue(elBoard.equals(newElBoard));
		
	}

}
