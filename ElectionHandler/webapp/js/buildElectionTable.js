
// Builds the HTML Table from ElectionIDs
 function buildElectionTable() {
	 
	 var electionConf = JSON.parse(electionConfigRaw);
	 var electionIDs = electionConf.electionIDs;

	 var head$ = $('<tr/>');
	 head$.append($('<td/>').html("Elections by ID"));
     $("#elections").append(head$);
     
     for (var i = 0 ; i < electionIDs.length ; i++) {
         var row$ = $('<tr/>');
         
         row$.append($('<td/>').html(electionIDs[i]));
         $("#elections").append(row$);
     }
 }
 
 