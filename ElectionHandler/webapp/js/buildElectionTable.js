////////////////////////////////////////////////////////////////////////////////////////////////////////////
//////////Builds the HTML Table from ElectionIDs

function buildElectionTable(res) {
	
	// expected time format is 'yy-mm-dd h:min [options not used yet]' in UTC+000 
	var resolveTime = function(time){
	    var dateTime = time.split(" ");
	    var date = dateTime[0].split("-");
	    // create a Date object from the incoming time string
	    var clientDate = new Date(date[0]+"-"+date[1]+"-"+date[2]+"T"+dateTime[1]+"Z");
	    // display 03 for March instead of 3 (and months below 10)
		var month = clientDate.getMonth()+1<10 ? "0"+(clientDate.getMonth()+1) : (clientDate.getMonth()+1);
		var day = clientDate.getDate()<10 ? "0"+clientDate.getDate() : clientDate.getDate();
		
		var hours = clientDate.getHours()	
		var dt = (hours>=12)?"PM":"AM";
		hours = (hours%12==0)?12:(hours%12);
		var mins = clientDate.getMinutes()<10 ? "0"+clientDate.getMinutes() : clientDate.getMinutes();
		date = clientDate.getFullYear()+"-"+month+"-"+day;
		time = hours+":"+mins+" "+dt;
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
	
	var collectingServer = "http://localhost:"+electionConf["nginx-port"]+"/cs";
	//don't use port 80 if it's not deployed
	if(electionConf.deployment){
		var sAddresses = JSON.parse(sAddressesRaw);
		collectingServer = sAddresses["server-address"].collectingserver;
	}
	 
	document.getElementById("elections").innerHTML = "";
	 
	var head$ = $('<tr/>');
	head$.append($('<th style="text-align:center"/>').html(" Election IDs "));
	head$.append($('<th style="text-align:center"/>').html(" Election Title "));
	head$.append($('<th style="text-align:center"/>').html(" Starting Time "));
	head$.append($('<th style="text-align:center"/>').html(" Ending Time "));
	head$.append($('<th style="text-align:center"/>').html(" Election State "));
	$("#elections").append(head$);
  
	var electionTitles = [];
	
	for (var i = 0 ; i < elections.length ; i++) {
		var elecID = elections[i].electionID;
		var elecStatus = 'waiting...';
		var startingTime = resolveTime(elections[i].startTime)
		var endingTime = resolveTime(elections[i].endTime)
		var ELS = elections[i].ELS
		var row$ = $('<tr class="faintHover"/>');
      
		row$.append($('<td />').html(elections[i].electionID));
		row$.append($('<td />').html(escapeHTML(elections[i].electionTitle, true)));
		row$.append($('<td />').html(startingTime));
		row$.append($('<td />').html(endingTime));
		row$.append($('<td id='+elecID+'/>').html(elecStatus));
		$("#elections").append(row$);
      
		setTimeout(getElectionStatus(elecID, ELS, function (eleID, ELS, stat){
			document.getElementById(eleID).innerHTML = stat;
		}),3000);
        
	}     
  
  function getElectionStatus(eleID, ELS, callback) {
      // Detemine the status of the system: (not-yet) open/closed, 
      // by quering the collecting server.
      // Depending on the state, either the voting tab or the
      // verification tab will be opened.
      //
      // The state is detemined in a (too?) simple way, by
      // checking if the final server has ready result.
      //

 	 var stat = 'what';
 	 var url = collectingServer+'/'+ELS+'/status';
      $.get(url)
       .fail(function () { 
          //var stat = 'no response';
    	  var stat = 'waiting...';
          callback(eleID, ELS, stat)
        })
       .done(function (result) {  // we have some response
          var stat = result.status;
          callback(eleID, ELS, stat)
        });

  }
  
  ////////////////////////////////////////////////////////////////
  ///////// Refresh State
  
	/* Refresh */
  var electionStates = window.setInterval(function() {
 	 for (var i = 0 ; i < elections.length ; i++) {
     	 var elecID = elections[i].electionID;
     	 var ELS = elections[i].ELS;
     	 getElectionStatus(elecID, ELS, function (eleID, ELS, stat){
     		 document.getElementById(eleID).innerHTML = stat;
     	 });
 	 }
  }, 3000);
  
  $('#welcome').show();
  
  res(electionStates);
  
}
String.prototype.width = function(font) {
	  var f = font || '12px arial',
	      o = $('<div>' + this + '</div>')
	            .css({'position': 'absolute', 'float': 'left', 'white-space': 'nowrap', 'visibility': 'hidden', 'font': f})
	            .appendTo($('body')),
	      w = o.width();

	  o.remove();

	  return w;
	}	
