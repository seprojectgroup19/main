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
var toggle_marker_color=1;
var toggle_empty_marker=0;

var table_info_content = `
  <table id="information-table">
      <thead>
          <h2 id="station">Dublin Bikes</h2>
          <hr style="width: 40%">
      </thead>
      <tbody>
        <tr>
          <td colspan="3">
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
          <td colspan="3">
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
          <td colspan="3">
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
  `;

var find_station_inner_html = `
<h3 style="text-align: center; color: white; font-size: 20pt; padding-top:10px; margin-bottom:0;padding-bottom:0;"> 
  Find Station 
</h3>
<hr style="width:50%;margin-top:0;margin-bottom:30px;">
<div style="width:80%; margin:auto;">
  <p>
    Station Number:<br>
    <select id="station_number_find" onchange=find_by_number()>
      <option value='default'>All</option>
    </select>
  </p>
    <br>
  <p>
    Station Address:<br>
    <select id="station_name_find" onchange=find_by_name()>
     <option value='default'>Search</option>
    </select>
  </p>
  <script>populate_station_number_dropdown();</script>
  <script>populate_station_name_dropdown();</script>
</div>
<button id="find_nearest_station_button" onclick="find_nearest_station();">Find Nearest Station</button>
`;

var graph_content_inner_html = `
<h3 style="text-align: center; color: white; font-size: 20pt; padding-top:10px; margin-bottom:0;padding-bottom:0;"> 
  Graphs
</h3>
<hr style="width:50%;margin-top:0;margin-bottom:30px;">
<!-- Insert select option here to generate graph -->
<div id="Graph_Content_div">

  <table>
    <tr>
      <td>
      Select station:
      </td>
      <td>
      <select id="station_number_graph_options">
        <option value='default'>Station</option>
      </select>
      </td>
      <td rowspan="4" style="position:relative;">
      <button id="submit" onclick="get_chart_data()">Generate<br>Graphs</button>
      </td>

    </tr>
    <script>populate_graph_options()</script>

    <tr>
      <td>
      Select Time Period:
      </td>
      <td>
      <select id='graph_days' onchange="chart_type_predictions()">
        <option value='default'>Time</option>
        <option value='-0.5'>Last 12 Hrs</option>
        <option value='-1'>Last Day</option>
        <option value='-7'>Last 7 Days</option>
        <option value='0.5'>Next 12 Hrs</option>
        <option value='1'>Next Day</option>
        <option value='7'>Next 7 Days</option>
      </select>
      </td>
    </tr>

    <tr>
      <td>
      Select Variable:
      </td>
      <td>
      <select id='graph_variable'>
        <option value='default'>Variable</option>
        <option value='stand'>Stands</option>
        <option value='bike'>Bikes</option>
        <option value='both'>Both</option>
      </select>
      </td>
    </tr>

    <tr>
      <td>
        Select Chart type:
      </td>
      <td>
        <select id='chart_type'>
          <option value='default'>Type</option>
          <option value='line'>Line Chart</option>
          <option value='bar'>Bar Chart</option>
          <option value='area'>Area Chart</option>
          <option value='scatter'>Scatter Chart</option>
        </select>
      </td>
    </tr>
  </table>

  <div id="graph_error_message" style="clear:both"></div>

</div>
<div id="chart_div"></div>
`;


var Forecast_content_inner_html = `
<h3 style="text-align: center; color: white; font-size: 20pt; padding-top:10px; margin-bottom:0;padding-bottom:0;"> 
  Forecast
</h3>
<hr style="width:50%;margin-top:0;margin-bottom:30px;">
<div style="width:80%; text-align: left; margin:auto; color:whitesmoke">
  <div id="forecast_form">
    Select Day:
    <select id='time_pred'>f
      <option value='default'>Day</option>
      <option value="Mon">Monday</option>
      <option value="Tue">Tuesday</option>
      <option value="Wed">Wednesday</option>
      <option value="Thu">Thursday</option>
      <option value="Fri">Friday</option>
      <option value="Sat">Saturday</option>
      <option value="Sun">Sunday</option>
    </select><br>
    
    Select Time:
    <select id="hour_forecast_options">
    <option value='default'>Hour</option>
    </select><br>

    Select station:
    <select id="station_number_forecast_options">
      <option value='default'>Station</option>
    </select><br>

    
    
    <!-- populate options -->
    <script>populate_forecast_options()</script>
    
    <button id="submit" onclick="Forecast()">Get Prediction</button>
    
    <div id="forecasts_message" style="clear:both"></div>
    
    <table id="Forecast_Content">
      <tr>
        <td>Available Bikes:</td>
        <td id="avail_b_forecast"></td>
      </tr>
      <tr>
        <td>Available Stands:</td>
        <td id="avail_s_forecast"></td>
      </tr>
    </table>
  </div>
</div>
`;

function Forecast() {

  // send the day and time. 
  var day = document.getElementById("time_pred").value;
  var hour = document.getElementById("hour_forecast_options").value;
  var snum = document.getElementById("station_number_forecast_options").value;
  var test=true;

  xmlhttp = new XMLHttpRequest();
  xmlhttp.onreadystatechange = function () {
    if (this.readyState == 4 && this.status == 200) {
      
      var data = JSON.parse(this.responseText);
      var nbikes = Math.round(parseFloat(data[0]));
      var nstands = Math.round(parseFloat(data[1]));

      $("#Forecast_Content").css("display","block");
      $("#avail_b_forecast").text(nbikes);
      $("#avail_s_forecast").text(nstands - nbikes);
      console.log(data);
    }
  };

  if (day=='default'){
    $("#forecasts_message").text("* The above fields are required.");
    $("#forecasts_message").css("display","block");
    $("#time_pred").css('color','red');
    test=false;
  } 
  else {
    $("#time_pred").css("color","black");
  }

  if (hour=='default'){
    $("#forecasts_message").text("* The above fields are required.");
    $("#forecasts_message").css("display","block");
    $("#hour_forecast_options").css('color','red');
    test=false;
  } 
  else {
    $("#hour_forecast_options").css("color","black");
  }

  if (snum=='default'){
    $("#forecasts_message").text("* The above fields are required.");
    $("#forecasts_message").css("display","block");
    $("#station_number_forecast_options").css('color','red');
    test=false;
  } 
  else {
    $("#station_number_forecast_options").css("color","black");
  }

  // check that the inputs are valid.
  if (!test) 
    return
  else {
    $("#forecasts_message").css("display","none");
    $("#forecasts_message").text("");
  }

  xmlhttp.open("GET", "/model_prediction?Day="+day+"&Time="+hour+"&Station="+snum, true);
  xmlhttp.send();
  }

var map;
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

var allMarkers = [];
//Write in pins - source: Slides "WebDev"
 function showStationMarkers(data) {
  var iconBase = 'https://maps.google.com/mapfiles/kml/shapes/';
  $.getJSON('../static/localjson.json', null, function(data) {
    data = data["features"]
    rackdata = fulllookup();
    for (x in data){
      var y = data[x].properties.number
      allMarkers[y] = new google.maps.Marker({
        position : {lat : data[x]["geometry"]["coordinates"]["1"],
        lng : data[x]["geometry"]["coordinates"]["0"]},
        map : map,
        name : data[x]["properties"]["name"],
        number : data[x]["properties"]["number"],
        icon: {url: "http://maps.google.com/mapfiles/ms/icons/green-dot.png"},
        avbikes: rackdata[y].bikes,
        avstands: rackdata[y].stands
      });

      if (toggle_marker_color==1) {
        for (p in allMarkers){
            if (rackdata[p].bikes == 0){
                allMarkers[p].icon.url = "../static/images/markers/red-dot.png"
            }
            else if (rackdata[p].bikes < 10){
                allMarkers[p].icon.url = "../static/images/markers/orange-dot.png"
            }
            else{
                allMarkers[p].icon.url = "../static/images/markers/green-dot.png"
            }
        } 
      }else{
        for (p in allMarkers){
          allMarkers[p].icon.url = "http://maps.google.com/mapfiles/ms/icons/red-dot.png";
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
      
        var destination = this.position.lat() +"," +this.position.lng();
        getPosition(destination);

      });
    }
  });
}

function weather_update() {

  xmlhttp = new XMLHttpRequest();
  xmlhttp.onreadystatechange = function () {
    if (this.readyState == 4 && this.status == 200) {
      
      var data = JSON.parse(this.responseText)[0];
      var last_update_time = new Date(data[14] * 1000);

      $("#weathericon").attr("class", JSON.parse(this.responseText)[0][5]);
      $("#Conditions").text(data[12]);
      $('#Temperature').text("");
      $('#Temperature').unbind().append(data[13] + ' &#8451;');
      $("#WindSpeed").text(data[19] + " km/h");
      $("#Humidity").text(100*data[4] + "%");
      $("#Precipitation").text(100*data[9] + "%");

      // Formatting output string. 
      var hours = ((last_update_time.getHours()<10) ? "0" : "") + last_update_time.getHours();
      var minutes = ((last_update_time.getMinutes()<10) ? "0" : "") + last_update_time.getMinutes();  

      $("#UpdateTime").text(hours + ":" + minutes);

      SkyCon();
    }
  };
  xmlhttp.open("GET", "/get_weather_update", true);
  xmlhttp.send();

  // sleep 5 mins then update again. 
  setTimeout(weather_update,300000);
}
weather_update();

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
    $("#infoboxcontent").html(Forecast_content_inner_html);
  } 
  else if (val == 3) {
    $("#menu_item_1").text("Close");
    $("#map").css("width", "55%");
    $("#infobox").css("width", "45%");
    $("#infobox").css("visibility", "visible");
    $("#infoboxcontent").html(graph_content_inner_html);
  }
}

function standinfo(stand) {
  xmlhttp = new XMLHttpRequest();
  xmlhttp.onreadystatechange = function () {
    if (this.readyState == 4 && this.status == 200) {
      //Writes query to HTML - allows for interactivity on page
      document.getElementById("avstands").innerHTML = JSON.parse(this.responseText)[0];
      document.getElementById("avbikes").innerHTML = JSON.parse(this.responseText)[1];
    }
  };
  xmlhttp.open("GET", "/lookup?id=" + stand, true);
  xmlhttp.send();
}

//Function updates marker mode - Different visuals for accessibility
var marker_mode_toggle = false;
function toggle_marker_mode(){
    if (marker_mode_toggle == false){
        console.log("on")
        marker_mode_toggle = true;
            //If not toggled, will change map markers to visual counterparts
                for (p in allMarkers){
            if (allMarkers[p].avbikes == 0){
                allMarkers[p].icon.url = "../static/images/markers/letter_x.png"
                allMarkers[p].setMap(null);
                allMarkers[p].setMap(map);
            }
            else if (allMarkers[p].avbikes < 10){
                allMarkers[p].icon.url = "../static/images/markers/number_1.png"
                allMarkers[p].setMap(null);
                allMarkers[p].setMap(map);
            }
            else{
                allMarkers[p].icon.url = "../static/images/markers/number_10.png"
                allMarkers[p].setMap(null);
                allMarkers[p].setMap(map);
            }
        };
    }else{
        console.log("off")
        marker_mode_toggle = false;
        for (p in allMarkers){
            if (allMarkers[p].avbikes == 0){
                allMarkers[p].icon.url = "../static/images/markers/red-dot.png";
                allMarkers[p].setMap(null);
                allMarkers[p].setMap(map);
            }
            else if (allMarkers[p].avbikes < 10){
                allMarkers[p].icon.url = "../static/images/markers/orange-dot.png";
                allMarkers[p].setMap(null);
                allMarkers[p].setMap(map);
            }
            else{
                allMarkers[p].icon.url = "../static/images/markers/green-dot.png";
                allMarkers[p].setMap(null);
                allMarkers[p].setMap(map);
            }
        };


    }


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
  return userlocation;
  });
}

function fulllookup(){
  var fullinfo;
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
    var weatherType = list[i];
    var elements = document.getElementsByClassName(weatherType);
    for (e = elements.length; e--;) {
      icons.set(elements[e], weatherType);
    }
  }
  icons.play();
}
SkyCon()

function heatmap(state) {
  if (state == 1) {
      // turn on heatmap
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
    return map_data[0];
  });
};

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
  var station_no;

  var x = navigator.geolocation.getCurrentPosition(
    function success(position) {

    var lat1 = position.coords.latitude;
    var lng1 = position.coords.longitude;

    $.getJSON("../static/localjson.json",
      function(data){

        for (var i=0; i<data.features.length; i++){

          var lng2 = data.features[i].geometry.coordinates[0];
          var lat2 = data.features[i].geometry.coordinates[1];
          station_no = data.features[i].properties.number;

          var dx = lat1 - lat2;
          var dy = lng1 - lng2;
          var dist =  Math.sqrt((dx*dx) + (dy*dy));

          if (dist < mindist) {
            mindist = dist;
            minlat = lat2;
            minlng = lng2;
          }
        }
        var pos1 = (lat1 + "," + lng1);
        var pos2 = (minlat + "," + minlng);
        calcRoute(pos1, pos2);

        document.getElementById("station_number_find").value=station_no;
        $("station_number_find").text(station_no);
        find_by_number();
      }
    );
  });
}

function toggle_map_colours(){
  if (toggle_marker_color==0) {
    // change marker colour here.    
    toggle_marker_color=1;
    initMap();
  }else{
    toggle_marker_color=0;
    initMap();
  }
}

var arrow_direction=0;
function flip_menu() {
  if (arrow_direction==0){
    $("#menu_arrow").css({
      "width":"10px",
      "height":"15px",
      "transform":"rotate(270deg)"
    });
    arrow_direction=1;
    $(".dropdown-content").css("height", "0%");
    $(".dropdown-content").css("visibility", "hidden");
  }
  else {
    $("#menu_arrow").css({
      "width":"10px",
      "height":"15px",     
      "transform":"rotate(90deg)"
    });
    arrow_direction=0;
    $(".dropdown-content").css("height", "140px");
    $(".dropdown-content").css("visibility", "visible");
  }
}

function populate_forecast_options() {

  drpdwn = document.getElementById('station_number_forecast_options');
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
  hrdrpdwn = document.getElementById('hour_forecast_options');
  for (var hr=0; hr <= 23; hr++) {
    var optionhr = document.createElement("OPTION");
    optionhr.textContent= ((hr < 10) ? "0" : "") + hr + ":00";
    optionhr.value=hr;
    hrdrpdwn.appendChild(optionhr);
  }
}

function populate_graph_options() {
  drpdwn = document.getElementById('station_number_graph_options');
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

// Function to generate charts
function get_chart_data() {
            
  var Days = parseFloat(document.getElementById("graph_days").value);

  // var resultion = document.getElementById("graph_resolution").value; // NOTE: THIS NEED TO BE ADDED TO THE CHART AS A BUTTON!
  var station = document.getElementById("station_number_graph_options").value;
  var plot_type =  document.getElementById("chart_type").value;
  var g_vars = document.getElementById("graph_variable").value;

  xmlhttp = new XMLHttpRequest();
  xmlhttp.onreadystatechange = function () {
      if (this.readyState == 4 && this.status == 200) {
      
          var data = JSON.parse(this.responseText);
          
          //As,Ab,Ts
          if (Days < 0) {

            var As = data[0];
            var Ab = data[1];
            var Ts = data[2];

            var aSTS = [['TimeStamp','AvailableStands']];
            var aBTS = [['TimeStamp','AvailableBikes']];
            var MultiPlot=[['TimeStamp','AvailableBikes','AvailableStands']];

            for (var i=0; i<As.length; i++){
              AStand = Math.round(parseFloat(Ab[i]));
              ABikes = Math.round(parseFloat(As[i]));
              aBTS.push([new Date(Ts[i]),AStand]);
              aSTS.push([new Date(Ts[i]),ABikes]);
              MultiPlot.push([new Date(Ts[i]),ABikes,AStand]);
            }
          } else {

            console.log(data)
            var aSTS = [['TimeStamp','AvailableStands']];
            var aBTS = [['TimeStamp','AvailableBikes']];
            var MultiPlot=[['TimeStamp','AvailableBikes','AvailableStands']];

            for (var i=0; i < data[0].length; i++){

              Ts = data[0][i].time;
              Ab =  Math.round(parseFloat(data[0][i].bike));
              As =  Math.round(parseFloat(data[1]) - Ab);

              aBTS.push([new Date(Ts),Ab]);
              aSTS.push([new Date(Ts),As]);
              MultiPlot.push([new Date(Ts),Ab,As]);
            }
          }

          // Load the Visualization API and the corechart package.
          google.charts.load('current', {'packages':['corechart']});

          // Set a callback to run when the Google Visualization API is loaded.
          google.charts.setOnLoadCallback(drawChart);

          // Callback that creates and populates a data table,
          // instantiates the pie chart, passes in the data and
          // draws it.
          function drawChart() {

            // Create the data table.
            var Sdata = new google.visualization.arrayToDataTable(aSTS);
            var Bdata = new google.visualization.arrayToDataTable(aBTS);
            var Both =  new google.visualization.arrayToDataTable(MultiPlot);

            // Plot_Data = Both;
            switch (g_vars) {
              case "bike": Plot_Data=Bdata;break;
              case "stand": Plot_Data=Sdata;break;
              case "both" : Plot_Data=Both; break;
              default: Plot_Data=Both;break;
            }

            // Set chart options
            var Lineoptions = {
                'title': 'Last '+24*Days+' Hrs Information on station '+ station,
                'chartArea': {'width': '90%', 'height': '70%'},
                lineWidth:5,
                backgroundColor: { fill:'transparent' },
                legend: {position: 'top', maxLines: 3},
                vAxis: {gridlines: {color: 'transparent'}, textStyle:{color: '#FFF'}},
                hAxis: {gridlines: {color: 'transparent'}, textStyle:{color: '#FFF'}},
                explorer: {
                  keepInBounds: true,
                  actions: ['dragToZoom', 'rightClickToReset']
                },
                'height':400,
                'width':'100%'
            };

            var Columnoptions = {
              'title': 'Last '+24*Days+' Hrs Information on station '+ station,
              'chartArea': {'width': '90%', 'height': '70%'},
              isStacked:true,
              'stroke-width':4,
              backgroundColor: { fill:'transparent' },
              legend: {position: 'top', maxLines: 3},
              vAxis: {gridlines: {color: 'transparent'}, textStyle:{color: '#FFF'}},
              hAxis: {gridlines: {color: 'transparent'}, textStyle:{color: '#FFF'}},
              explorer: {
                keepInBounds: true,
                actions: ['dragToZoom', 'rightClickToReset']
              },
              'height':400,
              'width':'100%'
            };

            var Scatteroptions = {
              'title': 'Last '+24*Days+' Hrs Information on station '+ station,
              'chartArea': {'width': '90%', 'height': '70%'},
              backgroundColor: { fill:'transparent' },
              legend: {position: 'top', maxLines: 3},
              vAxis: {gridlines: {color: 'transparent'}, textStyle:{color: '#FFF'}},
              hAxis: {gridlines: {color: 'transparent'}, textStyle:{color: '#FFF'}},
              explorer: {
                keepInBounds: true,
                actions: ['dragToZoom', 'rightClickToReset']
              },
              'height':400,
              'width':'100%'
            };

            var Areaoptions = {
              'title': 'Last '+24*Days+' Hrs Information on station '+ station,
              'chartArea': {'width': '90%', 'height': '70%'},
              backgroundColor: { fill:'transparent' },
              legend: {position: 'top', maxLines: 3},
              vAxis: {gridlines: {color: 'transparent'}, textStyle:{color: '#FFF'}},
              hAxis: {gridlines: {color: 'transparent'}, textStyle:{color: '#FFF'}},
              explorer: {
                keepInBounds: true,
                actions: ['dragToZoom', 'rightClickToReset']
              },
              'height':400,
              'width':'100%'
            };

            // change plot type
            switch (plot_type){

              case 'line': var chart = new google.visualization.LineChart(document.getElementById('chart_div'));
              chart.draw(Plot_Data, Lineoptions);
              break;

              case 'area': var chart = new google.visualization.AreaChart(document.getElementById('chart_div'));
              chart.draw(Plot_Data, Areaoptions);
              break;

              case 'scatter': var chart = new google.visualization.ScatterChart(document.getElementById('chart_div'));
              chart.draw(Plot_Data, Scatteroptions);
              break;
              
              case 'bar': var chart = new google.visualization.ColumnChart(document.getElementById('chart_div'));
              chart.draw(Plot_Data, Columnoptions);
              break;

              default: var chart = new google.visualization.AreaChart(document.getElementById('chart_div'));
              chart.draw(Plot_Data, Areaoptions);
              break;

            }
          }
      }
  };

  var Days = document.getElementById("graph_days").value;
  // var resultion = document.getElementById("graph_resolution").value; // NOTE: THIS NEED TO BE ADDED TO THE CHART AS A BUTTON!
  var station = document.getElementById("station_number_graph_options").value;
  var plot_type =  document.getElementById("chart_type").value;
  var g_vars = document.getElementById("graph_variable").value;

  var test=true;

  if (Days=='default') {
    $("#graph_error_message").text("* The above fields are required.");
    $("#graph_error_message").css("display","block");
    $("#graph_days").css('color','red');
    test=false;
  }
  else {
    $("#graph_days").css("color","black");
  }

  if (station=='default') {
    $("#graph_error_message").text("* The above fields are required.");
    $("#graph_error_message").css("display","block");
    $("#station_number_graph_options").css('color','red');
    test=false;
  }
  else {
    $("#station_number_graph_options").css("color","black");
  }

  if (plot_type=='default') {
    $("#graph_error_message").text("* The above fields are required.");
    $("#graph_error_message").css("display","block");
    $("#chart_type").css('color','red');
    test=false;
  }
  else {
    $("#chart_type").css("color","black");
  }

  if (g_vars=='default') {
    $("#graph_error_message").text("* The above fields are required.");
    $("#graph_error_message").css("display","block");
    $("#graph_variable").css('color','red');
    test=false;
  }
  else {
    $("#graph_variable").css("color","black");
  }

  if (!test)
    return
  else {
    $("#graph_error_message").css("display","none");
    $("#graph_error_message").text("");
  }

  if (Days < 0) {
    var resolution=60;
    var request_string = "/make_charts?Days="+(-1*Days)+"&Station="+station +"&TimeStep="+resolution;
  }
  else {
    var request_string = "/fullmodelgraph?TimeFrame="+Days+"&Station="+station;
  }
  xmlhttp.open("GET", request_string, true);
  xmlhttp.send();
}
<<<<<<< HEAD
=======

function chart_type_predictions() {
  var Days = document.getElementById("graph_days").value;

  var original_html = `
      <option value='default'>Type</option>
      <option value='line'>Line Chart</option>
      <option value='bar'>Bar Chart</option>
      <option value='area'>Area Chart</option>
      <option value='scatter'>Scatter Chart</option>
  `

  var new_html = `
    <option value='default'>Type</option>
    <option value='bar'>Bar Chart</option>
    <option value='scatter'>Scatter Chart</option>
  `

  if (parseFloat(Days) > 0) {
    document.getElementById("chart_type").innerHTML=new_html;
  } else {
    document.getElementById("chart_type").innerHTML=original_html;
  }
}
>>>>>>> seprojectgroup19/master
