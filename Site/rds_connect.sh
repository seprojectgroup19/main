#!/bin/bash

HOST='dublinbikesdb.ckigaawhnr98.us-east-2.rds.amazonaws.com';
PWD="dublinbikesdatabase";
QUERY="SELECT COUNT(*) FROM DublinBikesDB.dynamic;";

if [ $# -gt 0 ]; then
	mysql -h $HOST -P 3306 -u DBAdmin --password=$PWD <<< "$1;";
else
	mysql -h $HOST -P 3306 -u DBAdmin --password=$PWD;
fi
