import os
import sys
sys.path.insert(0, sys.path[0] + '/app/static/DB')

from flask import request, make_response,current_app
from functools import update_wrapper
from flask import render_template
from datetime import timedelta
import execute_query as eq
import xgboost as xgb
import requests as r
from app import app
import datetime
import json

@app.route('/')
def index():
 return render_template("index.html")

@app.route("/get_weather_update", methods=["GET"])
def get_weather_update():

    # Using the O'Connell street stations latest weather report as city wide weather
    weather = """
        SELECT *
        FROM DublinBikesDB.weather 
        WHERE number = 33
        ORDER BY time DESC LIMIT 1;
    """
    results = [tuple(eq.execute_sql(weather)[0])]
    
    return json.dumps(results)

@app.route('/lookup', methods=["GET"])
def lookup():

    id = request.args.get('id')
    
    bikes = f"""
        SELECT available_bike_stands, available_bikes, last_update 
        FROM DublinBikesDB.dynamic 
        WHERE number = {str(id)} 
        ORDER BY last_update DESC LIMIT 1;
    """
    
    result = list(eq.execute_sql(bikes)[0])

    return json.dumps(result)

@app.route('/fulllookup', methods=["GET"])
def fulllookup():

    fulldata = f"""
        SELECT first.number, first.status, first.available_bike_stands, first.available_bikes, second.icon
        FROM
        (SELECT bikes.number, bikes.status, bikes.available_bike_stands, bikes.available_bikes
        FROM DublinBikesDB.dynamic  bikes
        INNER JOIN
            (SELECT number, MAX(last_update) AS MaxDateTime
            FROM DublinBikesDB.dynamic
            GROUP BY number) groupedbikes
        ON bikes.number = groupedbikes.number
        AND bikes.last_update = groupedbikes.MaxDateTime) first
        INNER JOIN
        (SELECT weather.number, weather.icon
        FROM DublinBikesDB.weather  weather
        INNER JOIN
            (SELECT number, icon, MAX(time) AS MaxDateTime
            FROM DublinBikesDB.weather
            GROUP BY number) groupedweather
        ON weather.number = groupedweather.number
        AND weather.time = groupedweather.MaxDateTime) second
        ON first.number = second.number
    """

    result = list(eq.execute_sql(fulldata))
    resultdictionary = {}
    for i in result:
        resultdictionary[str(i[0])] = {}
        resultdictionary[str(i[0])]["status"] = i[1]
        resultdictionary[str(i[0])]["stands"] = i[2]
        resultdictionary[str(i[0])]["bikes"] = i[3]
        resultdictionary[str(i[0])]["weather_icon"] = i[4]

    return json.dumps(resultdictionary)

@app.route('/model', methods=["GET"])
def model():

    D = request.args.get('Day')
    H = request.args.get('Time')

    # store the day "today"
    current_day  = datetime.datetime.today().weekday()
    current_hour = datetime.datetime.today().hour()

    # determine the gap in hours between now and the prediction time. (weather forecast data bedomes daily after 48.)
    time_diff = 0

    if H > current_hour:
        time_diff += H - current_hour
    else:
        time_diff += 24 - H - current_hour

    # generate list of 1s and 0s for building input to model
    dayslist = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun']
    
    for index, day in enumerate(dayslist):
        
        if day == D:
            dayslist[index] = 1

            # hours between now and the prediction (havent accounted for time yet)
            if (current_day - (index+1) < 0):
                time_diff += (7*24) - 24*(current_day-index+1)
            else:
                time_diff += 24*(current_day-(index+1))

        else:
            dayslist[index] = 0



    with open("./static/DB/authentication.txt") as f:
        auth = f.read().split('\n')
    darksky_key = auth[2]

    # Query the darksy api here. for the relevant information
    # A Forecast Request returns the current weather conditions, 
    # a minute-by-minute forecast for the next hour (where available), 
    # an hour-by-hour forecast for the next 48 hours, 
    # and a day-by-day forecast for the next week.

    wresponse = r.get(f"https://api.darksky.net/forecast/{darksky_key}/53.344743,-6.290209?units=si")
    weatherforecast = wresponse.json()


    model = xgb.Booster()

    station_number = request.args.get('station_number')
    model.load_model(f'station_{station_number}.model')

    # What is the format of the inputs ?


    data = xgb.DMatrix(inputs)
    predictions = model.predict(data)

    return predictions

@app.route('/testpage')
def testpage():
    
    with open("./app/static/DB/authentication.txt") as f:
        auth = f.read().split('\n')
    
    darksky_key = auth[2]

    # Query the darksy api here. for the relevant information
    # A Forecast Request returns the current weather conditions, 
    # a minute-by-minute forecast for the next hour (where available), 
    # an hour-by-hour forecast for the next 48 hours, 
    # and a day-by-day forecast for the next week.

    # using the coordinates for the centre of the city.
    weatherforecast = r.get(f"https://api.darksky.net/forecast/{darksky_key}/53.34481, -6.266209?units=si")

    t = weatherforecast.json()
    data = []
    for i in list(t.keys()):
        data.append(t[i])

    return render_template("testpage.html", **{'WeatherForecast': t, 'res':data})


