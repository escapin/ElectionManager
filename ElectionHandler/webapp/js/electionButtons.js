function electionButtons() {
	
	/* Create 'click' event handler for rows */
    var rows = $('tr').not(':first');
    var row;
    var value;
    
    rows.on('click', function(e) {
        
        row = $(this);
        
        rows.removeClass('highlight');
        row.addClass('highlight');
        
        value = $(this).text().trim();        
    });
    
    $(document).bind('selectstart dragstart', function(e) { 
        e.preventDefault(); 
        return false; 
    });
	
	/* Send signal to node server */
	var config = JSON.parse(configRaw);
	var port = config.port;
	var address = config.address

	/* Create Button */
	$("#create").click(function() {
		$.post(address+":"+port+"/election", {task: "create", ID: "generated"}, function(data) {
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
		$.post(address+":"+port+"/election", {task: "remove", ID: value}, function(data) {
			if (data == "removed") {
				alert("Election removed");
				window.location.reload(true);
			}
			else{
				alert(data);
			}
		});
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
}