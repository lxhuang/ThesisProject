

$base_url = "http://23.21.246.188:80/";

$(document).ready(function(){
	
	$("#verify").click(function(){
		$.post(
			$base_url + "comment",
			"tid=" + $.session("turkID") + "&comment=" + $("#comment").val(),
			function(dat) {
				if( dat.code ) {
					$("body").html(
						"<div style='margin-top: 50px;'>" + dat.code + "</div>" + 
						"<div style='margin-top: 25px;'>Please copy the code and paste it into the text field in Amazon Mechanical Turk, and submit it, you are done.</div>"
					);
				} else {
					if( dat.err ) {
						alert(dat.err);
					} else {
						alert("You either do this study twice or come here without following the routine.");
					}
					return false;
				}
			},
			"json"
		)
		return false;
	});

});
