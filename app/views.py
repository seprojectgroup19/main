import os
import sys
sys.path.insert(0, sys.path[0] + '/app/static/DB')

from flask import request, make_response,current_app
from functools import update_wrapper
from flask import render_template
from datetime import timedelta

# python file to execute sql query
import execute_query as eq

import mysql.connector
import requests as r
from app import app
import json

@app.route('/')
def index():
 returnDict = {}
 returnDict['user'] = 'Cormac' # Feel free to put your name here!
 returnDict['title'] = 'Home'
 return render_template("index.html", **returnDict)


@app.route('/lookup', methods=["GET"])
def lookup():
    id = request.args.get('id')
    val_list = []
   
    validator = open("app/static/validation.txt", "r")
    for line in validator:
        val_list.append(line.rstrip())

    mydb = mysql.connector.connect(
      host=val_list[0],
      user=val_list[1],
      passwd=val_list[2],
      database=val_list[3]
    )

    mycursor = mydb.cursor()
    result_list = []

    sql = "SELECT available_bike_stands, available_bikes, last_update FROM DublinBikesDB.dynamic WHERE number = '"+str(id)+"' ORDER BY last_update DESC LIMIT 1"
    mycursor.execute(sql)

    for (available_bike_stands,  available_bikes, last_update) in mycursor:
        result_list.extend( [available_bike_stands,  available_bikes, last_update])
    del sql
    del mycursor
    mycursor = mydb.cursor()
    sql = "SELECT icon FROM DublinBikesDB.weather WHERE number = '"+str(id)+"' ORDER BY time DESC LIMIT 1;"
    mycursor.execute(sql)
    for (icon) in mycursor:
        result_list.extend( [icon])

    final_result = json.dumps(result_list)
    return final_result

@app.route('/testpage')
def testpage():
    
    result = eq.execute_sql("SELECT COUNT(*) FROM DublinBikesDB.dynamic;")
    
    return render_template("testpage.html", **{'result':result[0][0]})

