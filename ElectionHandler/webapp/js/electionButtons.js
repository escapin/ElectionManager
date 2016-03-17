function electionButtons() {
	
	var electionConf;	 
	var elections;
    
	var config;
	var port;
	var address;
	var host;
	
	/* Create 'click' event handler for rows */
    var rows;
    var row;
    var value;
	
	var elecType = "none";
	var buttonEnable = null;
	
	/* Ensure the table is always up to date */
	window.onload = function(){reloading();}
    
	//////////////////////////////////////////////////////////////////////////////
	/// PAGE 1
	
	function simpleElection(rand) {
		disableButtons();
		$('#processing').fadeIn(150);
		$.post(host+":"+port+"/election", {task: "simple", ID: "generated", random: rand, title: "", description: ""})
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
			 alerting('cannot connect to ElectionHandler at '+ host+":"+port+"/election");
		 });
	}
	
	function removeElection(pass) {
		if(value == null){
    		alerting("no election selected");
    	}
    	else{
    		disableButtons();
    		$('#processing').fadeIn(150);
    		$.post(host+":"+port+"/election", {task: "remove", ID: value, password: pass})
    		 .done(function(data){
    			$('#processing').fadeOut(150);
    			enableButtons();
    			if (data == "removed") {
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
    			 alerting('cannot connect to ElectionHandler at '+ host+":"+port+"/election");
    		 });
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
		$.post(host+":"+port+"/election", {task: "advanced", ID: "generated", title: ename, description: edesc, startTime: startingTime, endTime: endingTime})
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
			 alerting('cannot connect to ElectionHandler at '+ host+":"+port+"/election");
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
		$.post(host+":"+port+"/election", {task: "complete", ID: "generated", random: rand, title: ename, description: edesc, startTime: startingTime, endTime: endingTime, question: equestion, choices: echoices, password: pass, publishVoters: listVoters})
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
				alerting(data);
				$('#processing').hide();
			    buttonEnable = window.setInterval(enableWhenNotEmptyChoices($('#compl-create')), 100);
			}
		  })
		 .fail(function(){
			 enableButtons();
			 $('#processing').hide();
			 alerting('cannot connect to ElectionHandler at '+ host+":"+port+"/election");
			 buttonEnable = window.setInterval(enableWhenNotEmptyChoices($('#compl-create')), 100);
			 $('#complete').hide(150);
			 $('#welcome').show();
		 });
    }
    
    ////////////////////////////////////////////////////////////////
    /// Button Handlers
	
    /* Vote Button */
    $("#vote").click(function() {
    	if(value == null){
    		alerting("no election selected");
    	}
    	else{
    		window.location.href = address+"/"+value+"/votingBooth/";
		}
	});
	
	/* Close Button */
    $("#close").click(function() {
    	if(value == null){
    		alerting("no election selected");
    	}
    	else{
			window.location.href = address+"/"+value+"/collectingServer/admin/close";
		}
	});
    
	/* Create Buttons */
	$("#create").click(function() {
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
		verifylayer();
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
		reloading();
	});

	
    ////////////////////////////////////////////////////////////////
    /// Other Handlers
	
	/* Show alert message */
	function alerting(data){
		$('#showing').html(data);
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
		$("#create").prop('disabled', true);
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
		$("#create").prop('disabled', null);
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
		$("#vote").prop('disabled', true);
		$("#close").prop('disabled', true);
		$("#remove").prop('disabled', true);
		
		
		reload_js("js/ElectionConfigFile.js");
		buildElectionTable();
		
		electionConf = JSON.parse(electionConfigRaw);	 
		elections = electionConf.elections;
	    
		config = JSON.parse(configRaw);
		port = config.port;
		host = config.address;
		address = config.address;
		
		//don't use port 80 if it's not deployed
		 if(electionConf.deployment === false){
			 address = address+":"+electionConf["nginx-port"];
		 }
		
		/* Create 'click' event handler for rows */
	    rows = $('tr').not(':first');
		
		rows.on('click', function(e) {
	        row = $(this);
	        
	        rows.removeClass('highlight');
	        row.addClass('highlight');
	        
	        value = $(this).text().trim().split(" ")[0]; 
	        
	        $("#vote").prop('disabled', null);
			$("#close").prop('disabled', null);
			$("#remove").prop('disabled', null);
	        
	    });
	    
	    $(document).bind('selectstart dragstart', function(e) { 
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
    	verifyPass();
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
    
    function verifyPass(){
    	var temp = document.getElementById("e-pass").value;
		document.getElementById("e-pass").value = "";
		el = document.getElementById("askPass");
		el.style.visibility = "hidden";
		removeElection(temp);
    }
    
    function verifylayer() {
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
    			removeElection("");
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
			step: 60 * 1000,
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
	
	//$( "#culture" ).change(function() {
	//	changeCulture($(this).val());
	//});
	
	document.getElementById("cultDE").checked = true;
	
	$("#cultDE").click(function(){ 
	    changeCulture("de-DE");
	});
	$("#cultEN").click(function(){ 
	    changeCulture("en-EN");
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
	
	var serverTimezone = -60;
	var clientDate = new Date();
	var timeDifference = clientDate.getTimezoneOffset()-serverTimezone;
	var currentDate = new Date(clientDate.setTime(clientDate.getTime()+timeDifference*60000));
	var month = currentDate.getMonth()+1<10 ? "0"+(currentDate.getMonth()+1) : (currentDate.getMonth()+1);
	var day = currentDate.getDate()+1<10 ? "0"+currentDate.getDate() : currentDate.getDate();
	document.getElementById("s-date").value = currentDate.getFullYear()+"."+month+"."+day;
	document.getElementById("s-time").value = currentDate.getHours()+":"+currentDate.getMinutes();

	var endDate = new Date(currentDate.setTime(currentDate.getTime()+10*60000));
	month = endDate.getMonth()+1<10 ? "0"+(endDate.getMonth()+1) : (endDate.getMonth()+1);
	day = endDate.getDate()+1<10 ? "0"+endDate.getDate() : endDate.getDate();
	document.getElementById("e-date").value = endDate.getFullYear()+"."+month+"."+day;
	document.getElementById("e-time").value = endDate.getHours()+":"+endDate.getMinutes();
	
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
	
}