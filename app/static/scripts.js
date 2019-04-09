
//MAP CODE
var map;
var geocoder;
var infowindow

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
                for (x in data){
                    console.log(data[x].properties.number);
                    var y = data[x].properties.number
                    allMarkers[y] = new google.maps.Marker({
                    position : {lat : data[x]["geometry"]["coordinates"]["1"],
                    lng : data[x]["geometry"]["coordinates"]["0"]},
                    map : map,
                    name : data[x]["properties"]["name"],
                    number : data[x]["properties"]["number"],
                    icon: {url: "http://maps.google.com/mapfiles/ms/icons/green-dot.png"}
                                           });
                    allMarkers[y].addListener("click", function() {
                            var stationname = allMarkers[y]["name"];
                            var stationnumber = allMarkers[y]["number"];
                            $("#map").css("width","50%");
                            $("#infobox").css("width","49%");
                            $("#infobox").css("visibility","visible");
                            $("#station").text(stationname);
                            $("#avbikes").text("Loading...");
                            $("#avstands").text("Loading...");
                            map.panBy(0, 0);
                            standinfo(stationnumber);
                            var person = prompt("Please enter your name", "Harry Potter");
                            allMarkers[person].icon.url ="http://maps.google.com/mapfiles/ms/icons/blue-dot.png";
                        });
                }
                console.log(allMarkers)
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
