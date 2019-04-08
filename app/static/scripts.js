//MAP CODE
var map;
var geocoder;
var infowindow

function initMap() {

  infowindow = new google.maps.InfoWindow();
  geocoder = new google.maps.Geocoder;
  map = new google.maps.Map(document.getElementById('map'), {
    zoom: 13.5,
    center: {
      lat: 53.34481,
      lng: -6.266209
    },
    mapTypeId: 'terrain'
  });

  // loading map data from local json
  var data = map.data.loadGeoJson('../static/localjson.json');
  map.data.addGeoJson(data);


  map.data.setStyle(
    function (feature) {
      if (parseInt(feature.getProperty("number")) > 50) {
        console.log(feature.getProperty("number"));
        var color = feature.getProperty("color");
        console.log(color);
      }
      return {
        fillColor: 'green'
      };
    }
  );

  map.data.addListener('click', function (event) {
    var stationname = event.feature.getProperty("name");
    var stationnumber = event.feature.getProperty("number");
    $("#map").css("width", "50%");
    $("#infobox").css("width", "49.5%");
    $("#infobox").css("visibility", "visible");
    $("#station").text(stationname);
    $("#avbikes").text("Loading...")
    $("#avstands").text("Loading...")
    standinfo(stationnumber);
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
      console.log(this.responseText);
      document.getElementById("avstands").innerHTML = JSON.parse(this.responseText)[0]
      document.getElementById("avbikes").innerHTML = JSON.parse(this.responseText)[1];
      $("#weathericon").attr("class", JSON.parse(this.responseText)[3]);
      SkyCon()
    }
  };
  xmlhttp.open("GET", "/lookup?id=" + stand, true);
  xmlhttp.send();
}

function SkyCon() {
  var icons = new Skycons({
      "color": "#ffffff"
    }),
    list = [
      "clear-day", "clear-night", "partly-cloudy-day",
      "partly-cloudy-night", "cloudy", "rain", "sleet", "snow", "wind",
      "fog"
    ],
    i;

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
        data: new google.maps.LatLng(53.34481,-6.266209),//get_points(),
        map : map
      });

      heatmap.setMap(map);

  } else {
    // redraw original map
    initMap();
  }

}

function get_points(){

  var map_data = [];
  var file="../static/localjson.json";
  
  $.getJSON(file, 
    function(data){

      for (var i=0; i<data.features.length; i++){

        var lat = data.features[i].geometry.coordinates[0];
        var lng = data.features[i].geometry.coordinates[1];
        var station_number = data.features[i].properties.number;

        // add data to array for sending to heatmap. replace station number with n_bikes.
        // var str_ = new google.maps.LatLng(lat, lng);
        map_data.push(new google.maps.LatLng(parseFloat(lat), parseFloat(lng)));
      }

    console.log(map_data);
    
    return map_data[0];
  });
};

// function current_bikes(station_number) {
//   xmlhttp = new XMLHttpRequest();
//   xmlhttp.onreadystatechange = function () {
//     if (this.readyState == 4 && this.status == 200) {
//       return nbikes;
//     }
//   };
//   xmlhttp.open("GET", "/lookup?id=" + stand, true);
//   xmlhttp.send();
// }