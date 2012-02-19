

$base_url = "http://localhost:8483/";

$data = {};

$(document).ready(function(){
	
//	for( $i = 1; $i <= 90; $i++ ) $data[$i] = $i;


	$("#submit_amazon_turk_id").click(function(){
		$turk_id = $("#amazon_turk_id").val();
		$.session("turkID", $turk_id);

		window.location.href = $base_url + "pq";
	});

	$("span.usroption").click(function(){
		$selected = $(this).attr("value");
		
		$index = $(this).parent().parent().attr("no");
		
		$(this).parent().parent().find("td:gt(0)").attr("class", "unselected");

		$(this).parent().attr("class", "selected");

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