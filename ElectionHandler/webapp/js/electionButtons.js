function electionButtons() {
	
    //////////////////////////////////////////////////////////////////////////////
	/// PAGE 1
	
	/* Create 'click' event handler for rows */
    var rows = $('tr').not(':first');
    var row;
    var value;

    
	/* Send signal to node server */
	var config = JSON.parse(configRaw);
	var port = config.port;
	var address = config.address;

	function simpleElection() {
		disableButtons();
		$('#processing').fadeIn(150);
		$.post(address+":"+port+"/election", {task: "create", ID: "generated", title: "", description: ""}, function(data) {
			$('#processing').fadeOut(150);
			if (data == "created") {
				alert("Election created");
				window.location.reload(true);
			}
			else{
				alert(data);
			}
		});
	}
	
	function removeElection() {
		if(value == null){
    		alert("no election selected");
    	}
    	else{
    		disableButtons();
    		$('#processing').fadeIn(150);
    		$.post(address+":"+port+"/election", {task: "remove", ID: value}, function(data) {
    			$('#processing').fadeOut(150);
    			if (data == "removed") {
					alert("Election removed");
					window.location.reload(true);
				}
				else{
					alert(data);
				}
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
                		//console.log("should disable");
                		button.prop('disabled', true);
                	}
                }
                else{
                	//console.log("all good");
                	button.prop('disabled', null);
                }
            }
        };
    }	
    
    
    function createWithDescription() {
    	disableButtons();
		var ename = $('#e-name').val();
		var edesc = $('#e-desc').val();
		var startingTime = $('#start-time').val();
		var endingTime = $('#end-time').val();
		$('#processing').fadeIn(150);
		$.post(address+":"+port+"/election", {task: "create", ID: "generated", title: ename, description: edesc, startTime: startingTime, endTime: endingTime}, function(data) {
			$('#processing').fadeOut(150);
			if (data == "created") {
				alert("Election created");
				window.location.reload(true);
			}
			else{
				alert(data);
			}
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
    
	/* Create Button */
	$("#create").click(function() {
		simpleElection();
	});
	
    
	/* Remove Button */
	$("#remove").click(function() {
    	removeElection();
	});
    
	
    /* Advanced Button */
	$("#advance").click(function() {
		$('#welcome').hide(150);
	    $('#advanced').show(150);
	});

    /* Back Button */
	$("#back").click(function() {
		$('#advanced').hide(150);
	    $('#welcome').show(150);
	});
	
	/* Advanced-create Button */
	$("#adv-create").click(function() {
		createWithDescription();
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
		$("#adv-create").prop('disabled', true);
	}

	function enableButtons(){
		$("#vote").prop('disabled', null);
		$("#close").prop('disabled', null);
		$("#create").prop('disabled', null);
		$("#remove").prop('disabled', null);
		$("#advance").prop('disabled', null);
		$("#adv-create").prop('disabled', null);
	}
	
	
	
    $('#e-name').on('input', enableWhenNotEmpty($('#adv-create')));
    $('#e-desc').on('input', enableWhenNotEmpty($('#adv-create')));    
    $('#start-time').on('input', enableWhenNotEmpty($('#adv-create')));
    $('#end-time').on('input', enableWhenNotEmpty($('#adv-create')));
    
    
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