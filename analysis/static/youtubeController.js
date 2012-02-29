

var player = null;


$(document).ready(function(){
	
	var params = { allowScriptAccess : "always" };
	var atts = { id : "playercontainer" };
	swfobject.embedSWF(
		"http://www.youtube.com/apiplayer?enablejsapi=1&version=3", 
		"playercontainer",
		"320",
		"240",
		"8",
		null,
		null,
		params,
		atts
	);

});



