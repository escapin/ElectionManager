function electionButtons() {
	
	var electionConf;
	var votingBooth;
	var collectingServer;
	var lastMix;
	var elections;

	var electionManager;
	var protocol;
	
	/* Create 'click' event handler for rows */
    var rows;
    var row;
    var value;
	var task;
    
	var elecType = "none";
	var buttonEnable = null;
	var votingStatus = null;
	var electionStatus = null;
	/* Ensure the table is always up to date */
	window.onload = function(){reloading();}
    
	//////////////////////////////////////////////////////////////////////////////
	/// PAGE 1
	
	function simpleElection(rand) {
		disableButtons();
		$('#processing').fadeIn(150);
		$.post(electionManager+"/election", {task: "simple", ID: "generated", random: rand, title: "", description: ""})
		 .done(function(data){
			$('#processing').fadeOut(150);
			enableButtons();
			if (data == "created") {
				value = null;
				reloading();
				$('#processing').hide();
			}
			else{
				alerting(data);
				$('#processing').hide();
			}
		  })
		 .fail(function(){
			 enableButtons();
			 $('#processing').hide();
			 alerting('cannot connect to ElectionHandler at '+ electionManager);
		 });
	}
	
	function removeElection(pass) {
		if(value == null){
    		alerting("no election selected");
    	}
    	else{
    		disableButtons();
    		$('#processing').fadeIn(150);
    		$.post(electionManager+"/election", {task: "remove", ID: value, password: pass})
    		 .done(function(data){
    			$('#processing').fadeOut(150);
    			enableButtons();
    			if (data == "removed") {
    				window.clearInterval(votingStatus);
    				value = null;
    				reloading();
    				$('#processing').hide();
    			}
    			else{
    				alerting(data);
    				$('#processing').hide();
    			}
    		  })
    		 .fail(function(){
    			 enableButtons();
    			 $('#processing').hide();
    			 alerting('cannot connect to ElectionHandler at '+ electionManager);
    		 });
    	}
	}
	
	function closeElection(pass) {
		if(value == null){
    		alerting("no election selected");
    	}
    	else{
    		disableButtons();
    		$('#processing').fadeIn(150);
    		$.get(protocol+"admin:"+pass+"@"+collectingServer+"/"+value+"/collectingServer/admin/close")
    		 .done(function(data){
    			enableButtons();
    			$('#processing').fadeOut(150);
    			if(!data.ok){
    				alerting("election already closed", false);
    			}
    		  })
    		 .fail(function(data){
    			enableButtons();
    			$('#processing').hide();
    			if(data===undefined){
    				alerting("cannot connect to CollectingServer at "+ collectingServer, false);
    			}
    			else{
    				alerting("wrong password", false);
    			}
    		 });
    		enableButtons();
    	}
	}
    
    //////////////////////////////////////////////////////////////////////////////
    /// PAGE 2
    
	
    function enableWhenNotEmpty(button) {
        return function() {
        	var ename = $('#e-name').val();
        	var description = $('#e-desc').val();
        	var sdate = $('#s-date').val();
        	var edate = $('#e-date').val();
            var stime = $('#s-time').val();
            var etime = $('#e-time').val();
            var starttime = sdate + " " + stime + " GMT+0100";
            var endtime = edate + " " + etime + " GMT+0100";
            if( ename==='' || description==='')
            	button.prop('disabled', true);            
            else {
            	if( starttime==='' && endtime!=='')
                    button.prop('disabled', true);
                else if( starttime!=='' && endtime==='')
                	button.prop('disabled', true);
                else if( starttime!==''){
                	if (validTime(starttime) && validTime(endtime))
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
		$.post(electionManager+"/election", {task: "advanced", ID: "generated", title: ename, description: edesc, startTime: startingTime, endTime: endingTime})
		 .done(function(data){
			$('#processing').fadeOut(150);
			enableButtons();
			if (data == "created") {
				value = null;
				reloading();
				$('#processing').hide();
				$('#advanced').fadeOut(150);
				$('welcome').show();
			}
			else{
				alerting(data);
				$('#processing').hide();
			}
		  })
		 .fail(function(){
			 enableButtons();
			 $('#processing').hide();
			 alerting('cannot connect to ElectionHandler at '+ electionManager);
		 });
    }
	
    
    ////////////////////////////////////////////////////////////////////////////////
    // Page 3
    
	var nchoices = 2;
		
	function addChoice(){
		nchoices = nchoices + 1;
		
		//save inputs
		var str = "";
		for(var i = 3; i < nchoices; i++){
			str += $('#choice'+(i)).val() + " ";
		}
		
		//add new question
		if(nchoices === 3){
			document.getElementById("c-list").innerHTML+='<input id="choice'+nchoices+'" class="pure-input-1" type="text" size="50" placeholder="choice '+nchoices+'">';		
		}
		else{
			document.getElementById("c-list").innerHTML+='<input id="choice'+nchoices+'" class="pure-input-1" type="text" size="50" style="margin-top: 1.3em;" placeholder="choice '+nchoices+'">';		
		}
		//insert previous inputs
		str = str.split(" ");
		for(var i = 3; i < nchoices; i++){
			document.getElementById("choice"+(i)).value = str[i-3];
		}
		if(nchoices > 2){
			$("#remove-choice").prop('disabled', null);
		}
		document.getElementById('choice'+nchoices).focus();
		//document.getElementById('add-choice').setAttribute("style",
        //        "margin-top:"+(19.2*(nchoices-1)).toString()+"%");
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
		//document.getElementById('add-choice').setAttribute("style",
        //        "margin-top:"+(48.8*(nchoices-1)).toString()+"px");
	}
	
    function enableWhenNotEmptyChoices(button) {
        return function() {
        	var equestion = $('#e-question').val();
        	//var echoice1 = $('#choice1').val();
            //var echoice2 = $('#choice2').val();
            //if( equestion==='' || echoice1==='' || echoice2==='')
            //	button.prop('disabled', true);            
            //else {
              //  button.prop('disabled', null);
            //}
            var filled = true;
            for(var i = 1; i <= nchoices; i++){
            	if($("#choice"+nchoices).val()===''){
            		filled = false;
            	}
            }
            if(filled && equestion!==''){
            	button.prop('disabled', null);
            }
            else{
            	button.prop('disabled', true);
            }
        };
    }
	
    function completeElection(pass, rand) {
    	window.clearInterval(buttonEnable);
    	disableButtons();
    	var listVoters = document.getElementById("listVoters").checked;
    	changeCulture("de-DE");
		var ename = $('#e-name').val();
		var edesc = $('#e-desc').val();
    	var sdate = $('#s-date').val();
    	var edate = $('#e-date').val();
        var stime = $('#s-time').val();
        var etime = $('#e-time').val();
        changeCulture($( "#culture" ).val());
        var startingTime = sdate + " " + stime + " GMT+0100";
        var endingTime = edate + " " + etime + " GMT+0100";
		var equestion = $('#e-question').val();
		var electionCh = {};
		var echoices = [];
		for(i = 1; i <= nchoices; i++){
			echoices.push($('#choice'+i).val());
		}
		electionCh.choices = echoices;
		$('#processing').fadeIn(150);
		$.post(electionManager+"/election", {task: "complete", ID: "generated", random: rand, title: ename, description: edesc, startTime: startingTime, endTime: endingTime, question: equestion, choices: echoices, password: pass, publishVoters: listVoters})
		 .done(function(data){
			$('#processing').fadeOut(150);
			enableButtons();
			if (data == "created") {
				value = null;
				reloading();
				$('#complete').hide(150);
				$('#processing').hide();
			}
			else{
				alerting(data, false);
				$('#processing').hide();
			    buttonEnable = window.setInterval(enableWhenNotEmptyChoices($('#compl-create')), 100);
			}
		  })
		 .fail(function(){
			 enableButtons();
			 $('#processing').hide();
			 alerting('cannot connect to ElectionHandler at '+ electionManager, false);
			 buttonEnable = window.setInterval(enableWhenNotEmptyChoices($('#compl-create')), 100);
		 });
    }
    
    ////////////////////////////////////////////////////////////////
    /// Button Handlers
	
    $('#welcome').click(function(event) { 
        if(!$(event.target).closest('tr').length &&
           !$(event.target).is('tr')&&
           !$(event.target).is('#vote')&&
           !$(event.target).is('#close')&&
           !$(event.target).is('#remove')&&
           !$(event.target).is('#help')){
        	
        	row = null;
        	value = null;
        	rows.removeClass('highlight');
        	$("#vote").prop('disabled', true);
    		$("#close").prop('disabled', true);
    		$("#remove").prop('disabled', true);
    		document.getElementById("vote").style.visibility = "hidden";
			window.clearInterval(votingStatus);
        }        
    })
    
    /* Vote Button */
    $("#vote").click(function() {
    	if(value == null){
    		alerting("no election selected");
    	}
    	else{
    		//window.location.href = votingBooth+"/"+value+"/votingBooth/";
    		getElectionStatus(value, function (eleID, stat){
    			if(stat === "open"){
    				document.getElementById("inviteVoters").style.visibility = "visible";
    	    		document.getElementById("votePage").href = votingBooth+"/"+value+"/votingBooth/";
    	    		document.getElementById("votePage").innerHTML = votingBooth+"/"+value+"/votingBooth/";
    			}
    			else if(stat === "closed"){
    				document.getElementById("checkResult").style.visibility = "visible";
    	    		document.getElementById("resultPage").href = votingBooth+"/"+value+"/votingBooth/";
    	    		document.getElementById("resultPage").innerHTML = votingBooth+"/"+value+"/votingBooth/";
    			}
    			else{
    				alerting("Server is not responding");
    			}
    	 	 });
		}
	});
	
	/* Close Button */
    $("#close").click(function() {
    	if(value == null){
    		alerting("no election selected");
    	}
    	else{
			//window.location.href = collectingServer+"/"+value+"/collectingServer/admin/close";
			document.getElementById("electionClose").style.visibility = "visible";
		}
	});
    
	/* Create Buttons */
	$("#mock").click(function() {
		//askRandom("simple");
		simpleElection(false);
	});
	
	$("#adv-create").click(function() {
		advancedElection();
	});
	
	$("#compl-create").click(function() {
		//askRandom("complete");
		overlay(document.getElementById("urandom").checked);
	});

	/* Remove Button */
	$("#remove").click(function() {
    	//overlay("remove");
		//verifylayer();
		document.getElementById("electionDelete").style.visibility = "visible";
	});
    
    /* Advanced Button */
	$("#advance").click(function() {
		$('#welcome').hide(150);
	    $('#advanced').show(150);
	    buttonEnable = window.setInterval(enableWhenNotEmpty($('#next-adv')), 100);
	});
	
	$("#next-adv").click(function() {
		$('#advanced').hide(150);
	    $('#complete').show(150);
	    window.clearInterval(buttonEnable);
	    buttonEnable = window.setInterval(enableWhenNotEmptyChoices($('#compl-create')), 100);
	});

    /* Back Button */
	$("#back").click(function() {
		$('#advanced').hide(150);
	    $('#welcome').show(150);
	    window.clearInterval(buttonEnable);
	});

	$("#back2").click(function() {
		$('#complete').hide(150);
	    $('#advanced').show(150);
	    window.clearInterval(buttonEnable);
	    buttonEnable = window.setInterval(enableWhenNotEmpty($('#next-adv')), 100);
	});
	
	/* Choice buttons */
	$("#add-choice").click(function() {
		addChoice();
	});
	
	$("#remove-choice").click(function() {
		removeChoice();
	});
	
	/* Show infopage */
	$("#help").click(function() {
		document.getElementById("infopage").style.visibility = "visible";
		$("#closehelp").focus();
	});
	
	/* Close infopage */
	$("#closehelp").click(function() {
		document.getElementById("infopage").style.visibility = "hidden";
	});

	/* Close alertfield and reload configurations */
	$("#reload").click(function() {
		document.getElementById("alertfield").style.visibility = "hidden";
		for (var i = 1; i < rows.length; i++){
	        window.clearInterval(i);
		}
		if($('#do-reload').html()==="true"){
			reloading();
		}
	});

	/* Close VotingBooth link */
	$("#closeInvite").click(function() {
		document.getElementById("inviteVoters").style.visibility = "hidden";
	});
	$("#closeCheck").click(function() {
		document.getElementById("checkResult").style.visibility = "hidden";
	});
	
	/* Confirm page for closing election */
	$("#cancelClose").click(function() {
		document.getElementById("electionClose").style.visibility = "hidden";
	});
	$("#confirmClose").click(function() {
		document.getElementById("electionClose").style.visibility = "hidden";
		verifylayer("close");
	});
	/* Confirm page for deleting election */
	$("#cancelDelete").click(function() {
		document.getElementById("electionDelete").style.visibility = "hidden";
	});
	$("#confirmDelete").click(function() {
		document.getElementById("electionDelete").style.visibility = "hidden";
		verifylayer("remove");
	});
	
	this.winOpen = function(){
        window.open(collectingServer+"/"+value+"/collectingServer/admin/close");
    	document.getElementById("electionClose").style.visibility = "hidden";
    }
	
    ////////////////////////////////////////////////////////////////
    /// Other Handlers
	
	/* Show alert message */
	function alerting(data, reloads){
		if(!(reloads===false)){
			reloads = true;
		}
		$('#showing').html(data);
		$('#do-reload').html(String(reloads));
		document.getElementById("alertfield").style.visibility = "visible";
	}
	
	/* Reload a sourcefile */
    function reload_js(src) {
        $('script[src="' + src + '"]').remove();
        $('<script>').attr('src', src).appendTo('head');
    }
	
    /* Return true if integer */
	var isInt = function(n){
		return n % 1 === 0;
	}
	
	/* Validate date and time */
	var validTime = function(ttime){
		var stime = ttime.split(" ");
		if(!(stime.length === 3 || stime.length === 4)){
			return false;
		}
		var date = stime[0].split(".");
		var time = stime[1].split(":");
		var zone = stime[stime.length-1].split("+");
		if(stime.length > 3){
			var noon = stime[2];
			if(!(noon === "AM" || noon === "PM")){
				return false;
			}
		}
		if(date.length !== 3 || time.length !== 2 || zone.length !== 2){
			return false;
		}
		for (var i = 0; i < 3; i++){
			if (!isInt(date[i])){
				return false;
			}
		}
		for (var i = 0; i < 2; i++){
			if (!isInt(time[i])){
				return false;
			}
		}
		if(date[0] < 0 || date[1] < 0 || date[1] > 12 || date[2] < 0 || date[2] > 31){
			return false;
		}
		if(time[0] < 0 || time[0] > 23 || time[1] < 0 || time[1] > 59){
			return false;
		}
		if(!zone[0].match(/[A-Z]{3}/)){
			return false;
		}
		if(!zone[1].match(/[0-9]{4}/)){
			return false;
		}
		return true;
	}
	
	/* Disable Buttons */
	function disableButtons(){
		$("#vote").prop('disabled', true);
		$("#close").prop('disabled', true);
		$("#mock").prop('disabled', true);
		$("#remove").prop('disabled', true);
		$("#advance").prop('disabled', true);
		$("#next-adv").prop('disabled', true);
		$("#back").prop('disabled', true);
		$("#back2").prop('disabled', true);
		$("#adv-create").prop('disabled', true);
		$("#compl-create").prop('disabled', true);
	}

	/* Enable Buttons */
	function enableButtons(){
		$("#vote").prop('disabled', null);
		$("#close").prop('disabled', null);
		$("#mock").prop('disabled', null);
		$("#remove").prop('disabled', null);
		$("#advance").prop('disabled', null);
		$("#next-adv").prop('disabled', null);
		$("#back").prop('disabled', null);
		$("#back2").prop('disabled', null);
		$("#adv-create").prop('disabled', null);
		$("#compl-create").prop('disabled', null);
	}
	
	/* Load configs and enable selecting rows */
	function reloading(){
		value = null;
		$("#vote").prop('disabled', true);
		$("#close").prop('disabled', true);
		$("#remove").prop('disabled', true);
		document.getElementById("vote").style.visibility = "hidden";
		
		reload_js("js/ElectionConfigFile.js");

		 window.clearInterval(electionStatus);
	     buildElectionTable(function (electionStates){
	  		 electionStatus = electionStates;
	  	 });
	     
		electionConf = JSON.parse(electionConfigRaw);
		elections = electionConf.elections;
	    
		electionManager = "http://localhost:"+electionConf["nginx-port"]+"/electionManager";
		votingBooth = "http://localhost:"+electionConf["nginx-port"];
		collectingServer = "http://localhost:"+electionConf["nginx-port"];
		lastMix = "http://localhost:"+electionConf["nginx-port"];
		
		//don't use port 80 if it's not deployed
		 if(electionConf.deployment === true){
			 var sAddresses = JSON.parse(sAddressesRaw);
			 electionManager = sAddresses.electionHandler;
			 votingBooth = sAddresses["server-address"].votingbooth;
			 collectingServer = sAddresses["server-address"].collectingserver;
			 lastMix = sAddresses["server-address"].mix2;
		 }
		var tmp = collectingServer.split("://");
		if(tmp.length > 1){
			protocol = tmp[0]+"://";
			collectingServer = tmp[1];
		}
		else{
			protocol = '';
			collectingServer = tmp[0]
		}
			/* Create 'click' event handler for rows */
	    rows = $('tr').not(':first');

	    rows.on('click', function(e) {
	        row = $(this);
	        
	        rows.removeClass('highlight');
	        row.addClass('highlight');
	        
	        value = $(this).text().trim().split(" ")[0]; 
	        
			$("#remove").prop('disabled', null);
			
			// Show Invite Voters or Check Result button
			// (depending on election state) and retest every second
			window.clearInterval(votingStatus);
			showVotingState(value);
		    votingStatus = window.setInterval(function() {
		    	showVotingState(value);
		     }, 1000);
		    
	        
	    });
	    
	    $('#welcome').bind('selectstart dragstart', function(e) { 
	        e.preventDefault(); 
	        return false; 
	    });
	}

    ////////////////////////////////////////////////////////////////////////////
    // Password overlay
    
    $("#ok-ov").click(function() {
    	createPass("complete", document.getElementById("mod").value);
	});
    
    $("#cancel-ov").click(function() {
    	overlay("");
		document.getElementById("cr-pass1").value = "";
		document.getElementById("cr-pass2").value = "";
    });
    
    $("#ok-pass").click(function() {
    	verifyPass(task);
    	task = null;
	});
    
    $("#cancel-pass").click(function() {
    	el = document.getElementById("askPass");
		el.style.visibility = "hidden";
		document.getElementById("e-pass").value = "";
    });
    
    function overlay(rand) {
    	el = document.getElementById("newPass");
    	el.style.visibility = (el.style.visibility == "visible") ? "hidden" : "visible";
    	document.getElementById("mod").value = rand;
    	document.getElementById("cr-pass1").focus();
    }
    
    function createPass(type, rand){
    	if($("#cr-pass1").val()===$("#cr-pass2").val()){
    		var temp = document.getElementById("cr-pass1").value;
			document.getElementById("cr-pass1").value = "";
			document.getElementById("cr-pass2").value = "";
			switch(type){
    		case "simple":
    			overlay("");
    			simpleElection(rand);
    			break;
    		case "advanced":
    			overlay("");
    			advancedElection(temp);
    			break;
    		case "complete":
    			overlay("");
    			completeElection(temp, rand);
    			break;
    		case "remove":
    			overlay("");
    			removeElection(temp);
    			break;
    		default:
    			alerting("this shouldn't happen, mode is " + document.getElementById("mod").value);
    		}
    	}
    	else{
			document.getElementById("cr-pass1").value = "";
			document.getElementById("cr-pass2").value = "";
    		alerting("Passwords do not match");
    	}
    }
    
    function verifyPass(origin){
    	var temp = document.getElementById("e-pass").value;
		document.getElementById("e-pass").value = "";
		el = document.getElementById("askPass");
		el.style.visibility = "hidden";
		switch(origin){
		case "remove":
			removeElection(temp);
			break;
		case "close":
			closeElection(temp);
		}
    }
    
    function verifylayer(origin) {
    	task = origin;
    	if(value == null){
    		alerting("no election selected");
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
    			switch(origin){
        		case "remove":
        			removeElection("");
        			break;
        		case "close":
        			closeElection("");
    			}
    		}
    	}
    }
    
    ////////////////////////////////////////////////////////////////////////////
    // Random overlay
    
    function askRandom(etype) {
    	document.getElementById("mod").value = etype;
    	elecType = etype;
		el = document.getElementById("userRandom");
		el.style.visibility = "visible";
		document.getElementById("u-norm").focus();
    }
    
    function progressElection(rand){
    	type = elecType;
    	elecType = "none";
    	if(type == "complete"){
    		overlay(rand);
    	}
    	else{
    		simpleElection(rand);
    	}
    }
	
	$("#u-rand").click(function() {
		el = document.getElementById("userRandom");
		el.style.visibility = "hidden";
		progressElection(true);

	});
	
	$("#u-norm").click(function() {
		el = document.getElementById("userRandom");
		el.style.visibility = "hidden";
		progressElection(false);
	});
	
////////////////////////////////////////////////////////////////////////////////////////////////////////////
//////////Date and Time
	
	$.widget( "ui.timespinner", $.ui.spinner, {
		options: {
			// seconds
			step: 10 * 60 * 1000,
			// hours
			page: 60
		},

		_parse: function( value ) {
			if ( typeof value === "string" ) {
				// already a timestamp
				if ( Number( value ) == value ) {
					return Number( value );
				}
				return +Globalize.parseDate( value );
			}
			return value;
		},

		_format: function( value ) {
			return Globalize.format( new Date(value), "t" );
		}
	});
	
	
	
	$(function() {
		$( "#s-date" ).datepicker();
	});
	
	$(function() {
		$( "#e-date" ).datepicker();
	});

	$(function() {
		$( "#s-time" ).timespinner();
	});
    
	$(function() {
		$( "#e-time" ).timespinner();
	});
	
	//var serverTimezone = 0;
	//var clientDate = new Date();
	//var timeDifference = clientDate.getTimezoneOffset()-serverTimezone;
	//var currentDate = new Date(clientDate.setTime(clientDate.getTime()+timeDifference*60000));
	var currentDate = new Date();
	var month = currentDate.getMonth()+1<10 ? "0"+(currentDate.getMonth()+1) : (currentDate.getMonth()+1);
	var day = currentDate.getDate()+1<10 ? "0"+currentDate.getDate() : currentDate.getDate();
	
	var hours = currentDate.getHours()	
	var dt = (hours>=12)?"PM":"AM";
	hours = (hours%12==0)?12:(hours%12);
			
	document.getElementById("s-date").value = currentDate.getFullYear()+"."+month+"."+day;
	document.getElementById("s-time").value = hours+":"+currentDate.getMinutes()+" "+dt;

	var endDate = new Date(currentDate.setTime(currentDate.getTime()+10*60000));
	month = endDate.getMonth()+1<10 ? "0"+(endDate.getMonth()+1) : (endDate.getMonth()+1);
	day = endDate.getDate()+1<10 ? "0"+endDate.getDate() : endDate.getDate();
	
	hours = endDate.getHours()
	dt = (hours>=12)?"PM":"AM";
	hours = (hours%12==0)?12:(hours%12);
	
	document.getElementById("e-date").value = endDate.getFullYear()+"."+month+"."+day;
	document.getElementById("e-time").value = hours+":"+endDate.getMinutes()+" "+dt;

	
	
	var currentTime = function(){
		var currentDate = new Date();
		var month = currentDate.getMonth()+1<10 ? "0"+(currentDate.getMonth()+1) : (currentDate.getMonth()+1);
		var day = currentDate.getDate()+1<10 ? "0"+currentDate.getDate() : currentDate.getDate();
		nowDate = currentDate.getFullYear()+"."+month+"."+day;
		nowTime = currentDate.getHours()+":"+currentDate.getMinutes();
		
		return nowDate + " " + nowTime;
	}
	
	var endsTime = function(){
		var endDate = new Date(currentDate.setTime(currentDate.getTime()+10*60000));
		month = endDate.getMonth()+1<10 ? "0"+(endDate.getMonth()+1) : (endDate.getMonth()+1);
		day = endDate.getDate()+1<10 ? "0"+endDate.getDate() : endDate.getDate();
		endingDate = endDate.getFullYear()+"."+month+"."+day;
		endingTime = endDate.getHours()+":"+endDate.getMinutes();
		
		return endingDate + " " + endingTime;
	}
	
	function changeCulture(cult){
		var current = $("#s-time").timespinner("value");
		var current2 = $("#e-time").timespinner("value");
		Globalize.culture(cult);
		$( "#s-time" ).timespinner("value", current);
		$( "#e-time" ).timespinner("value", current2);
	}
	
	// Show Invite Voters or Check Result button
	// (depending on election state)
	function showVotingState(id){
		getElectionStatus(id, function (eleID, stat){
			if(stat === "open"){
		        $("#vote").prop('disabled', null);
				$("#close").prop('disabled', null);
	    		document.getElementById("vote").value = "Invite Voters to Vote";
	    		document.getElementById("vote").style.visibility = "visible";
			//console.log( $("#removeMsg").html() );
			//console.log( $("#removeOpen").html() );
			// inserting the hidden message with id='removeOpen' inside the HTML tag with id='removeMsg'
			$("#removeMsg").html( $("#removeOpen").html() );
			}
			else if(stat === "closed"){
		        $("#vote").prop('disabled', null);
				$("#close").prop('disabled', true);
	    		document.getElementById("vote").value = "Check Election Result";
	    		document.getElementById("vote").style.visibility = "visible";
			// inserting the hidden message with id='removeClosed' inside the HTML tag with id='removeMsg'
			$("#removeMsg").html( $("#removeClosed").html() );
			}
			else{
				document.getElementById("vote").style.visibility = "hidden";
			}
	 	 });
	}
	
	function getElectionStatus(eleID, callback) {
	      // Detemine the status of the system: (not-yet) open/closed, 
	      // by quering the final mix server.
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
	
}
