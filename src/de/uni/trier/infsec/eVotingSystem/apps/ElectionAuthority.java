package de.uni.trier.infsec.eVotingSystem.apps;

import java.io.IOException;
import java.nio.file.FileSystems;
import java.nio.file.FileVisitResult;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.PathMatcher;
import java.nio.file.Paths;
import java.nio.file.SimpleFileVisitor;
import java.nio.file.attribute.BasicFileAttributes;
import java.util.LinkedList;

import de.uni.trier.infsec.eVotingSystem.bean.CollectingServerID;
import de.uni.trier.infsec.eVotingSystem.bean.FinalServerID;
import de.uni.trier.infsec.eVotingSystem.parser.Keys;
import de.uni.trier.infsec.eVotingSystem.parser.KeysParser;
import static de.uni.trier.infsec.eVotingSystem.apps.AppUtils.readCharsFromFile;
	
public class ElectionAuthority {
	public static void main(String[] args) throws IOException {
		
		// retrieve the public keys of Collecting Server
		String filename = AppParams.PUBLIC_KEY_dir + "CollectingServer_PU.json";
		String stringJSON = readCharsFromFile(filename);
		Keys k=KeysParser.parseJSONString(stringJSON);
		CollectingServerID colServID = new CollectingServerID(AppParams.colServURI, k.encrKey, k.verifKey);
		
		// retrieve the public keys of Final Server
		filename = AppParams.PUBLIC_KEY_dir + "FinalServer_PU.json";
		stringJSON = readCharsFromFile(filename);
		k=KeysParser.parseJSONString(stringJSON);
		FinalServerID finServID = new FinalServerID(AppParams.finServURI, k.encrKey, k.verifKey);
		
		// retrieve the public keys of voters
		String pattern="voter*";
		Path dir=Paths.get(AppParams.PUBLIC_KEY_dir);
		Finder finder = new Finder(pattern);
		Files.walkFileTree(dir, finder);
		for(Path p: finder.getMatches()){
			System.out.println(p);
		}
	}
	
	
	 public static class Finder extends SimpleFileVisitor<Path> {

     private final PathMatcher matcher;
     private int numMatches = 0;
     private LinkedList<Path> fMatched = new LinkedList<Path>();

     Finder(String pattern) {
         matcher = FileSystems.getDefault()
                 .getPathMatcher("glob:" + pattern);
     }

     // Compares the glob pattern against
     // the file or directory name.
     void find(Path file) {
         Path name = file.getFileName();
         if (name != null && matcher.matches(name)) {
             numMatches++;
             fMatched.add(name);
         }
     }

     int getNumMatches(){
    	 return numMatches;
     }
     LinkedList<Path> getMatches(){
    	 return fMatched;
     }

     // Invoke the pattern matching
     // method on each file.
     @Override
     public FileVisitResult visitFile(Path file,
             BasicFileAttributes attrs) {
         find(file);
         return FileVisitResult.CONTINUE;
     }

     // Invoke the pattern matching
     // method on each directory.
     @Override
     public FileVisitResult preVisitDirectory(Path dir,
             BasicFileAttributes attrs) {
         find(dir);
         return FileVisitResult.CONTINUE;
     }

     @Override
     public FileVisitResult visitFileFailed(Path file,
             IOException exc) {
         System.err.println(exc);
         return FileVisitResult.CONTINUE;
     }
 }
}
