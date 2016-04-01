////////////////////////////////////////////////////////////////////////////////////////////////////////////
//////////Builds the HTML Table from ElectionIDs

function buildElectionTable(res) {
	
	// expected time format is 'yy-mm-dd h:min [options not used yet]' in UTC+000 
	var resolveTime = function(time){
	    var dateTime = time.split(" ");
	    var date = dateTime[0].split("-");
	    var clientDate = new Date(date[0]+"-"+date[1]+"-"+date[2]+"T"+dateTime[1]);
	    clientDate = new Date(clientDate.setTime(clientDate.getTime()-clientDate.getTimezoneOffset()*60000))
	    
		var month = clientDate.getMonth()+1<10 ? "0"+(clientDate.getMonth()+1) : (clientDate.getMonth()+1);
		var day = clientDate.getDate()+1<10 ? "0"+clientDate.getDate() : clientDate.getDate();
		
		var hours = clientDate.getHours()	
		var dt = (hours>=12)?"PM":"AM";
		hours = (hours%12==0)?12:(hours%12);
				
		date = clientDate.getFullYear()+"-"+month+"-"+day;
		time = hours+":"+clientDate.getMinutes()+" "+dt;
		dateTime = date + " " + time;
		
	    return dateTime;
	}

    //////////////////////////////////////////////////////////////////////////////
    /// Escape HTML
    var MAP = { '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#39;'};

    function escapeHTML(s, forAttribute) {
    	return s.replace(forAttribute ? /[&<>'"]/g : /[&<>]/g, function(c) {
    		return MAP[c];
    	});
    }
	
    //////////////////////////////////////////////////////////////////////////////
    /// Build the election table
	var electionConf = JSON.parse(electionConfigRaw);	
	var elections = electionConf.elections;
	
	var lastMix = "http://localhost:"+electionConf["nginx-port"];
	//don't use port 80 if it's not deployed
	if(electionConf.deployment === true){
		var sAddresses = JSON.parse(sAddressesRaw);
		lastMix = sAddresses["server-address"].mix2;
	}
	 
	document.getElementById("elections").innerHTML = "";
		 
	var head$ = $('<tr/>');
	head$.append($('<th style="text-align:center"/>').html(" Election IDs "));
	head$.append($('<th style="text-align:center"/>').html(" Election Title "));
	head$.append($('<th style="text-align:center"/>').html(" Starting Time "));
	head$.append($('<th style="text-align:center"/>').html(" Ending Time "));
	head$.append($('<th style="text-align:center"/>').html(" Election State "));
	$("#elections").append(head$);
  
	for (var i = 0 ; i < elections.length ; i++) {
		var elecID = elections[i].electionID;
		var elecStatus = 'waiting';
		var startingTime = resolveTime(elections[i].startTime)
		var endingTime = resolveTime(elections[i].endTime)
		var row$ = $('<tr/>');
      
		row$.append($('<td style="text-align:center"/>').html("&nbsp;&nbsp;&nbsp;"+elections[i].electionID+" &nbsp;&nbsp;&nbsp;"));
		row$.append($('<td style="text-align:center"/>').html("&nbsp;&nbsp;&nbsp;"+escapeHTML(elections[i].electionTitle, true)+"&nbsp;&nbsp;&nbsp;"));
		row$.append($('<td style="text-align:center"/>').html("&nbsp;&nbsp;&nbsp;"+startingTime+"&nbsp;&nbsp;&nbsp;"));
		row$.append($('<td style="text-align:center"/>').html("&nbsp;&nbsp;&nbsp;"+endingTime+"&nbsp;&nbsp;&nbsp;"));
		row$.append($('<td style="text-align:center" id='+elecID+'/>').html("&nbsp;&nbsp;&nbsp;"+elecStatus+"&nbsp;&nbsp;&nbsp;"));
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
 	 var url = lastMix+'/'+eleID+'/mix/03/status';
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
         	 stat = 'open';
          }
          callback(eleID, stat)
        });

  }
  
  ////////////////////////////////////////////////////////////////
  ///////// Refresh State
  
	/* Refresh */
  var electionStates = window.setInterval(function() {
 	 for (var i = 0 ; i < elections.length ; i++) {
     	 var elecID = elections[i].electionID;
     	 getElectionStatus(elecID, function (eleID, stat){
     		 document.getElementById(eleID).innerHTML = stat;
     	 });
 	 }
  }, 1000);
  
  $('#welcome').show();
  
  res(electionStates);
  
}
