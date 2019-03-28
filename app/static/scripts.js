
//MAP CODE
var map;
var geocoder;
var infowindow

function initMap() {

    infowindow = new google.maps.InfoWindow();
    geocoder = new google.maps.Geocoder;
    map = new google.maps.Map(document.getElementById('map'), {
        zoom: 13.5,
        center: {lat: 53.34481, lng:-6.266209},
        mapTypeId: 'terrain'
    });

    // loading map data from local json
    var data = map.data.loadGeoJson('../static/localjson.json');
    map.data.addGeoJson(data);


    map.data.setStyle(function(feature){
        if (parseInt(feature.getProperty("number")) > 50){
            console.log(feature.getProperty("number"));
        feature.setProperty("icon","/static/images/sunnyicon.jpg");
        }
    });







    map.data.addListener('click', function(event) {
        var stationname = event.feature.getProperty("name");
        var stationnumber = event.feature.getProperty("number");
        $("#map").css("width","50%");
        $("#infobox").css("width","49%");
        $("#infobox").css("visibility","visible");
        $("#station").text(stationname);
        $("#avbikes").text("Loading...")
        $("#avstands").text("Loading...")
        standinfo(stationnumber);
    });

}

// handles dropdown menu
function clickHandler(val){
    if (val == 1 ) {
        $("#map").css("width","100%");
        $("#infobox").css("width","0%");
        $("#infobox").css("visibility","hidden");
        document.documentElement.scrollTop = 0;
    }
    else if (val == 2){
        $("#station").text("UNDER CONSTRUCTION");

    }
    else if (val == 3) {
        $("#station").text("UNDER CONSTRUCTION");
    }
}

function standinfo(stand){
    xmlhttp = new XMLHttpRequest();
    xmlhttp.onreadystatechange = function() {
          if (this.readyState == 4 && this.status == 200) {
              //Writes query to HTML - allows for interactivity on page
            console.log(this.responseText);
            document.getElementById("avstands").innerHTML = JSON.parse(this.responseText)[0]
            document.getElementById("avbikes").innerHTML = JSON.parse(this.responseText)[1];
            $("#weathericon").attr("class",JSON.parse(this.responseText)[3]);
            SkyCon()
       }
        };
    xmlhttp.open("GET","/lookup?id="+ stand ,true);
    xmlhttp.send();
}
function SkyCon(){
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
