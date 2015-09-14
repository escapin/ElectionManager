function electionButtons() {
	
    //////////////////////////////////////////////////////////////////////////////
	/// PAGE 1
	
	/* Create 'click' event handler for rows */
    var rows = $('tr').not(':first');
    var row;
    var value;
    
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
	
	/* Send signal to node server */
	var config = JSON.parse(configRaw);
	var port = config.port;
	var address = config.address;

	/* Create Button */
	$("#create").click(function() {
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
    
	/* Remove Button */
	$("#remove").click(function() {
    	if(value == null){
    		alert("no election selected");
    	}
    	else{
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
	});
    
    /* Vote Button */
    $("#vote").click(function() {
    	if(value == null){
    		alert("no election selected");
    	}
    	else{
			window.location.href = address+"/"+value+"/votingBooth";
		}
	});
    
    //////////////////////////////////////////////////////////////////////////////
    /// PAGE 2
    
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
	
    $('#e-name').on('input', enableWhenNotEmpty($('#adv-create')));
    $('#e-desc').on('input', enableWhenNotEmpty($('#adv-create')));
	
    function enableWhenNotEmpty(button) {
        return function() {
        	var ename = $('#e-name').val();
        	var description = $('#e-desc').val();
            if( ename==='' || description==='') 
                button.prop('disabled', true);
            else 
                button.prop('disabled', null);
        };
    }
    
	/* Advanced-create Button */
	$("#adv-create").click(function() {
		var ename = $('#e-name').val();
		var edesc = $('#e-desc').val();
		$('#processing').fadeIn(150);
		$.post(address+":"+port+"/election", {task: "create", ID: "generated", title: ename, description: edesc}, function(data) {
			$('#processing').fadeOut(150);
			if (data == "created") {
				alert("Election created");
				window.location.reload(true);
			}
			else{
				alert(data);
			}
		});
	});
}