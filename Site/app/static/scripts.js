//MAP CODE
var map;
var geocoder;
var infowindow
var map_center = {
  lat: 53.34481,
  lng: -6.266209
};
var zoom_level = 13.5;


function initMap() {

    infowindow = new google.maps.InfoWindow();
    geocoder = new google.maps.Geocoder;
    var latlng = new google.maps.LatLng(53.34481, -6.266209);
    map = new google.maps.Map(document.getElementById('map'), {
        zoom: 13.5,
        center: latlng,
        mapTypeId: 'terrain'
    });

    showStationMarkers();

}

//Write in pins - source: Slides "WebDev"
 function showStationMarkers(data) {
            var iconBase = 'https://maps.google.com/mapfiles/kml/shapes/';
            $.getJSON('../static/localjson.json', null, function(data) {
                data = data["features"]
                var allMarkers = [];
                rackdata = fulllookup();
                for (x in data){
                    var y = data[x].properties.number
                    allMarkers[y] = new google.maps.Marker({
                    position : {lat : data[x]["geometry"]["coordinates"]["1"],
                    lng : data[x]["geometry"]["coordinates"]["0"]},
                    map : map,
                    name : data[x]["properties"]["name"],
                    number : data[x]["properties"]["number"],

                    icon: {url: "http://maps.google.com/mapfiles/ms/icons/green-dot.png"}
                                           });


                    for (p in allMarkers){
                        if (rackdata[p].bikes < 5){
                            allMarkers[p].icon.url = "http://maps.google.com/mapfiles/ms/icons/red-dot.png"
                        }
                        else if (rackdata[p].bikes < 10){
                            allMarkers[p].icon.url = "http://maps.google.com/mapfiles/ms/icons/blue-dot.png"
                        }
                        else{
                            allMarkers[p].icon.url = "http://maps.google.com/mapfiles/ms/icons/green-dot.png"
                        }

                    }


                    allMarkers[y].addListener("click", function() {
                            var stationname = this["name"];
                            var stationnumber = this["number"];
                            $("#map").css("width","65%");
                            $("#infobox").css("width","35%");
                            $("#infobox").css("visibility","visible");
                            $("#station").text(stationname);
                            $("#avbikes").text("Loading...");
                            $("#avstands").text("Loading...");
                            map.panBy(0, 0);
                            standinfo(stationnumber);
                        });
                }
            });
}

// handles dropdown menu
function clickHandler(val) {
  if (val == 1) {
    $("#map").css("width", "100%");
    $("#infobox").css("width", "0%");
    $("#infobox").css("visibility", "hidden");
    document.documentElement.scrollTop = 0;
  } else if (val == 2) {
    $("#station").text("UNDER CONSTRUCTION");

  } else if (val == 3) {
    $("#station").text("UNDER CONSTRUCTION");
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

function split_window_info(stationname, stationnumber) {

  $("#map").css("width","60%");
  $("#infobox").css("width","40%");
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

  sn = document.getElementById("station_number_find").value;

  // bring up information on the stations. (activate click event)
  standinfo(sn);

  if (sn=='default'){
    initMap();
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

            split_window_info(stationname, station_number);

          }
        }
      }
    );
  }
}
