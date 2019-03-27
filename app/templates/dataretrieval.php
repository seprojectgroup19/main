<?php
include "connecinfo.php";

//Error handling imported with server connection data

//Adapted from W3 schools - https://www.w3schools.com/xml/ajax_php.asp
$id = intval($_GET['id']);

//Queries server - formats response as html
$sql="SELECT available_bike_stands, available_bikes, last_update FROM DublinBikesDB.dynamic WHERE number = '".$id."' ORDER BY last_update DESC LIMIT 1";
$result = mysqli_query($conn,$sql);

//Alternative formatting adapted from https://stackoverflow.com/questions/14456529/mysqli-fetch-array-while-loop-columns
while($row = mysqli_fetch_array($result)) {
    $typeArray[0] = $row['available_bike_stands'];
    $typeArray[1] = $row['available_bikes'];
}
$json = json_encode($typeArray);
echo $json;
mysqli_close($conn);
?>
