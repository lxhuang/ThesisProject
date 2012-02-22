
$base_url = "http://localhost:8483/";

var timer = null;

var state = 0;	//0: stop; 1:playing, 2:end

var started = 0; // whether the user starts the video or not

// data format
// s:tttt|b:tttt|p:tttt| (s, start; b, backchannel; p, pause)
var dat = [];
var post_data = {};

function showTip($t) {
	$("#tip").text($t);
}

function showMask( $info ) {
	$("#info").text($info);	
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
	$time = (new Date()).getTime();
	switch(type) {
		case 's':
			dat.push( 's:'+$time );
			break;
		case 'b':
			dat.push( 'b:'+$time );
			break;
		case 'p':
			dat.push( 'p:'+$time );
			break;
		default:
			break;
	}
}

function onSpace() {
	$("body").focus();

	if( state == 0 ) { // stop

		$('body').scrollTop( $('body').height() );

		addEvent('s');
		
		playVideo();
		
		hideMask();
		
		state = 1;
		started = 1;

		showTip("Press space bar when you'd like to give feedback");

	} else if (state == 1) { // playing
		addEvent('b');

		turnonFrame();
	} else { // end
		
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

		$("#tip").next().show();

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
					alert("Error at server side. Cannot delete the video. Refresh the page please.");
				}
			},
			"json"
		)

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

				$("tr").find("td:gt(0)").attr("class", "unselected");

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
				onComplete();
			}
			break;
		case 1:     // playing
			break;
		case 2:     // paused
			showTip("");
			showMask("Press space bar to start");

			addEvent('p');
			state = 0;
			break;
		case 3:     // buffering
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
		player.loadVideoById("rMICjUA4piA");
	} else {
		$("#intro").remove();
		$("#once").remove();
		player.mute();
		player.loadVideoById($.session("currentVideo"));
	}

	timer = setTimeout("loadingProgress()", 200);
	
	showMask("The video is now loading. Wait...");
	state = 2;
}

function loadingProgress() {
	var loaded = player.getVideoBytesLoaded();
	var total  = player.getVideoBytesTotal();
	
	if( total != 0 ) {
		var percent = parseInt((loaded/total) * 100);
		showMask("The video is now loading. Wait (" + percent + "%)");
	}

	if( loaded == total ) {
		clearTimeout(timer);

		state = 0;

		showMask("Press space bar to start");
	} else {
		setTimeout("loadingProgress()", 200);
	}
}


/////// Longtail player /////////
/*
function onStateChange(obj) {
	switch(obj.newstate) {
		case 'BUFFERING':
			break;
		case 'PLAYING':
			showTip("Press space bar when you'd like to give feedback");
			break;
		case 'PAUSED':
			showTip("");
			showMask("Press space bar to start");

			addEvent('p');
			state = 0;
			break;
		case 'COMPLETED':
			showTip("");

			addEvent('p');
			state = 2;
			onComplete();
			break;
		default:
			break;
	}
}

function onTimeChange(obj) {}

function onLoading(obj) {
	if( duration != 0 && obj.loaded != 0 && obj.loaded == obj.total ) {
		state = 0;

		showMask("Press space bar to start");

		player.removeModelListener('LOADED', 'onLoading');
	}
}

function onMetaLoaded(obj) {
	if( obj.duration ) {
		player.removeModelListener( 'META', 'onMetaLoaded' );
	}
}

function playVideo() {
	player.sendEvent('PLAY');
	player.sendEvent('MUTE', false);
}

function loadVideo() {
	player.addModelListener( 'META', 'onMetaLoaded' );
	player.addModelListener( 'LOADED', 'onLoading' );

	if( $.session("currentVideo") == undefined )
		player.sendEvent('LOAD', '../video/example.flv');
	else {
		$("#intro").remove();
		$("#tip").next().remove();
		player.sendEvent('LOAD', '../video/'+$.session("currentVideo")+'.flv');
	}

	player.sendEvent('PLAY');
	player.sendEvent('PLAY', 'false');

	showMask("The video is now loading. Wait...");
	state = 2;
}

function onPlayerReady() {
	player.addModelListener( 'STATE', 'onStateChange' );
	player.addModelListener( 'TIME',  'onTimeChange' );
	
	loadVideo();
}
*/

function onUserEvent(evt) {
	if( !evt ) evt = window.event;

	if( evt.keyCode == 32 ) {
		onSpace();

		document.onkeydown = function(evt) {}
	}
}

$(document).ready(function(){

	$("span.usroption").click(function(){
		$selected = $(this).attr("value");
		
		$index = $(this).parent().parent().attr("no");
		
		$(this).parent().parent().find("td:gt(0)").attr("class", "unselected");

		$(this).parent().attr("class", "selected");

		post_data[parseInt($index)] = $selected;
	});

	$("span.usroption").hover(
		function() {
			$("span.usroption").css("cursor", "pointer");
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

	document.onkeydown = function(evt) {
		onUserEvent(evt);
	}

	document.onkeyup = function(evt) {
		if( !evt ) evt = window.event;
		if( evt.keyCode == 32 ) {
			turnoffFrame();
			document.onkeydown = function(evt) {
				onUserEvent(evt);
			}
		}
	}

});