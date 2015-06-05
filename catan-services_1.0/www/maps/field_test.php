<!DOCTYPE html>
<html>
  <head>
    <meta name="viewport" content="initial-scale=1.0, user-scalable=no">
    <meta charset="utf-8">
    <title>DICE: Disaster and Incident Communications nEtwork Visualization</title>
    <style>
      html, body, #map-canvas {
        height: 100%;
        margin: 0px;
        padding: 0px
      }
      #timestamp {
        position: absolute;
        top: 3%;
        left: 50%;
        margin-left: -180px;
        z-index: 5;
        background-color: #fff;
	    padding: 15px;
		border-bottom: 1px solid black;
		border-radius: 15px;
		box-shadow: 5px 5px 5px #888888;
		font-size:175%;
		font-weight:bold;
		background:#3385FF;
		color:white;
      }
    </style>
    <script src="https://maps.googleapis.com/maps/api/js?key=AIzaSyCM1x3VgMzI2rIpVFHk9VGduhoYVcYmGvM"></script>
    <script src="jquery-1.11.1.min.js"></script>
    <script>
var gps_data = {};
var signal_noise_data = {};
var mesh_data = {};
var messages_data = {};
<?php 
$data_path = "/home/ch23339/projects/catan/experiments/field_test_0106/";
foreach (Array("1","2","3") as $node_id) {
	$data = file_get_contents($data_path."node_".$node_id.".json");
	echo $data;
}



?>

var FOCUS_NODE = 2;

var map;
var refreshIntervalId;
var node_markers = {};
var node_links = {};
var node_icon = 'http://www.google.com/intl/en_us/mapfiles/ms/micons/blue-dot.png'
var icons = {'1':'http://maps.google.com/mapfiles/kml/paddle/1.png',
			 '2':'http://maps.google.com/mapfiles/kml/paddle/2.png',
		     '3':'http://maps.google.com/mapfiles/kml/paddle/3.png'
			}


function timeConverter(UNIX_timestamp){
  var a = new Date(UNIX_timestamp*1000);
  var months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
  var year = a.getFullYear();
  var month = months[a.getMonth()];
  var date = a.getDate();
  var hour = a.getHours();
  var min = "0"+a.getMinutes();
  var sec = "0"+a.getSeconds();
  var time = month + ' ' + date + ', ' + year + ' @ ' + hour + ':' + min.substr(min.length-2) + ':' + sec.substr(sec.length-2) ;
  return time;
}


link_lines = [];
function updateLinks() {

	for (l in link_lines) {
		link_lines[l].setMap(null);
	}
	link_lines = [];
	for (node_id in node_links) {
		for (x in node_links[node_id]) {
			link = node_links[node_id][x];

			if (node_id in node_markers && link['name'] in node_markers) {
				pos1 = node_markers[node_id].getPosition();
				pos2 = node_markers[link['name']].getPosition();

				pos1 = new google.maps.LatLng(pos1.lat(),pos1.lng());
				pos2 = new google.maps.LatLng(pos2.lat(),pos2.lng());
				ends = [pos1, pos2];
				
				quality = link["link_quality"]/100.0;
				console.log(node_id+" <-> "+link['name']+" "+quality);
				if (quality < .1) {
					quality = .1;
				}
				link_line = new google.maps.Polyline({
				    path: ends,
				    geodesic: true,
				    strokeColor: '#FF0000',
				    strokeOpacity: quality,
				    strokeWeight: 5
				  });

				link_line.setMap(map);
				link_lines.push(link_line);
// 				clearInterval(refreshIntervalId);
			}
		}
	}
	
}

function updateData() {
	smallest = -1;
	next_node = 0;

	data_type = "";
	// Check GPS Data
	for (node_id in gps_data) {
		if (gps_data[node_id].length == 0)
			continue;
		ts = gps_data[node_id][0][0];
		if (smallest == -1 || ts < smallest) {
			next_node = node_id;
			smallest = ts;
			data_type = "gps";
		}
	}
	// Check Signal Data
	for (node_id in signal_noise_data) {
		if (signal_noise_data[node_id].length == 0)
			continue;
		ts = signal_noise_data[node_id][0][0];
		if (smallest == -1 || ts < smallest) {
			next_node = node_id;
			smallest = ts;
			data_type = "signal";
		}
	}
	// Check Mesh Data
	for (node_id in mesh_data) {
		if (mesh_data[node_id].length == 0)
			continue;
		ts = mesh_data[node_id][0][0];
		if (smallest == -1 || ts < smallest) {
			next_node = node_id;
			smallest = ts;
			data_type = "mesh";
		}
	}
	// Check Mesh Data
	for (node_id in messages_data) {
		if (messages_data[node_id].length == 0)
			continue;
		ts = messages_data[node_id][0][0];
		if (smallest == -1 || ts < smallest) {
			next_node = node_id;
			smallest = ts;
			data_type = "message";
		}
	}

	// Update our time
	var formattedTime = timeConverter(smallest);

	document.getElementById("timestamp").innerHTML = formattedTime;

	if (data_type == "gps") {
		gps = gps_data[next_node][0][1];
		gps_data[next_node].splice(0,1);
		var myLatlng = new google.maps.LatLng(gps['latitude'],
				   gps['longitude']);
	
		if (next_node in node_markers) {
			node_markers[next_node].setPosition(myLatlng);
		} else {
			node_markers[next_node] = new google.maps.Marker({
				position: myLatlng,
				map: map,
				icon: icons[next_node],
				title: 'Node '+node_id
			});
		}
		if (next_node == FOCUS_NODE) {
			map.panTo(myLatlng);
		}
	} else if (data_type == "signal") {
		signal_noise_data[next_node].splice(0,1);
	} else if (data_type == "mesh") {

		mesh = mesh_data[next_node][0][1];
		mesh_data[next_node].splice(0,1);

		node_links[next_node] = mesh;

		updateLinks();
		
		
// 		clearInterval(refreshIntervalId);
	} else if (data_type == "message") {

		data = messages_data[next_node][0][1];
		messages_data[next_node].splice(0,1);

		to = data['to_first']+' '+data['to_last'];
		from = data['from_first']+' '+data['from_last'];

		if (data['status'] == null) {
			status_msg = "";
		} else {
			statuses = {'information_sought': "Seeking information",
				'is_note_author': "Self reported",
				'believed_alive': "Believed to be alive",
				'believed_missing': "Believed to be missing"};
			status_msg = '<p>Status: '+statuses[data['status']]+'</p>';
		}
		if (data['message'] == null) {
			data['message'] = '<i>None.</i>';
		}
		
		var contentString = '<div id="content" style="overflow: hidden;white-space: nowrap;">'+
	      '<div id="siteNotice">'+
	      '</div>'+
	      '<h1 id="firstHeading" class="firstHeading">'+to+'</h1>'+
	      '<div id="bodyContent">'+
	      '<p><b>'+data['message']+'</b></p>' +
	      status_msg +
	      '<p>Reported by '+from+'</p><BR>' +
	      '</div>'+
	      '</div>';

		var myLatlng;
		if (data['gps_latitude'] != null && data['gps_longitude'] != null) 
			myLatlng = new google.maps.LatLng(data['gps_latitude'],
					data['gps_longitude']);
		else if (data['origin_node'] in node_markers)
			myLatlng = node_markers[data['origin_node']].getPosition();
		else
			return;
		
		var infowindow = new google.maps.InfoWindow({
			content: contentString,
		});
		var marker = new google.maps.Marker({
			position: myLatlng,
			map: map,
			title: 'Message'
		});
		infowindow.open(map,marker);

		// Timeout in X seconds
		setTimeout(function() {
			marker.setMap(null);
			infowindow.close();
		},5000);
	}
	
}

function initialize() {
  console.log("Initializing");

  // TODO intelligent centering of map based on our data points
  var myLatlng = new google.maps.LatLng(42.359048, -71.093599);
  var mapOptions = {
    zoom: 17,
    center: myLatlng
  };
  
  map = new google.maps.Map(document.getElementById('map-canvas'), mapOptions);

	for (node_id in messages_data) {
		if (mesh_data[node_id].length == 0)
			continue;
		for (mid in messages_data[node_id]) {
			
 			
		}
		break;
		
	}
  refreshIntervalId = setInterval(updateData,50);

}


var loc6 = new google.maps.LatLng(42.356844, -71.098681);

// Listeners that add or remove classes of nodes  

// Add a Node marker to the map and push to the array.
function addNodeMarker(markerInfo) {

   var infowindow = new google.maps.InfoWindow({
     content: markerInfo.contentString
  });

  var marker = new google.maps.Marker({
    position: markerInfo.location,
    map: null,
    icon: node_icon,
    title: markerInfo.title
  });

  google.maps.event.addListener(marker, 'mouseover', function() {
    infowindow.open(map,marker);
  });

  google.maps.event.addListener(marker, 'mouseout', function() {
    infowindow.close();
  });

  node_markers.push(marker);
}



google.maps.event.addDomListener(window, 'load', initialize);

    </script>
  </head>
  <body>
    <div id="timestamp">Jan 1, 2015 @ blah pm</div>
    <div id="map-canvas"></div>
  </body>
</html>
