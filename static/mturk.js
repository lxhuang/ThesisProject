

$base_url = "http://23.21.246.188:80/";

$data = {};

$(document).ready(function(){

	if( $.browser.msie ) {
		alert("We don't accept Microsoft IE browser (yes, it sucks). Please use a Firefox or Chrome or Safari instead.");
		return;
	}
	if( $.browser.opera ) {
		alert("We don't accept Opera. Please use a Firefox or Chrome or Safari instead");
		return;
	}
	
//	for( $i = 1; $i <= 90; $i++ ) $data[$i] = $i;

	$("#submit_amazon_turk_id").click(function(){
		$turk_id = $("#amazon_turk_id").val();
		$.session("turkID", $turk_id);

		window.location.href = $base_url + "pq";		

	});

	$("td.usroption").hover(
		function() {
			$("td.usroption").css("cursor", "pointer");
		},
		function() {}
	);

	$("td.usroption").click(function(){
		$selected = $(this).find("span").attr("value");
		
		$index = $(this).parent().attr("no");
		
		$(this).parent().find("td:gt(0)").attr("class", "unselected usroption");

		$(this).attr("class", "selected usroption");

		$data[parseInt($index)] = $selected;
	});

	$("#submit_personality").click(function(){
		$age = $("#age").val();
		$sex = $("#sex option:selected").val();
		
		if( $.isNumeric($age) == false ) {
			alert("Please input your age, for example, 37");
			return;
		}

		$size = 0;
		for( $key in $data ) {
			if( $data.hasOwnProperty($key) )
				$size++;
		}
		if( $size != 90 ) {
			alert("Please finish all the questions");
			return;
		}

		$personality = "";
		for( $i = 1; $i <= $size; $i++ ) {
			$personality += $data[$i];
		}

		$turk_id = $.session("turkID");
		if( $turk_id == undefined ) {
			return;
		}

		$.post(
			$base_url + "pq",
			"turkId=" + $turk_id + "&age=" + $age + "&sex=" + $sex + "&result=" + $personality,
			function(dat) {
				if( dat.err ) {
					alert(dat.err);
					return false;
				} else {
					$.session("uid", dat.res);
					window.location.href = $base_url + "example?id=" + dat.res + "&tid=" + $turk_id;
				}
			},
			"json"
		);

		return false;
	});
});
