
$base_url = "http://23.21.246.188:80/";

var timer = null;

var state = 0;	//0: stopped; 1:playing, 2:end

var started = 0; // whether the user starts the video or not

// data format
// s:tttt|b:tttt|p:tttt| (s, start; b, backchannel; p, pause)
var dat = [];
var post_data = {};

function showTip($t) {
	$("#tip").html($t);
}

function showMask( $info ) {
	$("#info").html($info);	
	$("#mask").css("z-index", 2);
	$("object").attr("width", "0")
}

function hideMask() {
	$("#mask").css("z-index", -1);
	$("object").attr("width", "640")
}

// visual feedback to user when he presses space bar
function turnonFrame() {
	$("#mask").parent().parent().css("background-color", "#3D9400");
}

function turnoffFrame() {
	$("#mask").parent().parent().css("background-color", "#000000");	
}

function addEvent(type) {
	time = (new Date()).getTime();

	dat.push( type + ":" + time );
}

function onSpace() {
	$("body").focus();

	if( state == 0 ) { // stop
		addEvent('s');
		
		state = 1;
		started = 1;

		hideMask();
		showTip("Press space bar when you'd like to give feedback<br/>Don't click on the player area");

		playVideo();

		$('body').scrollTop( $('body').height() );

	} else if (state == 1) { // playing
		addEvent('b');

		turnonFrame();
	} else {
		
	}
}

function requestNextVideo() {
	
	$.session("turkID", $.session("turkID"));
	
	$.post(
		$base_url + "task",
		"tid=" + $.session("turkID"),
		function(dat) {
			if( dat.v ) {
				if( parseInt(dat.v) == -1 ) {
					window.location.href = $base_url + "comment";
				} else {
					$.session("currentVideo", dat.v);
					
					loadVideo();

					$('body').scrollTop( 0 );
				}
			} else {
				alert("Error at server side.");
			}
		},
		"json"
	);

}

function postFeedbackData() {
	$bc = dat.toString();
	$vid = $.session("currentVideo");
	$tid = $.session("turkID");

	$.post(
		$base_url + "watch",
		"tid=" + $tid + "&vid=" + $vid + "&bc=" + $bc,
		function() {},
		"json"
	);

	dat.splice(0, dat.length);
}

function onComplete() {
	if( $.session("currentVideo") == undefined ) {
		dat.splice(0, dat.length);
		
		showMask("Example video finished");

		$("#once").show();

		$('body').scrollTop( $('body').height() );
	} else {
		postFeedbackData();
		
		// tell the server this video is done
		$.post(
			$base_url + "task",
			"tid=" + $.session("turkID") + "&act=1",
			function(dat) {
				if( dat.res == "success" ) {
					
					showPostQuestionnaire();

					$('body').scrollTop( $('body').height() );

				} else {
					$.session("turkID", $.session("turkID"));
					$.session("currentVideo", $.session("currentVideo"));
					alert("Error at server side. Cannot delete the video. Refresh the page please.");
				}
			},
			"json"
		);
	}
}

function showPostQuestionnaire() {

	showMask("Please finish the questionnaire below");
	
	$("#pq").show();

}

function submitPostQuestion() {
	
	var size = 0;
	for( key in post_data ) {
		if( post_data.hasOwnProperty(key) )
			size++;
	}
	if( size != 6 ) {
		alert("Please finish all the questions");
		return false;
	}

	$psi = "";
	for( i = 1; i <= size; i++ ) {
		$psi += post_data[i];
	}

	$.post(
		$base_url+"psi",
		"tid=" + $.session("turkID") + "&vid=" + $.session("currentVideo") + "&psi=" + $psi,
		function(dat) {
			if( dat.success ) {
				$("#pq").hide();

				post_data = {};

				$("tr").find("td:gt(0)").attr("class", "unselected usroption");

				requestNextVideo();	
			}
		},
		"json"
	);
	return true;
}

/////// Video related manipulation /////////

function onYouTubePlayerReady( playerId ) {
	
	player = document.getElementById("playercontainer");

	player.addEventListener("onStateChange", "onStateChangeHandler");
	player.addEventListener("onError", "onErrorHandler");

	loadVideo();

}

function onErrorHandler(code) {
	switch(code) {
		case 2:
			alert("Invalid video ID");
			break;
		case 100:
			alert("The video has been removed");
			break;
		case 101:
		case 150:
			alert("The video cannot be played in embedded mode");
			break;
		default:
			break;
	}
}

var paused = 0;

function onStateChangeHandler(newstate) {
	switch(newstate) {
		case -1:    // unstarted
			break;
		case 0:     // ended
			if ( started == 1 ) {
				showTip("");
				showMask("Request the next video...");

				addEvent('p');
				state = 2;
				started = 0;
				paused = 0;
				onComplete();
			}
			break;
		case 1:     // playing
			if( paused == 1 ) {
				addEvent('c');
				state = 1;
				paused = 0;
			}
			break;
		case 2:     // paused (should never happen)
			if( started == 1 ) {
				addEvent('pp');
				state = 3;
				paused = 1;
			}
			break;
		case 3:     // buffering
			if( started == 1 ) {
				addEvent('pp');
				state = 3;
				paused = 1;
			}
			break;
		case 5:     // cued
			break;
		default:
			break;
	}
}

function playVideo() {
	player.setVolume(100);
	player.seekTo(0);
	player.playVideo();
}

function loadVideo() {
	if( $.session("currentVideo") == undefined ) {
		player.mute();
		player.loadVideoById("oc5dJlRw6vU");
	} else {
		$("#intro").remove();
		$("#once").remove();
		player.mute();
		player.loadVideoById($.session("currentVideo"));
	}
	
	player.setPlaybackQuality("small");
	player.setPlaybackQuality("medium");

	showMask("The video is now loading. Wait...");
	state = 2;

	timer = setTimeout("loadingProgress()", 200);
}

function loadingProgress() {
	var loaded = player.getVideoBytesLoaded();
	var total  = player.getVideoBytesTotal();
	
	if( total != 0 ) {
		var percent = parseInt((loaded/total) * 100);
		showMask("The video is now loading. Wait (" + percent + "%)");

		if( loaded >= total/2 ) {

			state = 0;

			showMask("Press space bar to start <br/> Don't click on the player area");

			return;
		}
	}

	setTimeout("loadingProgress()", 200);
}

function onUserEvent(evt) {
	if( !evt ) evt = window.event;

	if( evt.keyCode == 32 ) {
		onSpace();

		window.onkeydown = function(evt) {}
	}
}

$(document).ready(function(){

	$.session("turkID", $("#turkID").attr("value"));

	$("td.usroption").click(function(){
		
		$selected = $(this).find("span").attr("value");
		
		$index = $(this).parent().attr("no");
		
		$(this).parent().find("td:gt(0)").attr("class", "unselected usroption");

		$(this).attr("class", "selected usroption");

		post_data[parseInt($index)] = $selected;
	});

	$("td.usroption").hover(
		function() {
			$("td.usroption").css("cursor", "pointer");
		},
		function() {}
	);
	
	$("#startButton").click(function(){
		
		requestNextVideo();
		
		return false;
	});

	$("#nextButton").click(function(){
		
		submitPostQuestion();

		return false;

	});

	window.onkeydown = function(evt) {
		onUserEvent(evt);
	}

	window.onkeyup = function(evt) {
		if( !evt ) evt = window.event;
		if( evt.keyCode == 32 ) {
			turnoffFrame();
			window.onkeydown = function(evt) {
				onUserEvent(evt);
			}
		}
	}

});
