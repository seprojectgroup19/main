from flask import render_template
from flask import request, make_response,current_app
from app import app
from functools import update_wrapper
from datetime import timedelta
import mysql.connector
import os
import requests as r
import json



#CORS HEADER
def crossdomain(origin=None, methods=None, headers=None, max_age=21600,
                attach_to_all=True, automatic_options=True):
    """Decorator function that allows crossdomain requests.
      Courtesy of
      https://blog.skyred.fi/articles/better-crossdomain-snippet-for-flask.html
    """
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    # use str instead of list if using Python 3.x
    if headers is not None and not isinstance(headers, list):
        headers = ', '.join(x.upper() for x in headers)
    # use str instead of list if using Python 3.x
    if not isinstance(origin, list):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        """ Determines which methods are allowed
        """
        if methods is not None:
            return methods

        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        """The decorator function
        """
        def wrapped_function(*args, **kwargs):
            """Caries out the actual cross domain code
            """
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers
            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            h['Access-Control-Allow-Credentials'] = 'true'
            h['Access-Control-Allow-Headers'] = \
                "Origin, X-Requested-With, Content-Type, Accept, Authorization"
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)
    return decorator



@app.route('/')
def index():
 returnDict = {}
 returnDict['user'] = 'Cormac' # Feel free to put your name here!
 returnDict['title'] = 'Home'
 return render_template("index.html", **returnDict)


@app.route('/lookup', methods=["GET"])
@crossdomain(origin='*')
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



