#!/bin/bash

############### read the last update log information.

#log of bikes data
log="$( tail -n2 SEProject/update_log.txt )";

# log of weather data
weatherlog="$(tail -n2 SEProject/weather_update_log.txt )";

############### Determine if the scraper processes are running.

# Grep python is to filter out the grep process from the result of grep api
var="$( ps -aux | grep APIScraper | grep python )";

if [[ -z "$var" ]]; then
	status="Offline";
else
	status="Running";
fi

# check if the weather scraper is running
weathervar="$(ps -aux | grep WeatherScraper2.py | grep python )";

if [[ -z "$weathervar" ]]; then
	weatherstatus="Offline";
else
	weatherstatus="Running";
fi

################ find the number of rows in each table.

response=$(./rds_connect.sh "SELECT COUNT(*) FROM DublinBikesDB.dynamic;" 2>/dev/null);
count=$( echo $response | cut -d" " -f2- );

wresponse=$(./rds_connect.sh "SELECT COUNT(*) FROM DublinBikesDB.weather;" 2>/dev/null);
wcount=$( echo $wresponse | cut -d" " -f2- );

#printing out information messages

echo " ";
echo "--------------------------";
echo "    Scraper information";
echo "--------------------------";

printf "\n Bike information scraper ";
printf "\n==========================\n";
printf "\nStatus:\t$status";
printf "\nCount:\t$count\n";
printf "\nRecent updates: \n$log\n\n";

printf "\n Weather information scraper ";
printf "\n=============================\n";
printf "\nStatus:\t$weatherstatus";
printf "\nCount:\t$wcount\n";
printf "\nRecent updates: \n$weatherlog\n\n";

