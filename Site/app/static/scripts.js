//MAP CODE
var map;
var geocoder;
var infowindow
var map_center = {
  lat: 53.34481,
  lng: -6.266209
};
var zoom_level = 13.5;
var toggle_markers=1;
var toggle_heatmap=0;

var table_info_content = `
<table id="information-table">
<thead>
    <h2 id="station">Dublin Bikes</h2>
    <hr style="width: 40%">
</thead>
<tbody>
  <tr>
    <td>
      <h3 style ="margin-bottom: 10px;">
        Weather
      </h3>
    </td>
    <td>
      <h3>
        Status:
      </h3>
    </td>
    <td>
      <p id="status">
        Open
      </p>
    </td>
  </tr>
  <tr>
    <td rowspan="2">
        <p>
          <canvas id = "weathericon" class="clear-day" width="50" height="50"></canvas>
        </p>
    </td>
    <td>
      <h3>
        Available Bikes:
      </h3>
    </td>
    <td>
      <p id ="avbikes">
        Loading...
      </p>
    </td>
  </tr>
  <tr>
    <td>
      <h3>
        Available Stands
      </h3>
    </td>
    <td>
      <p id ="avstands">
        Loading...
      </p>
    </td>
  </tr>
</tbody>
</table>
`
var find_station_inner_html = `
<h3 style="text-align: center; color: white; font-size: 20pt; padding-top:20px; margin-bottom:0;padding-bottom:0;"> 
  Find Station 
</h3><br>
<hr style="width:50%;margin-top:0;margin-bottom:30px;">
<p>
  Station Number:<br>
  <select id="station_number_find" onchange=find_by_number()>
    <option value='default'>All</option>
  </select>
  <script>populate_station_number_dropdown();</script>
</p>
<br>
<p>
  Station Address:<br>
  <select id="station_name_find" onchange=find_by_name()>
    <option value='default'>Search</option>
  </select>
</p>
<script>populate_station_name_dropdown();</script>

<button id="find_nearest_station_button" onclick="find_nearest_station();">Find Nearest Station</button>
`;

var Forecast_content_inner_html = `
<div id="Forecast_content_inner_html">
<h3 style="text-align: center; color: white; font-size: 20pt; padding-top:20px; margin-bottom:0;padding-bottom:0;">
Sample Content
</h3><br>

<img src="../static/images/WeekendAverage.png" alt="Weekend Average">
<img src="../static/images/WeekdayAverage.png" alt="Weekend Average">

</div>
`;


var graph_content_inner_html = `
<h3 style="text-align: center; color: white; font-size: 20pt; padding-top:20px; margin-bottom:0;padding-bottom:0;">
Under Construction
</h3><br>
`;

function initMap() {
    directionsService = new google.maps.DirectionsService();
    directionsDisplay = new google.maps.DirectionsRenderer();
    infowindow = new google.maps.InfoWindow();
    geocoder = new google.maps.Geocoder;
    var latlng = new google.maps.LatLng(53.34481, -6.266209);
    map = new google.maps.Map(document.getElementById('map'), {
        zoom: 13.5,
        center: latlng,
        mapTypeId: 'terrain'
    });
    directionsDisplay.setMap(map);

    if (toggle_markers==1) {
      showStationMarkers();
    }
    else if (toggle_heatmap) {
      console.log("HEATMAP")
    }
    else {
      console.log("NO MARKERS")
    }

}

//Write in pins - source: Slides "WebDev"
 function showStationMarkers(data) {
  var iconBase = 'https://maps.google.com/mapfiles/kml/shapes/';
  $.getJSON('../static/localjson.json', null, function(data) {
    data = data["features"]
    var allMarkers = [];
    rackdata = fulllookup();
    for (x in data){
      
      var y = data[x].properties.number;

      allMarkers[y] = new google.maps.Marker({
        position : {lat : data[x]["geometry"]["coordinates"]["1"],
        lng : data[x]["geometry"]["coordinates"]["0"]},
        map : map,
        name : data[x]["properties"]["name"],
        number : data[x]["properties"]["number"],
        icon: {url: "http://maps.google.com/mapfiles/ms/icons/green-dot.png"}
      });

      for (p in allMarkers){
          if (rackdata[p].bikes == 0){
              allMarkers[p].icon.url = "http://maps.google.com/mapfiles/ms/icons/red-dot.png"
          }
          else if (rackdata[p].bikes < 10){
              allMarkers[p].icon.url = "http://maps.google.com/mapfiles/ms/icons/orange-dot.png"
          }
          else{
              allMarkers[p].icon.url = "http://maps.google.com/mapfiles/ms/icons/green-dot.png"
          }
      }

      allMarkers[y].addListener("click", function() {
        var stationname = this["name"];
        var stationnumber = this["number"];
        $("#infoboxcontent").html(table_info_content);
        $("#map").css("width","65%");
        $("#infobox").css("width","35%");
        $("#infobox").css("visibility","visible");
        $("#station").text(stationname);
        $("#avbikes").text("Loading...");
        $("#avstands").text("Loading...");
        $("#menu_item_1").text("Close");
        map.panBy(0, 0);
        document.getElementById("avstands").innerHTML = rackdata[stationnumber].stands
        document.getElementById("avbikes").innerHTML = rackdata[stationnumber].bikes
        document.getElementById("status").innerHTML = rackdata[stationnumber].status
        $("#weathericon").attr("class", rackdata[stationnumber].weather_icon);
        SkyCon();
        var destination = this.position.lat() +"," +this.position.lng();
        getPosition(destination);

      });
    }
  });
}

// handles dropdown menu
function clickHandler(val) {
  if (val == 1) {

    if ($("#menu_item_1").text()=="Close"){
      $("#menu_item_1").text("Find Station");
      $("#map").css("width", "100%");
      $("#infobox").css("width", "0%");
      $("#infobox").css("visibility", "hidden");
      document.documentElement.scrollTop = 0;
      
    } else {
      $("#menu_item_1").text("Close");
      $("#map").css("width", "70%");
      $("#infobox").css("width", "30%");
      $("#infobox").css("visibility", "visible");
      $("#infoboxcontent").html(find_station_inner_html)
    }
  } 
  else if (val == 2) {
    $("#menu_item_1").text("Close");
    $("#map").css("width", "70%");
    $("#infobox").css("width", "30%");
    $("#infobox").css("visibility", "visible");
    $("#infoboxcontent").html(graph_content_inner_html);
  } 
  else if (val == 3) {
    $("#menu_item_1").text("Close");
    $("#map").css("width", "70%");
    $("#infobox").css("width", "30%");
    $("#infobox").css("visibility", "visible");
    $("#infoboxcontent").html(Forecast_content_inner_html);
  }
}

function standinfo(stand) {
  xmlhttp = new XMLHttpRequest();
  xmlhttp.onreadystatechange = function () {
    if (this.readyState == 4 && this.status == 200) {
      //Writes query to HTML - allows for interactivity on page
      document.getElementById("avstands").innerHTML = JSON.parse(this.responseText)[0];
      document.getElementById("avbikes").innerHTML = JSON.parse(this.responseText)[1];
      $("#weathericon").attr("class", JSON.parse(this.responseText)[3]);
      SkyCon()
    }
  };
  xmlhttp.open("GET", "/lookup?id=" + stand, true);
  xmlhttp.send();
}

function calcRoute(start, end) {
  var request = {
    origin: start,
    destination: end,
    travelMode: 'WALKING'
  };
  directionsService.route(request, function(result, status) {
    if (status == 'OK') {
      directionsDisplay.setDirections(result);
    }
  });
}

function getPosition(ending) {
  navigator.geolocation.getCurrentPosition(
    function success(position) {
    // for when getting location is a success
    var userlocation = (position.coords.latitude + "," + position.coords.longitude);
    calcRoute(userlocation,ending);
    console.log(userlocation)
  return userlocation;
  });
}

function fulllookup(){
        var fullinfo
      xmlhttp = new XMLHttpRequest();
      xmlhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            testvar = JSON.parse(this.responseText)
            $("#contentwindow").css("visibility","visible");
            $("#loadingwindow").css("visibility","hidden");
            $("#loadingwindow").css("height","0%");
            $("#loadingwindow").css("width","0%");
            $("#contentwindow").css("height","70%");
            $("#contentwindow").css("width","100%");
            return testvar;

        }
  };

  xmlhttp.open("GET", "/fulllookup", false);
  xmlhttp.send();
    return xmlhttp.onreadystatechange();
}

function SkyCon() {
  var i;

  var icons = new Skycons({
      "color": "#ffffff"
    });

  var list = [
      "clear-day", "clear-night", "partly-cloudy-day",
      "partly-cloudy-night", "cloudy", "rain", "sleet", "snow", "wind",
      "fog"
    ]

  for (i = list.length; i--;) {
    var weatherType = list[i],
      elements = document.getElementsByClassName(weatherType);
    for (e = elements.length; e--;) {
      icons.set(elements[e], weatherType);
    }
  }

  icons.play();
}
SkyCon()

function heatmap(state) {

  console.log(state);

  if (state == 1) {
      // turn on heatmap

      map = new google.maps.Map(document.getElementById('map'), {
        center: {
          lat: 53.34481,
          lng: -6.266209
        },
        zoom: 13.5,
        mapTypeId: 'satellite'
      });

      var heatmap = new google.maps.visualization.HeatmapLayer({
        data: getPoints(),
        map : map
      });
      console.log(getPoints());
      heatmap.setMap(map);

  } else {
    // redraw original map
    initMap();
  }

}

function get_Points(){

  var map_data = [];
  var file="../static/localjson.json";

  $.getJSON(file,
    function(data){

      for (var i=0; i<data.features.length; i++){

        var lng = data.features[i].geometry.coordinates[0];
        var lat = data.features[i].geometry.coordinates[1];
        var station_number = data.features[i].properties.number;

        // add data to array for sending to heatmap. replace station number with n_bikes.
        // var str_ = new google.maps.LatLng(lat, lng);
        console.log(lat); console.log(53.782745);
        map_data.push(new google.maps.LatLng(parseFloat(lat), parseFloat(lng)));
      }

    console.log(map_data);

    return map_data[0];
  });
};

function getPoints() {
  return [
    new google.maps.LatLng(53.782745, -6.444586),
    new google.maps.LatLng(53.782842, -6.443688),
    new google.maps.LatLng(53.782919, -6.442815),
    new google.maps.LatLng(53.782551, -6.445368),
    new google.maps.LatLng(53.782992, -6.442112),
    new google.maps.LatLng(53.783100, -6.441461)
  ];
}

function populate_station_number_dropdown(){

  drpdwn = document.getElementById('station_number_find');

  $.getJSON("../static/localjson.json", function(data){

      for (var i=0; i<data.features.length; i++){
        var station_number = data.features[i].properties.number;

        var option = document.createElement("OPTION");
        option.textContent=station_number;
        option.value=station_number;
        drpdwn.appendChild(option);
      }
    }
  );
}

function populate_station_name_dropdown(){

  name_drpdwn = document.getElementById('station_name_find');

  $.getJSON("../static/localjson.json", function(data){

      for (var i=0; i<data.features.length; i++){
        
        var name = data.features[i].properties.name;

        var name_option = document.createElement("OPTION");
        name_option.textContent=name;
        name_option.value=name;
        name_drpdwn.appendChild(name_option);
      }
    }
  );
}

// Redefine this function to make a popup info box over the marker on pan to center.
function split_window_info(stationname, stationnumber) {

  $("#map").css("width","70%");
  $("#infobox").css("width","30%");
  $("#infobox").css("visibility","visible");

  $("#station").text(stationname);
  $("#avbikes").text("Loading...");
  $("#avstands").text("Loading...");

  marker.icon.url ="http://maps.google.com/mapfiles/ms/icons/blue-dot.png";
  map.panBy(0, 0);
  standinfo(stationnumber);
}

function find_by_number(){
  // find station by number from localjson

  var sn = document.getElementById("station_number_find").value;
  var sname = document.getElementById("station_name_find")
  // bring up information on the stations. (activate click event)
  // standinfo(sn);

  if (sn=='default'){
    initMap();
    sname.text='Search';
    sname.value='default';
  }
  else {
    $.getJSON("../static/localjson.json",
      function(data){

        for (var i=0; i<data.features.length; i++){

          var lng = data.features[i].geometry.coordinates[0];
          var lat = data.features[i].geometry.coordinates[1];
          var stationname = data.features[i].properties.name;
          var station_number = data.features[i].properties.number;

          if (station_number == sn) {

            map.panTo(new google.maps.LatLng(lat, lng));
            map.setZoom(17);

            // split_window_info(stationname, station_number);
            sname.value = stationname;
            sname.text = stationname;
            
            // need to minimise the search window here. !important.
          }
        }
      }
    );
  }
}

function find_by_name() {

  sname = document.getElementById("station_name_find").value;
  sn = document.getElementById("station_number_find");

  if (sname=='default'){
    initMap();
  }
  else {
    $.getJSON("../static/localjson.json",
      function(data){

        // loop thorugh data to find correct station number then set number of station and call find by number.

        for (var i=0; i<data.features.length; i++){
          var stationname = data.features[i].properties.name;
          var station_number = data.features[i].properties.number;

          if (stationname == sname){

            sn.value=station_number;
            $("station_number_find").text(station_number);
            find_by_number();

          }
        }
      }
    );
  }
}

function find_nearest_station() {
  
  var minlat, minlng;
  var mindist=10000000000.0;
  var x = navigator.geolocation.getCurrentPosition(
    function success(position) {

    var lat1 = position.coords.latitude;
    var lng1 = position.coords.longitude;

    $.getJSON("../static/localjson.json",
      function(data){

        for (var i=0; i<data.features.length; i++){

          var lng2 = data.features[i].geometry.coordinates[0];
          var lat2 = data.features[i].geometry.coordinates[1];
          var dist = distance_between_latlng (lat1,lat2,lng1,lng2);

          if (dist < mindist) {
            mindist = dist;
            minlat = lat2;
            minlng = lng2;
          }
        }
        console.log(mindist,minlng,minlat);
        var pos1 = (lat1 + "," + lng1);
        var pos2 = (lat2 + "," + lng2);
        calcRoute(pos1, pos2);
      }
    );
  });
}

function distance_between_latlng (lat1, lat2, lng1, lng2) {

  dx = lat1 - lat2;
  dy = lng1 - lng2;

  distance =  Math.sqrt((dx*dx) + (dy*dy));

  return distance;
}