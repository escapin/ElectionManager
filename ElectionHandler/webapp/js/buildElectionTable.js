
// Builds the HTML Table from ElectionIDs
 function buildElectionTable() {
	 
	 var configs = JSON.parse(configRaw);
	 var host = configs.address;
	 var electionConf = JSON.parse(electionConfigRaw);	 
	 var elections = electionConf.elections;
	 
	 var head$ = $('<tr/>');
	 head$.append($('<td style="text-align:center"/>').html("&nbsp; Election IDs &nbsp;"));
	 head$.append($('<td style="text-align:center"/>').html("&nbsp; Election Title &nbsp;"));
	 head$.append($('<td style="text-align:center"/>').html("&nbsp; Election State &nbsp;"));
	 head$.append($('<td style="text-align:center"/>').html("&nbsp; Starting Time &nbsp;"));
	 head$.append($('<td style="text-align:center"/>').html("&nbsp; Ending Time &nbsp;"));
     $("#elections").append(head$);
     
     for (var i = 0 ; i < elections.length ; i++) {
    	 var elecID = elections[i].electionID;
    	 var elecStatus = 'waiting';
     
         var row$ = $('<tr/>');
         
         row$.append($('<td style="text-align:center"/>').html("&nbsp;&nbsp;&nbsp;"+elections[i].electionID+"&nbsp;&nbsp;&nbsp;"));
         row$.append($('<td style="text-align:center"/>').html("&nbsp;&nbsp;&nbsp;"+elections[i].electionTitle+"&nbsp;&nbsp;&nbsp;"));
         row$.append($('<td style="text-align:center" id='+elecID+'/>').html("&nbsp;&nbsp;&nbsp;"+elecStatus+"&nbsp;&nbsp;&nbsp;"));
         row$.append($('<td style="text-align:center"/>').html("&nbsp;&nbsp;&nbsp;"+elections[i].startTime.substring(0, elections[i].startTime.length-9)+"&nbsp;&nbsp;&nbsp;"));
         row$.append($('<td style="text-align:center"/>').html("&nbsp;&nbsp;&nbsp;"+elections[i].endTime.substring(0, elections[i].endTime.length-9)+"&nbsp;&nbsp;&nbsp;"));

         $("#elections").append(row$);
         
         getElectionStatus(elecID, function (eleID, stat){
    		 document.getElementById(eleID).innerHTML = stat;
    	 });
     }     
     
     
     function getElectionStatus(eleID, callback) {
         // Detemine the status of the system: (not-yet) open/closed, 
         // by quering the final mix server.
         // Depending on the state, either the voting tab or the
         // verification tab will be opened.
         //
         // The state is detemined in a (too?) simple way, by
         // checking if the final server has ready result.
         //
    	 var stat = 'what';
    	 var url = host+'/'+eleID+'/mix/03/status';
         $.get(url)
          .fail(function () { 
             var stat = 'no response';
             callback(eleID, stat)
           })
          .done(function (result) {  // we have some response
             var stat = 'pending';
        	 if (result.status==='result ready'){
            	 stat = 'closed';
             }
             else {
            	 stat = 'ready';
             }
             callback(eleID, stat)
           });

     }


     // Returns a promise of the state of the final mix server
     // The promise resolves to true if the result is ready and
     // to false otherwise.
     // The promise is rejected if the final server is down of
     // works for a different election.
     //
     function resultOfFinalServerReady(eleID) {
    	 var url = host+'/'+eleID+'/mix/03/status';
         $.get(url)
          .fail(function () { 
             return 'pending';
           })
          .done(function (result) {  // we have some response
             if (result.electionID.substring(0, 5).toUpperCase() !== electionID.toUpperCase()) {
                 reject('wrong election ID')
             }
             else if (result.status==='result ready'){
            		 return 'closed';
             }
             else {return 'ready';}
           });
     }
     
     
     ////////////////////////////////////////////////////////////////
     ///////// Refresh State
     
 	/* Refresh */
     window.setInterval(function() {
    	 for (var i = 0 ; i < elections.length ; i++) {
        	 var elecID = elections[i].electionID;
        	 getElectionStatus(elecID, function (eleID, stat){
        		 document.getElementById(eleID).innerHTML = stat;
        	 });
    	 }
     }, 1000);
     
     
     $('#welcome').show();
     
 }
 
 
 
