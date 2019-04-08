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
    
    bikes = f"""
        SELECT available_bike_stands, available_bikes, last_update 
        FROM DublinBikesDB.dynamic 
        WHERE number = {str(id)} 
        ORDER BY last_update DESC LIMIT 1;
    """
    weather = f"""
        SELECT icon 
        FROM DublinBikesDB.weather 
        WHERE number = {str(id)}
        ORDER BY time DESC LIMIT 1;
    """
    result = list(eq.execute_sql(bikes)[0])
    result += [tuple(eq.execute_sql(weather)[0])]

    return json.dumps(result)

@app.route('/testpage')
def testpage():
    
    return render_template("testpage.html", **{'result': 5})

