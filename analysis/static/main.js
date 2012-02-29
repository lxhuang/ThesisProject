
var base_url = "http://localhost:8483/";

var TYPE_CODERLIST   = 0;
var TYPE_VIDEOLIST   = 1;
var TYPE_DATABYVIDEO = 2;
var TYPE_DATABYCODER = 3;

var canvas_height = 200;

var video_table = null, coder_table = null;
var video_data  = null, coder_data  = null;

var coder_buffer = {};
var video_buffer = {};

var paper_set = [];
var indicator = [];

var video_ready = 0;

function showMask( $info ) {
	$("#info").html($info);
	$("#mask").css("z-index", 2);
	$("object").attr("width", "0")
}

function hideMask() {
	$("#mask").css("z-index", -1);
	$("object").attr("width", "320")
}

function createPaper(dat, paper_id, w, h) {
	
	var len = dat.length;

	// find the peak
	var max = dat[0];
	for( i=1; i<len; i++ ) {
		if( dat[i]>max )
			max=dat[i];
	}

	// create a new div
	$child_canvas = $("<div>").attr("id", paper_id)
						.css("width",  w)
						.css("height", h)
						.css("border-bottom", "1px solid #CCCCCC")
						.css("margin-bottom", "5px");
	$("#paint").append($child_canvas);

	// create a raphael paper
	var paper = Raphael(document.getElementById(paper_id), w, h);
	paper_set.push(paper)

	// dat is an array, representing the time line of the video (sample rate is 100ms)
	x = 0;
	y = dat[0] / max * h;
	str = "M0," + (h-y);
	for( i=1; i<w; i++ ) {
		y = dat[Math.round(i * len / w)];
		y = y / max * h;
		str = str + "L" + i + "," + (h-y);
	}

	// draw the histogram
	p = paper.path(str);
	p.attr({"stroke": "#11ED3D", "stroke-width":2});

	// print the paper ID
	paper.text(50, 10, paper_id);
}

function onSelectCoder(coders) {
	selectedVideo = getSelectedVideo();
	
	if( selectedVideo == null ) {
		alert("Please select video first");
		return;
	}

	$("#paint div:gt(0)").remove();
	paper_set.splice(1, paper_set.length-1);

	var w = $("#paint").width();

	$.each( coders, function(index, value) {
		if( coder_buffer[selectedVideo] && coder_buffer[selectedVideo][value] )
			createPaper( coder_buffer[selectedVideo][value], value, w, canvas_height );
		else {
			$.post(
				base_url,
				"type=" + TYPE_DATABYCODER + "&vid=" + selectedVideo + "&turkId=" + value,
				function(dat) {
					if( coder_buffer[selectedVideo] )
						coder_buffer[selectedVideo][value] = dat;
					else {
						coder_buffer[selectedVideo] = {};
						coder_buffer[selectedVideo][value] = dat;
					}
					createPaper( dat, value, w, canvas_height );
				},
				"json"
			);
		}
	} );
}

function onSelectVideo(video) {
	if( player ) {
		player.loadVideoById(video);
		player.mute();
		showMask("loading " + video + "...");

		video_ready = 0;

		setTimeout("loadingProgress()", 200);
	}

	// clear the painting area
	$("#paint").html("");
	paper_set.splice(0, paper_set.length);

	var w = $("#paint").width();

	if( video_buffer[video] ) {
		createPaper( video_buffer[video], "total_view", w, canvas_height );
		return;
	}

	$.post(
		base_url,
		"type=" + TYPE_DATABYVIDEO + "&vid=" + video,
		function(dat) {
			video_buffer[video] = dat;
			createPaper(dat, "total_view", w, canvas_height);
		},
		"json"
	);
}

function loadingProgress() {
	var loaded = player.getVideoBytesLoaded();
	var total  = player.getVideoBytesTotal();
	
	if( total != 0 ) {
		if( loaded >= total/5 ) {
			hideMask();
			player.setVolume(100);
			player.seekTo(0);
			player.pauseVideo();
			video_ready = 1;

			setTimeout("currentProgress()", 100);

			return;
		}
	}

	setTimeout("loadingProgress()", 200);
}

function currentProgress() {
	var curr  = player.getCurrentTime();
	var total = player.getDuration();
	var w = $("#paint").width();

	for( i=0; i<indicator.length; i++ ) indicator[i].remove();
	indicator.splice(0, indicator.length);

	$.each(paper_set, function(index, value) {
		
		var x = Math.round(curr / total * w);
		var str = "M" + x + ",0L" + x + "," + canvas_height;

		i = value.path(str);
		i.attr({"stroke":"red"});

		indicator.push(i);

	} );

	setTimeout("currentProgress()", 100);
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

function seekTo(percent) {
	if( video_ready ) {
		dur = player.getDuration();
		player.seekTo( dur*percent, true );
		player.setVolume(100);
		player.playVideo();	
	} else {
		alert("Wait until the video gets loaded");
		return;	
	}
}

function onYouTubePlayerReady( playerId ) {
	player = document.getElementById("playercontainer");
	player.addEventListener("onError", "onErrorHandler");
}

function requestCoderList() {
	$.post(
		base_url,
		"type="+TYPE_CODERLIST,
		function(coderSet) {
			coder_data = new google.visualization.DataTable();
			coder_data.addColumn( "string", "TurkID" );
			coder_data.addRows( coderSet.length );
			for( i=0; i<coderSet.length; i++ ) {
				var turkId = coderSet[i]["turkID"];
				coder_data.setCell(i, 0, turkId);
			}

			coder_table = new google.visualization.Table(document.getElementById("codertable"));
			coder_table.draw(coder_data, {showRowNumber: true, height: "300px", width: "200px"});

			google.visualization.events.addListener(coder_table, 'select', function(){
				selection = coder_table.getSelection();
				coders = [];
				for( i=0; i<selection.length; i++ ) {
					var item = selection[i];
					var coder = coder_data.getFormattedValue(item.row, 0);
					
					coders.push(coder);
				}
				onSelectCoder(coders);
			});
		},
		"json"
	);
}

function getSelectedVideo() {
	selection = video_table.getSelection();
	videos = [];
	if( selection.length > 1 ) {
		alert( "you're only allowed to select one video once" );
		return;
	}

	for( i=0; i<selection.length; i++ ) {
		var item = selection[i];
		var video = video_data.getFormattedValue(item.row, 0);
		
		return video;
	}

	return null;
}

function requestVideoList() {
	$.post(
		base_url,
		"type="+TYPE_VIDEOLIST,
		function(videoSet) {
			video_data = new google.visualization.DataTable();
			video_data.addColumn( "string", "videoID" );
			video_data.addRows( videoSet.length );

			for( i=0; i<videoSet.length; i++ ) {
				var videoId = videoSet[i]["vid"];
				video_data.setCell(i, 0, videoId);
			}

			video_table = new google.visualization.Table(document.getElementById("videotable"));
			video_table.draw(video_data, {showRowNumber: true, height: "300px", width: "200px"});

			google.visualization.events.addListener(video_table, 'select', function(){
				onSelectVideo( getSelectedVideo() );
			});
		},
		"json"
	);
}

google.load('visualization', '1', {packages:['table']});
google.setOnLoadCallback(function(){
	requestCoderList();
	requestVideoList();
});

$(document).ready(function(){
	
	$("#paint").click(function(evt){
		var x0 = $("#paint").position().left;
		var x1 = evt.pageX;
		var w  = $("#paint").width();
		seekTo( (x1-x0)/w );
	});


	$("#video_play").click(function(){
		if( video_ready ) {
			player.setVolume(100);
			player.playVideo();
		} else {
			alert("Wait until the video gets loaded");
		}
		return false;
	});


	$("#video_stop").click(function(){
		player.stopVideo();
		return false;
	});


});


