
var base_url = "http://23.21.246.188:80/";
var canvas_height = 200;

var TYPE_CODERLIST   = 0,
	TYPE_VIDEOLIST   = 1,
	TYPE_DATABYVIDEO = 2,
	TYPE_DATABYCODER = 3,
	TYPE_CODERPSI    = 4;

var EXTROVERSION      = "1",
	AGREEABLENESS     = "2",
	CONSCIENTIOUSNESS = "3",
	NEUROTICISM       = "4",
	OPENNESS          = "5",
	SELFCONSCIOUS     = "6",
	OTHERFOCUS        = "7",
	SHYNESS           = "8",
	SELFMONITOR       = "9";

var video_table = null, 
	coder_table = null, 
	video_data  = null, 
	coder_data  = null;

var coder_buffer = {};
var video_buffer = {};
var coder_info_buffer = {};
var outliner_buffer = {};
var mark_buffer = {};

var paper_set = [];
var indicator = [];

var video_ready = 0;

var palette = {
	sz : 15,
	gap : 5,
	palette_width : 0,
	palette_height : 0,
	palette_selected : null,
	_colors: ["#000000", "#1B65DE", "#08C24F", "#B5BA2D", "#F59B0A", "#E81207"],

	_draw: function(paper, clr, x0, y0, w, h) {
		str = "M" + x0 + "," + y0 + "L" +
				(x0+w) + "," + y0 + "L" +
				(x0+w) + "," + (y0+h) + "L" +
				x0 + "," + (y0+h) + "Z";

		bg = paper.path( str );
		bg.attr({fill: clr});

		return bg;
	},
	init: function() {
		
		palette.palette_width = 3 * palette.sz + 4 * palette.gap;
		palette.palette_height = 2 * palette.sz + 3 * palette.gap;

		if( $("#palette") ) {
			
			w = $("#palette").width();
			h = $("#palette").height();		
			r = Raphael(document.getElementById("palette"), w, h);
			palette.palette_selected = palette._draw(r, "#000000", 0, 0, w, h);

		}
		
	},
	display: function(x, y) {
		if( $("#palette_container").length ) {
			$("#palette_container").show();
			return;
		}
				
		container = $("<div>").attr("id", "palette_container")
						.css({
							"width" : palette.palette_width, 
							"height": palette.palette_height,
							"position": "absolute",
							"top": y,
							"left": x,
							"z-index": 3
						});
		
		$("body").append(container);

		r = Raphael(document.getElementById("palette_container"), palette.palette_width, palette.palette_height);

		r.rect(0, 0, palette.palette_width, palette.palette_height, 10).attr({fill: "#CCCCCC"});

		index = 0;
		for( i=1; i<=2; i++ ) { // row
			for( j=1; j<=3; j++ ) { // col
				palette._draw(r, palette._colors[index], j*palette.gap + (j-1)*palette.sz, i*palette.gap + (i-1)*palette.sz, palette.sz, palette.sz)
					.data("clr", palette._colors[index])
					.click(function() {
						$("#palette").attr("value", this.data("clr"));
						$("#palette_container").hide();
						if( palette.palette_selected ) {
							palette.palette_selected.attr({fill: this.data("clr")});
						}
					});
				index++;
			}
		}
	},
	close: function() {
		$("#palette_container").hide();
	}
};


var updater = {
	cursor: 0,
	errorSleepTime: 500,

	poll: function() {
		$.post(
			base_url + "update",
			"cursor=" + updater.cursor,
			function(dat) {
				if(dat.res)
					updater.onSuccess(dat.res);
				else
					updater.onError();
			},
			"json"
		);
	},

	onSuccess: function(dat) {
		if( dat.length ) {
			updater.cursor = dat[dat.length-1].id;

			for( i=0; i<dat.length; i++ ) {
				updater.showMessage(dat[i]);
			}
		}

		updater.errorSleepTime = 500;
		setTimeout( "updater.poll()", updater.errorSleepTime );
	},

	onError: function() {
		updater.errorSleepTime *= 2;
		setTimeout( "updater.poll()", updater.errorSleepTime );
	},

	showMessage: function(dat) {
		var uuid   = dat.id;
		var tokens = dat.body.split("|");
		var clr    = tokens[0].split(":")[1];
				
		var str = "";
		for( j=1; j<tokens.length; j++ ) {
			if( j>1 )
				str = str + "|";
			str = str + tokens[j];
		}

		addMessage(str, clr, uuid);
	}
};

function showMask( $info ) {
	$("#info").html($info);
	$("#mask").css("z-index", 2);
	$("object").attr("width", "0")
}

function hideMask() {
	$("#mask").css("z-index", -1);
	$("object").attr("width", "320")
}

function addMessage(msg, clr, uuid) {
	$new_message = $("<div>").css({
		"width": "300px", 
		"color": clr,
		"font-size": "13px",
		"font-family": "Georgia"
	}).html(msg);

	if( uuid ) {
		if( $("#"+uuid).length == 0 )
			$new_message.attr("id", uuid);
		else
			return;
	}

	$("#messagebox").append( $new_message );
	$("#messagebox").scrollTop( 2000 );
}

function newMessage( msg ) {
	$("#send").attr("disabled", "disabled");

	$.post(
		base_url + "new",
		"msg="+msg,
		function(dat) {
			if(dat.id) {
				updater.cursor = dat.id;
				updater.showMessage(dat);
				$("#send").removeAttr("disabled");
				$("#send").parent().find("textarea").val("");
			}
		},
		"json"
	);
}

function createHistogram(dat, paper_id, w, h) {
	
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

	// background
	bg = paper.path("M0,0").attr({stroke: "none", opacity: .3});

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
	bg.attr( {
		path: str + "L" + w + "," + h + "L0," + h + "Z",
		fill: "#11ED3D"
	} );

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
		if( outliner_buffer[selectedVideo+","+value] ) {
			alert( value+" is outlier" );
			return;
		}

		if( coder_buffer[selectedVideo] && coder_buffer[selectedVideo][value] )
			createHistogram( coder_buffer[selectedVideo][value], value, w, canvas_height/2 );
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
					createHistogram( dat, value, w, canvas_height/2 );
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
		createHistogram( video_buffer[video], "consensus view", w, canvas_height );
		return;
	}

	$.post(
		base_url,
		"type=" + TYPE_DATABYVIDEO + "&vid=" + video,
		function(dat) {
			if( dat.res ) {
				video_buffer[video] = dat.res;
				createHistogram(dat.res, "consensus view", w, canvas_height);	
			}
			if( dat.outliner ) {
				$.each(dat.outliner, function(index, value) {
					addMessage("[outlier] "+value, "red");
					outliner_buffer[ value ] = 1; // vid->turkId
				} );
			}
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
		player.setVolume(100);
		player.playVideo();
		player.seekTo( dur*percent, true );
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
			coder_data.addColumn( "string", "Attr" );
			
			coder_data.addRows( coderSet.length );
			for( i=0; i<coderSet.length; i++ ) {
				var turkId = coderSet[i]["turkID"];
				
				coder_info_buffer[turkId] = {};
				coder_info_buffer[turkId]["gender"]	= coderSet[i]["gender"];
				coder_info_buffer[turkId]["age"] = coderSet[i]["age"];
				coder_info_buffer[turkId]["1"] = coderSet[i]["1"];
				coder_info_buffer[turkId]["2"] = coderSet[i]["2"];
				coder_info_buffer[turkId]["3"] = coderSet[i]["3"];
				coder_info_buffer[turkId]["4"] = coderSet[i]["4"];
				coder_info_buffer[turkId]["5"] = coderSet[i]["5"];
				coder_info_buffer[turkId]["6"] = coderSet[i]["6"];
				coder_info_buffer[turkId]["7"] = coderSet[i]["7"];
				coder_info_buffer[turkId]["8"] = coderSet[i]["8"];
				coder_info_buffer[turkId]["9"] = coderSet[i]["9"];
				coder_info_buffer[turkId]["psi"] = {};

				coder_data.setCell(i, 0, turkId);
				coder_data.setCell(i, 1, coderSet[i]["gender"]);
			}

			coder_table = new google.visualization.Table(document.getElementById("codertable"));
			coder_table.draw(coder_data, {showRowNumber: true, height: "300px", width: "200px"});

			google.visualization.events.addListener(coder_table, 'select', function(){
				onSelectCoder( getSelectedCoder() );
			});
		},
		"json"
	);
}

function getSelectedCoder() {
	selection = coder_table.getSelection();
	coders = [];
	for( i=0; i<selection.length; i++ ) {
		var item = selection[i];
		var coder = coder_data.getFormattedValue(item.row, 0);
					
		coders.push(coder);
	}
	return coders;
}

function getSelectedVideo() {
	selection = video_table.getSelection();
	videos = [];
	if( selection.length > 1 ) {
		alert( "you're only allowed to select one video once" );
		return null;
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

function addMark(mid, comment) {
	a = $("<a>")
		.attr("href", "#")
		.text(comment)
		.click(function() {
			$("#notes").hide();

			_mid = $(this).parent().attr("mid");
			
			if( mark_buffer[_mid] ) {
				restoreState( 
					mark_buffer[_mid]["video"], 
					mark_buffer[_mid]["coder"].split("|"), 
					mark_buffer[_mid]["time"]
				);
			}
			
			return false;
		} );

	del = $("<span>").text("X")
					 .css( {
					 	"font-size": "11px",
					 	"margin-left": "4px",
					 	"color": "red"
					 } )
					 .hover(
					 	function() {
					 		$(this).css("cursor", "pointer");
					 	},
					 	function() {
					 		$(this).removeClass("cursor");
					 	}
					 )
					 .click(function() {
					 	_mid = $(this).parent().attr("mid");
					 	$.post(
					 		base_url+"mark",
					 		"mid="+_mid,
					 		function() {
					 			$("#notes div[mid='"+_mid+"']").remove();
					 		},
					 		"json"
					 	);
					 } );

	$("#notes").append(
		$("<div>")
		.css({
			"font-size": "13px",
			"font-family": "Arial",
			"margin-bottom": "5px"
		})
		.attr("mid", mid)
		.append(a)
		.append(del)
	);
}

function setMarkBuffer(mid, vid, coder, time, comment) {
	mark_buffer[mid] = {};
	mark_buffer[mid]["video"] = vid;
	mark_buffer[mid]["coder"] = coder;
	mark_buffer[mid]["time"] = time;
	mark_buffer[mid]["comment"] = comment;
}

function requestMarks() {
	$.post(
		base_url + "mark",
		"mid=-1",
		function(dat) {
			if( dat.length ) {
				for( i=0; i<dat.length; i++ ) {
					addMark( 
						dat[i]["mid"], 
						dat[i]["comment"] 
					);
					
					setMarkBuffer( 
						dat[i]["mid"], 
						dat[i]["vid"], 
						dat[i]["turkID"], 
						dat[i]["time"], 
						dat[i]["comment"] 
					);
				}
			}
		},
		"json"
	);
}

function updatePSIAttr(video) {
	if( coder_data ) {
		rowNum = coder_data.getNumberOfRows();
		for( i=0; i<rowNum; i++ ) {
			turkId = coder_data.getValue(i, 0);
			attrValue = coder_info_buffer[turkId]["psi"][video];
			coder_data.setCell(i, 1, ""+attrValue);
		}
		coder_table.draw(coder_data, {showRowNumber: true, height: "300px", width: "200px"});
	}
}

function updateCoderPSI() {
	video = getSelectedVideo();
	if( video == null ) return;

	if( coder_info_buffer[ coder_data.getValue(0,0) ]["psi"][video] ) {
		updatePSIAttr(video);
	} else {
		$.post(
			base_url,
			"type=" + TYPE_CODERPSI + "&vid=" + video,
			function(dat) {
				for( i=0; i<dat.length; i++ ) {
					turkId = dat[i]["turkID"];
					psi    = dat[i]["psi"];
					coder_info_buffer[turkId]["psi"][video] = psi;
				}
				updatePSIAttr(video);
			},
			"json"
		);	
	}
}

function updateCoderAttribute(attr) {
	if( coder_data ) {
		rowNum = coder_data.getNumberOfRows();
		for( i=0; i<rowNum; i++ ) {
			turkId = coder_data.getValue(i, 0);
			
			if( coder_info_buffer[turkId] && coder_info_buffer[turkId][attr] )
				attrValue = coder_info_buffer[turkId][attr];
			else
				continue;

			coder_data.setCell(i, 1, ""+attrValue);
		}
		coder_table.draw(coder_data, {showRowNumber: true, height: "300px", width: "200px"});
	}
}

google.load('visualization', '1', {packages:['table']});
google.setOnLoadCallback(function(){
	requestCoderList();
	requestVideoList();
	requestMarks();
});


function restoreStateVideoTime(time) {
	if( video_ready == 1 ) {
		player.setVolume(100);
		player.playVideo();
		player.seekTo(parseFloat(time), true);
	} else {
		setTimeout( "restoreStateVideoTime(" + time + ")", 100 );
	}
}
function restoreState( video, coder, time ) {
	
	onSelectVideo(video);
	for( i=0; i<video_data.getNumberOfRows(); i++ ) {
		if( video_data.getValue(i,0) == video ) {
			video_table.setSelection([{row:i, column:null}]);
			break;
		}
	}

	if( coder.length > 0 ) {
		onSelectCoder(coder);
		for( i=0; i<coder_data.getNumberOfRows(); i++ ) {
			if( $.inArray(coder_data.getValue(i,0), coder) != -1 ) {
				coder_table.setSelection([{row:i, column:null}]);
			}
		}
	}

	if( player ) {
		setTimeout( "restoreStateVideoTime(" + time + ")", 100 );
	}

}

function saveState( comment ) {
	turkId = "";
	curr  = 0;
	coder = getSelectedCoder();
	video = getSelectedVideo();
	
	if( video == null ) {
		alert("Select video first");
		return;
	}

	if( video_ready && player ) {
		curr  = player.getCurrentTime();
	}

	body = "vid=" + video;
	if( coder.length != 0 ) {
		for( i=0; i<coder.length; i++ ) {
			if( i>=1 )
				turkId = turkId + "|";
			turkId = turkId + coder[i];
		}
		body = body + "&turkID=" + turkId;
	}
	
	if( curr ) body = body + "&time=" + curr;

	body = body + "&comment=" + comment;

	$.post(
		base_url+"mark",
		body,
		function(dat) {
			if( dat.id ) {
				addMark( dat.id, comment )
				setMarkBuffer( dat.id, video, turkId, ""+curr, comment );
				$("#send").parent().find("textarea").val("");
			}
		},
		"json"
	);
		
}

$(document).ready(function(){
	
	$("#whom").val("NewGuest");

	$("#paint").click(function(evt) {
		var x0 = $("#paint").position().left;
		var x1 = evt.pageX;
		var w  = $("#paint").width();
		seekTo( (x1-x0)/w );
	} );


	$("#video_play").click(function() {
		if( video_ready ) {
			player.setVolume(100);
			player.playVideo();
		} else {
			alert("Wait until the video gets loaded");
		}
		return false;
	} );


	$("#video_stop").click(function() {
		player.stopVideo();
		return false;
	} );

	$("#attr").change(function() {
		attr = $("#attr option:selected").val();
		if( attr == "psi" ) {
			updateCoderPSI();
		} else {
			updateCoderAttribute(attr);
		}
	} );

	
	palette.init();

	$("#palette").click(function(evt) {
		x = evt.pageX;
		y = evt.pageY;
		palette.display(x, y-palette.palette_height);
	} );

	$("#send").click(function() {
		if( $("#send").parent().find("textarea").val() == "" ) {
			alert("Cannot send empty message");
			return;
		}

		body = "c:" + $("#palette").attr("value") + "|"
					+ $("#whom").val() + " said " + $("#send").parent().find("textarea").val();
		
		newMessage(body);
	} );

	$("#save").click(function() {
		comment = $("#send").parent().find("textarea").val();

		if( comment == "" ) {
			alert("Write some comments about your saving");
			return;
		}
		
		saveState(comment);
	} );

	$("#openNote").click( function() {$("#notes").show();} );
	$("#closeNote").click( function() {$("#notes").hide();} );

	updater.poll();
	notice = "c:" + $("#palette").attr("value") + "|a new guest comes";
	newMessage( notice );
});


