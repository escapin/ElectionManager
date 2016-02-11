function electionButtons() {
	
	
    //////////////////////////////////////////////////////////////////////////////
	/// PAGE 1
	
	var electionConf = JSON.parse(electionConfigRaw);	 
	var elections = electionConf.elections;
	
	/* Create 'click' event handler for rows */
    var rows = $('tr').not(':first');
    var row;
    var value;
    
	/* Send signal to node server */
	var config = JSON.parse(configRaw);
	var port = config.port;
	var address = config.address;
	
	////////////////////////////////////////////////////////////////////////
	
	function reloading(){
		electionConf = JSON.parse(electionConfigRaw);	 
		elections = electionConf.elections;
		
		/* Create 'click' event handler for rows */
	    rows = $('tr').not(':first');
	    row;
	    value;
	    
		/* Send signal to node server */
		config = JSON.parse(configRaw);
		port = config.port;
		address = config.address;
		
		
		rows.on('click', function(e) {
	        
	        row = $(this);
	        
	        rows.removeClass('highlight');
	        row.addClass('highlight');
	        
	        value = $(this).text().trim();  
	        value = value.substring(0, 5);
	    });
	    
	    $(document).bind('selectstart dragstart', function(e) { 
	        e.preventDefault(); 
	        return false; 
	    });
	}
	
	function alerting(data){
		$('#showing').html(data);
		document.getElementById("alertfield").style.visibility = "visible";
	}

	$("#reload").click(function() {
		reload_js("js/ElectionConfigFile.js");
		document.getElementById("alertfield").style.visibility = "hidden";
		buildElectionTable();
		reloading();
	});
	
    function reload_js(src) {
        $('script[src="' + src + '"]').remove();
        $('<script>').attr('src', src).appendTo('head');
    }
	
    ///////////////////////////////////////////////////////////////////////////
    
	function simpleElection(rand) {
		disableButtons();
		$('#processing').fadeIn(150);
		$.post(address+":"+port+"/election", {task: "simple", ID: "generated", random: rand, title: "", description: ""})
		 .done(function(data){
			$('#processing').fadeOut(150);
			if (data == "created") {
				reload_js("js/ElectionConfigFile.js");
				buildElectionTable();
				reloading();
				$('#processing').hide();
				enableButtons();
			}
			else{
				alerting(data);
				$('#processing').hide();
				enableButtons();
			}
		  })
		 .fail(function(){
			 $('#processing').hide();
			 enableButtons();
			 alerting('cannot connect to ElectionHandler at '+ address+":"+port+"/election");
		 });
	}
	
	function removeElection(pass) {
		if(value == null){
    		alert("no election selected");
    	}
    	else{
    		disableButtons();
    		$('#processing').fadeIn(150);
    		$.post(address+":"+port+"/election", {task: "remove", ID: value, password: pass})
    		 .done(function(data){
    			$('#processing').fadeOut(150);
    			if (data == "removed") {
    				reload_js("js/ElectionConfigFile.js");
    				buildElectionTable();
    				reloading();
    				$('#processing').hide();
    				enableButtons();
    			}
    			else{
    				alerting(data);
    				$('#processing').hide();
    				enableButtons();
    			}
    		  })
    		 .fail(function(){
    			 $('#processing').hide();
    			 enableButtons();
    			 alerting('cannot connect to ElectionHandler at '+ address+":"+port+"/election");
    		 });
    	}
	}
    
    //////////////////////////////////////////////////////////////////////////////
    /// PAGE 2
    
	
    function enableWhenNotEmpty(button) {
        return function() {
        	var ename = $('#e-name').val();
        	var description = $('#e-desc').val();
            var stime = $('#start-time').val();
            var etime = $('#end-time').val();
            if( ename==='' || description==='')
            	button.prop('disabled', true);            
            else {
            	if( stime==='' && etime!=='')
                    button.prop('disabled', true);
                else if( stime!=='' && etime==='')
                	button.prop('disabled', true);
                else if( stime!==''){
                	if (validTime(stime) && validTime(etime))
                		button.prop('disabled', null);
                	else{
                		button.prop('disabled', true);
                	}
                }
                else{
                	button.prop('disabled', null);
                }
            }
        };
    }	
    
    
    function advancedElection() {
    	disableButtons();
		var ename = $('#e-name').val();
		var edesc = $('#e-desc').val();
		var startingTime = $('#start-time').val();
		var endingTime = $('#end-time').val();
		$('#processing').fadeIn(150);
		$.post(address+":"+port+"/election", {task: "advanced", ID: "generated", title: ename, description: edesc, startTime: startingTime, endTime: endingTime})
		 .done(function(data){
			$('#processing').fadeOut(150);
			if (data == "created") {
				reload_js("js/ElectionConfigFile.js");
				buildElectionTable();
				reloading();
				$('#processing').hide();
				enableButtons();
				$('#advanced').fadeOut(150);
				$('welcome').show();
			}
			else{
				alerting(data);
				$('#processing').hide();
				enableButtons();
			}
		  })
		 .fail(function(){
			 $('#processing').hide();
			 enableButtons();
			 alerting('cannot connect to ElectionHandler at '+ address+":"+port+"/election");
		 });
    }
	
    
    ////////////////////////////////////////////////////////////////////////////////
    // Page 3
    
	var nchoices = 2;
		
	function addChoice(){
		nchoices = nchoices + 1;
		document.getElementById("c-list").innerHTML+='<input id="choice'+nchoices+'" class="pure-input-1" type="text" size="50" placeholder="choice '+nchoices+'">';
		document.getElementById("c-list").innerHTML+='<div class="extra-info"></div>';
		if(nchoices > 2){
			$("#remove-choice").prop('disabled', null);
		}
		document.getElementById('choice'+nchoices).focus();
		document.getElementById('add-choice').setAttribute("style",
                "margin-top:"+(48.8*(nchoices-1)).toString()+"px");
	}
	
	function removeChoice(){
		if(nchoices > 2){
			var elem = document.getElementById("choice"+nchoices);
			elem.parentElement.removeChild(elem);
			nchoices = nchoices - 1;
		}
		if(nchoices <= 2){
			$("#remove-choice").prop('disabled', true);
		}
		document.getElementById('add-choice').setAttribute("style",
                "margin-top:"+(48.8*(nchoices-1)).toString()+"px");
	}
	
    function enableWhenNotEmptyChoices(button) {
        return function() {
        	var equestion = $('#e-question').val();
        	var echoice1 = $('#choice1').val();
            var echoice2 = $('#choice2').val();
            if( equestion==='' || echoice1==='' || echoice2==='')
            	button.prop('disabled', true);            
            else {
                button.prop('disabled', null);
            }
        };
    }
	
    function completeElection(pass) {
    	disableButtons();
		var ename = $('#e-name').val();
		var edesc = $('#e-desc').val();
		var startingTime = $('#start-time').val();
		var endingTime = $('#end-time').val();
		var equestion = $('#e-question').val();
		var electionCh = {};
		var echoices = [];
		for(i = 1; i <= nchoices; i++){
			echoices.push($('#choice'+i).val());
		}
		electionCh.choices = echoices;
		$('#processing').fadeIn(150);
		$.post(address+":"+port+"/election", {task: "complete", ID: "generated", title: ename, description: edesc, startTime: startingTime, endTime: endingTime, question: equestion, choices: echoices, password: pass})
		 .done(function(data){
			$('#processing').fadeOut(150);
			if (data == "created") {
				reload_js("js/ElectionConfigFile.js");
				buildElectionTable();
				reloading();
				$('#processing').hide();
				enableButtons();
				$('#complete').fadeOut(150);
				$('welcome').show();
			}
			else{
				alerting(data);
				$('#processing').hide();
				enableButtons();
			}
		  })
		 .fail(function(){
			 $('#processing').hide();
			 enableButtons();
			 alerting('cannot connect to ElectionHandler at '+ address+":"+port+"/election");
		 });
    }
    
    ////////////////////////////////////////////////////////////////
    /// Button Handlers
	
    /* Vote Button */
    $("#vote").click(function() {
    	if(value == null){
    		alert("no election selected");
    	}
    	else{
			window.location.href = address+"/"+value+"/votingBooth";
		}
	});
	
	/* Close Button */
    $("#close").click(function() {
    	if(value == null){
    		alert("no election selected");
    	}
    	else{
			window.location.href = address+"/"+value+"/collectingServer/admin/close";
		}
	});
    
	/* Create Buttons */
	$("#create").click(function() {
		askRandom();
	});
	
	$("#adv-create").click(function() {
		advancedElection();
	});
	
	$("#compl-create").click(function() {
		overlay("complete");
	});

	/* Remove Button */
	$("#remove").click(function() {
    	//overlay("remove");
		verifylayer();
	});
    
	
    /* Advanced Button */
	$("#advance").click(function() {
		$('#welcome').hide(150);
	    $('#advanced').show(150);
	});
	
	$("#next-adv").click(function() {
		$('#advanced').hide(150);
	    $('#complete').show(150);
	});

    /* Back Button */
	$("#back").click(function() {
		$('#advanced').hide(150);
	    $('#welcome').show(150);
	});

	$("#back2").click(function() {
		$('#complete').hide(150);
	    $('#advanced').show(150);
	});
	
	/* Choice buttons */
	$("#add-choice").click(function() {
		addChoice();
	});
	
	$("#remove-choice").click(function() {
		removeChoice();
	});
	
    ////////////////////////////////////////////////////////////////
    /// Other Handlers
	
	var isInt = function(n){
		return n % 1 === 0;
	}
	
	/* Validate Time */
	var validTime = function(ttime){
		var stime = ttime.split(" ");
		if(stime.length != 3){
			//console.log("basically wrong");
			return false;
		}
		var date = stime[0].split(".");
		var time = stime[1].split(":");
		var zone = stime[2].split("+");
		if(date.length !== 3 || time.length !== 2 || zone.length !== 2){
			//console.log("wrong length");
			return false;
		}
		//console.log("works so far1");
		for (var i = 0; i < 3; i++){
			if (!isInt(date[i])){
				//console.log("not int");
				return false;
			}
		}
		for (var i = 0; i < 2; i++){
			if (!isInt(time[i])){
				//console.log("not int2");
				return false;
			}
		}
		//console.log("works so far2");
		if(date[0] < 0 || date[1] < 0 || date[1] > 12 || date[2] < 0 || date[2] > 31){
			//console.log("wrong numbers");
			return false;
		}
		if(time[0] < 0 || time[0] > 23 || time[1] < 0 || time[1] > 59){
			//console.log("wrong numbers2");
			return false;
		}
		//console.log("works so far3");
		if(!zone[0].match(/[A-Z]{3}/)){
			//console.log("wrong matching");
			return false;
		}
		if(!zone[1].match(/[0-9]{4}/)){
			//console.log("wrong matching2");
			return false;
		}
		//console.log("done all");
		return true;
	}
	
	/* Disable Buttons */
	function disableButtons(){
		$("#vote").prop('disabled', true);
		$("#close").prop('disabled', true);
		$("#create").prop('disabled', true);
		$("#remove").prop('disabled', true);
		$("#advance").prop('disabled', true);
		$("#next-adv").prop('disabled', true);
		$("#back").prop('disabled', true);
		$("#back2").prop('disabled', true);
		$("#adv-create").prop('disabled', true);
		$("#compl-create").prop('disabled', true);
	}

	function enableButtons(){
		$("#vote").prop('disabled', null);
		$("#close").prop('disabled', null);
		$("#create").prop('disabled', null);
		$("#remove").prop('disabled', null);
		$("#advance").prop('disabled', null);
		$("#next-adv").prop('disabled', true);
		$("#back").prop('disabled', true);
		$("#back2").prop('disabled', true)
		$("#adv-create").prop('disabled', null);
		$("#compl-create").prop('disabled', null);
	}
	
	
	
    $('#e-name').on('input', enableWhenNotEmpty($('#adv-create')));
    $('#e-desc').on('input', enableWhenNotEmpty($('#adv-create')));    
    $('#start-time').on('input', enableWhenNotEmpty($('#adv-create')));
    $('#end-time').on('input', enableWhenNotEmpty($('#adv-create')));
    
    $('#e-name').on('input', enableWhenNotEmpty($('#next-adv')));
    $('#e-desc').on('input', enableWhenNotEmpty($('#next-adv')));    
    $('#start-time').on('input', enableWhenNotEmpty($('#next-adv')));
    $('#end-time').on('input', enableWhenNotEmpty($('#next-adv')));
    
    $('#e-question').on('input', enableWhenNotEmptyChoices($('#compl-create')));
    $('#choice1').on('input', enableWhenNotEmptyChoices($('#compl-create')));
    $('#choice2').on('input', enableWhenNotEmptyChoices($('#compl-create')));
    
    
    rows.on('click', function(e) {
        
        row = $(this);
        
        rows.removeClass('highlight');
        row.addClass('highlight');
        
        value = $(this).text().trim();  
        value = value.substring(0, 5);
    });
    
    $(document).bind('selectstart dragstart', function(e) { 
        e.preventDefault(); 
        return false; 
    });
    
    ////////////////////////////////////////////////////////////////////////////
    // Password overlay
    
    function overlay(etype) {
    	el = document.getElementById("newPass");
    	el.style.visibility = (el.style.visibility == "visible") ? "hidden" : "visible";
    	document.getElementById("mod").value = etype;
    	document.getElementById("cr-pass1").focus();
    }
    
    $("#ok-ov").click(function() {
    	createPass();
	});
    
    $("#cancel-ov").click(function() {
    	overlay("");
		document.getElementById("cr-pass1").value = "";
		document.getElementById("cr-pass2").value = "";
    });
    
    function createPass(){
    	if($("#cr-pass1").val()===$("#cr-pass2").val()){
    		var temp = document.getElementById("cr-pass1").value;
			document.getElementById("cr-pass1").value = "";
			document.getElementById("cr-pass2").value = "";
			switch(document.getElementById("mod").value){
    		case "simple":
    			overlay("");
    			simpleElection(temp);
    			break;
    		case "advanced":
    			overlay("");
    			advancedElection(temp);
    			break;
    		case "complete":
    			overlay("");
    			completeElection(temp);
    			break;
    		case "remove":
    			overlay("");
    			removeElection(temp);
    			break;
    		default:
    			alert("this shouldn't happen, mode is " + document.getElementById("mod").value);
    		}
    	}
    	else{
			document.getElementById("cr-pass1").value = "";
			document.getElementById("cr-pass2").value = "";
    		alert("Passwords do not match");
    	}
    }
    
    
    $("#ok-pass").click(function() {
    	verifyPass();
	});
    
    $("#cancel-pass").click(function() {
    	el = document.getElementById("askPass");
		el.style.visibility = "hidden";
		document.getElementById("e-pass").value = "";
    });
    
    function verifyPass(){
    	var temp = document.getElementById("e-pass").value;
		document.getElementById("e-pass").value = "";
		el = document.getElementById("askPass");
		el.style.visibility = "hidden";
		removeElection(temp);
    }
    
    function verifylayer() {
    	if(value == null){
    		alert("no election selected");
    	}
    	else{
    		var i = 0;
    		for(i = 0; i < elections.length ; i++) {
    			if(elections[i].electionID == value){
    				break;
    			}
    		}
    		if(elections[i].protect){
    			el = document.getElementById("askPass");
    			el.style.visibility = "visible";
    			document.getElementById("e-pass").focus();
    		}
    		else{
    			removeElection("");
    		}
    	}
    }
    
    ////////////////////////////////////////////////////////////////////////////
    // Random overlay
    
    function askRandom() {
		el = document.getElementById("userRandom");
		el.style.visibility = "visible";
		document.getElementById("u-norm").focus();
    }
	
	$("#u-rand").click(function() {
		simpleElection(true);
		el = document.getElementById("userRandom");
		el.style.visibility = "hidden";
	});
	
	$("#u-norm").click(function() {
		simpleElection(false);
		el = document.getElementById("userRandom");
		el.style.visibility = "hidden";
	});
    
	
}

////////////////////////////////////////////////////////////////////////////////////////////////////////////
//////////Builds the HTML Table from ElectionIDs

function buildElectionTable() {
	 
	 var configs = JSON.parse(configRaw);
	 var host = configs.address;
	 var electionConf = JSON.parse(electionConfigRaw);	 
	 var elections = electionConf.elections;
	 	 
	 document.getElementById("elections").innerHTML = "";
	 
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




