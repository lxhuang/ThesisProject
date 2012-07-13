
var base_url = "http://localhost:8483/";
var test_video_base = "http://localhost:8483/static/";
var video_base = "https://s3.amazonaws.com/multicomp_backchannel_videos/";
var video = null;
var test_mode = true;

// whether enough data has been loaded
var ready_to_play = false;
// whether the video has started playing
var start_playing = false;

// called whenever a new video gets loaded
function startSession() {
	updateMask("Press space bar to load video");
}
// called whenever a video finishes playing
function endSession() {
	ready_to_play = false;
	start_playing = false;
}

function updateMask(content) {
	if (content) {
		$("#mask").show();
		$("#info span").text(content);
	} else {
		$("#mask").hide();
	}
}

// create paper to draw timeline
var timeline_paper = null;
var timeline_indicator = null;
var user_label_id = 0;
var user_labels = [];
var label_start = false;
function clearPaper() {
	for (i = 0; i < user_labels.length; ++i) {
		user_labels[i].remove();
	}
	user_labels.splice(0, user_labels.length);
}
function createPaper() {
	w = $("#timeline_container").width();
	h = $("#timeline_container").height();
	timeline_paper = Raphael(document.getElementById("timeline_container"), w, h);
	background = timeline_paper.rect(0, 0, w, h).attr({"fill":"#FFF"});
	background.click(function(evt){
		seekVideoPercentage(evt.offsetX / w);
	});
}
function drawTimeline(x) {
	if (timeline_indicator) timeline_indicator.remove();
	var canvas_height = $("#timeline_container").height();
	var str = "M" + x + ",0L" + x + "," + canvas_height;
	if (timeline_paper) {
		timeline_indicator = timeline_paper.path(str);
		timeline_indicator.attr({"stroke": "red"});
	}
}
function drawUserLabel(x) {
	if (label_start) {
		var x0 = user_labels[user_labels.length - 1].attr("x");
		user_labels[user_labels.length - 1].attr("width", x - x0);
	}
}
function updateTimelineIndicator() {
	var t = video.currentTime;
	var percent = t / video.duration;
	var canvas_width = $("#timeline_container").width();
	drawTimeline(canvas_width * percent);
	drawUserLabel(canvas_width * percent);
	if (ready_to_play == true)
		requestAnimFrame(updateTimelineIndicator);
}
function startDrawingLabel() {
	var t = video.currentTime;
	var percent = t / video.duration;
	var canvas_width = $("#timeline_container").width();
	var canvas_height = $("#timeline_container").height();
	var _user_label = timeline_paper.rect(percent * canvas_width, 0, 0, canvas_height);
	_user_label.attr({"fill":"#4486F6", "stroke":"#B1C9ED", "fill-opacity":0.7});
	_user_label.data("start", t);
	_user_label.data("id", user_label_id);
	user_labels.push(_user_label);
	label_start = true;
	user_label_id = user_label_id + 1;
}
function stopDrawingLabel() {
	var t = video.currentTime;
	if (user_labels.length > 0) {
		user_labels[user_labels.length - 1].data("end", t);
	}
	label_start = false;
}

// video related operations
function checkLoadingStatus() {
	buffered = video.buffered;
	if (buffered.length > 0) {
		percentage = buffered.end(0) / video.duration;
		percentage = parseInt(percentage * 100);
		if (percentage >= 40) {
			ready_to_play = true;
			updateMask("Press space bar to start video");
			return;
		}
		updateMask("Loaded " + percentage + "%");
		console.log(percentage);
	}
	requestAnimFrame(checkLoadingStatus);
}
function loadVideo(videoId) {
	if (test_mode) {
		$("#mp4").attr("src", test_video_base + videoId + ".mp4");
	} else {
		$("#mp4").attr("src", video_base + videoId + ".mp4");
	}
	video.volume = 0;
	video.load();
	video.play();
	updateMask("Loading...");
	requestAnimFrame(checkLoadingStatus);
}
function playVideo() {
	video.play();
	updateMask(false);
	start_playing = true;
	updateTimelineIndicator();
}
var play_until_when = 0
function playUntil(time) {
	play_until_when = time;
	resumeVideo();
	_playUntil();
}
function _playUntil() {
	if (video.currentTime >= play_until_when) {
		video.pause();
	} else {
		requestAnimFrame(_playUntil);
	}
}
function seekVideo(time) {
	video.currentTime = time;
}
function seekVideoPercentage(p) {
	seek_to_time = p * video.duration;
	video.currentTime = seek_to_time;
}
function resumeVideo() {
	video.play();
}

// html5 video related events
function registerMediaEvents() {
	video = document.getElementById("video");
	video.addEventListener("ended", function() {
		$("#check_finish").show();
	}, false);
}

// user events
function onSpaceDown(evt) {
	if (!start_playing) {
		if (!ready_to_play) {
			loadVideo("test");
		} else {
			seekVideo(0);
			playVideo();
		}
	} else {
		startDrawingLabel();
	}
	window.onkeydown = function(evt) {}
}
function onSpaceUp(evt) {
	window.onkeydown = function(evt) { if (evt.keyCode == 32) onSpaceDown(evt); }
	if (start_playing) {
		stopDrawingLabel();
		updateLabelContainer();
	}
}

// label container
function clearLabelContainer() {
	$("#label_container table").html("");
}
function updateLabelContainer() {
	if (user_labels.length > 0) {
		var beg = user_labels[user_labels.length - 1].data("start");
		var end = user_labels[user_labels.length - 1].data("end");
		var idx = user_labels[user_labels.length - 1].data("id");
		beg = beg.toFixed(3);
		end = end.toFixed(3);

		var entry = $("<tr class='user_label_entry'>").attr("user_label_id", idx)
	    	        .append($("<td class='user_label_entry_span'>").text(beg))
	        	    .append($("<td class='user_label_entry_span'>").text(end))
	            	.append($("<td class='user_label_entry_span'>").append(
	            		$("<a href='#'>").append(
	            			$("<img width='12px' height='12px'>").attr("src", "/static/img/delete.png")
	            		).click(function(){
	            			selected_user_label_id = $(this).parent().parent().attr("user_label_id");
	            			selected_user_label_id = parseInt(selected_user_label_id);
	            			deleteUserLabel(selected_user_label_id);
	            			return false;
	            		})
	            	))
	            	.append($("<td class='user_label_entry_span'>").append(
	            		$("<a href='#'>").append(
	            			$("<img width='24px' height='24px'>").attr("src", "/static/img/play.png")
	            		).click(function(){
	            			selected_user_label_id = $(this).parent().parent().attr("user_label_id");
	            			selected_user_label_id = parseInt(selected_user_label_id);
	            			playUserLabel(selected_user_label_id);
	            			return false;
	            		})
	            	))
	            	.mouseover(function(){
	            		selected_user_label_id = $(this).attr("user_label_id");
	            		selected_user_label_id = parseInt(selected_user_label_id);
	            		emphasizeUserLabel(selected_user_label_id);
	            		$(this).css("text-decoration", "underline");
	            	})
	            	.mouseout(function(){
	            		selected_user_label_id = $(this).attr("user_label_id");
	            		selected_user_label_id = parseInt(selected_user_label_id);
	            		deemphasizeUserLabel(selected_user_label_id);
	            		$(this).css("text-decoration", "");
	            	});

		$("#label_container table").append(entry);

		var y1 = entry.position().top;
		var y0 = $("#label_container tr:eq(0)").position().top;
		var h  = $("#label_container").height();
		if (y1 - y0 > h)
			document.getElementById("label_container").scrollTop = ((y1 - y0) - h) + 50;
	}
}

// interact with user labels
function deleteUserLabel(user_label_id) {
	for (i = 0; i < user_labels.length; ++i) {
		if (parseInt(user_labels[i].data("id")) == user_label_id) {
			user_labels[i].remove();
			user_labels.splice(i, 1);
			break;
		}
	}
	$("table .user_label_entry[user_label_id=" + user_label_id + "]").remove();
}
function playUserLabel(user_label_id) {
	for (i = 0; i < user_labels.length; ++i) {
		if (parseInt(user_labels[i].data("id")) == user_label_id) {
			start = parseFloat(user_labels[i].data("start"));
			end = parseFloat(user_labels[i].data("end"));
			seekVideo(start);
			playUntil(end);
			break;
		}
	}
}
function emphasizeUserLabel(user_label_id) {
	for (i = 0; i < user_labels.length; ++i) {
		if (parseInt(user_labels[i].data("id")) == user_label_id) {
			user_labels[i].attr({"fill":"#0AF01D"});
			break;
		}
	}
}
function deemphasizeUserLabel(user_label_id) {
	for (i = 0; i < user_labels.length; ++i) {
		if (parseInt(user_labels[i].data("id")) == user_label_id) {
			user_labels[i].attr({"fill":"#4486F6"});
			break;
		}
	}
}

function clean() {
	endSession();
	clearPaper();
	clearLabelContainer();

	$("#check_finish").hide();
	$("#check_finish :checkbox").removeAttr("checked").next().text("Check it if you think you have finished.");
	$("#submit_label").hide();

	startSession();
}

// interact with server
function requestNextVideo() {}
function submitLabels() {
	ret_string = "";
	for (i = 0; i < user_labels.length; ++i) {
		start = user_labels[i].data("start").toFixed(4);
		end = user_labels[i].data("end").toFixed(4);
		ret_string = ret_string + start + "," + end;
		if (i < user_labels.length - 1)
			ret_string = ret_string + ";";
	}
	alert(ret_string);
}

$(document).ready(function(){
	registerMediaEvents();

	$("#check_finish").hide().change(function() {
		if ($("#check_finish :checkbox").is(":checked")) {
			$("#check_finish :checkbox").next().text("Uncheck it if you think you have not finished yet.");
			$("#submit_label").show();
		} else {
			$("#check_finish :checkbox").next().text("Check it if you think you have finished.");
			$("#submit_label").hide();
		}
	});

	$("#submit_label").hide().click(function() {
		submitLabels();
		clean();
	});

	window.onkeydown = function(evt) {
		if (evt.keyCode == 32)
			onSpaceDown(evt);
	}
	window.onkeyup = function(evt) {
		if (evt.keyCode == 32)
			onSpaceUp(evt);
	}

	$("#play_speed option:eq(1)").attr("selected", "selected");

	$("#play_speed").change(function () {
		play_back_speed = $("#play_speed option:selected").attr("value");
		play_back_speed = parseFloat(play_back_speed);
		video.playbackRate = play_back_speed;
	});

	startSession();

	createPaper();

	// shim layer with setTimeout fallback
    window.requestAnimFrame = (function(){
      return window.requestAnimationFrame       || 
             window.webkitRequestAnimationFrame || 
             window.mozRequestAnimationFrame    || 
             window.oRequestAnimationFrame      || 
             window.msRequestAnimationFrame     || 
             function( callback ){
             	window.setTimeout(callback, 1000 / 60);
             };
    })();
});