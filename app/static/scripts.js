
//MAP CODE
var map;
var geocoder;
var infowindow

function initMap() {

    infowindow = new google.maps.InfoWindow();
    geocoder = new google.maps.Geocoder;
    map = new google.maps.Map(document.getElementById('map'), {
        zoom: 12,
        center: {lat: 53.349, lng: -6.2603},
        mapTypeId: 'terrain'
    });
    var script = document.createElement('script');
    script.src = map.data.loadGeoJson('../static/localjson.json');
    document.getElementsByTagName('head')[0].appendChild(script);

    map.data.addListener('click', function(event) {
        var stationname = event.feature.getProperty("name");
        $("#map").css("width","50%");
        $("#infobox").css("width","49%");
        $("#infobox").css("visibility","visible");
        $("#station").text(stationname);
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