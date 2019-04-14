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
import pandas as pd
import datetime
import calendar
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
    
    # Required forecast day and hour and station to choose model. One for each station.
    D = request.args.get('Day')
    H = request.args.get('Time')
    station_number = request.args.get('Station')

    # generate list of 1s and 0s for building input to model
    dayslist = ['Sun','Mon','Tue','Wed','Thu','Fri','Sat']

    inputs = {
        'Mon':0.0,
        'Tue':0.0,
        'Wed':0.0,
        'Thu':0.0,
        'Fri':0.0,
        'Sat':0.0,
        'Sun':0.0,
        'hour_x':0.0,
        'partly-cloudy-day':0.0,
        'partly-cloudy-night':0.0,
        'clear-night':0.0,
        'clear-day':0.0,
        'fog':0.0,
        'wind':0.0,
        'cloudy':0.0,
        'rain':0.0,
        'apparentTemperature':0.0,
        'cloudCover':0.0,
        'dewPoint':0.0,
        'humidity':0.0,
        'precipIntensity':0.0,
        'precipProbability':0.0,
        'pressure':0.0,
        'temperature':0.0,
        'windBearing':0.0,
        'windGust':0.0,
        'windSpeed':0.0,
        'uvIndex':0.0,
        'visibility':0.0
    }

    icons = [
        'partly-cloudy-day',
        'partly-cloudy-night',
        'clear-night',
        'clear-day',
        'fog',
        'wind',
        'cloudy',
        'rain']

    wcols = [
        'apparentTemperature',
        'cloudCover',
        'dewPoint',
        'humidity',
        'precipIntensity',
        'precipProbability',
        'pressure',
        'temperature',
        'windBearing',
        'windGust',
        'windSpeed',
        'uvIndex',
        'visibility']

    # set day and hour.
    inputs[D] = 1.0
    inputs['hour_x'] = H

    # get authentication information (api-key)
    with open("./static/DB/authentication.txt") as f:
        auth = f.read().split('\n')
    darksky_key = auth[2]

    # Query the darksy api here. for the relevant information. A Forecast Request returns the current weather conditions, 
    # a minute-by-minute forecast for the next hour (where available), an hour-by-hour forecast for the next 48 hours, 
    # and a day-by-day forecast for the next week.

    wresponse = r.get(f"""
                        https://api.darksky.net/forecast/{darksky_key}/53.34481, -6.266209?
                        units=si&
                        exclude=currently,flags,alerts,minutely
                        """)
    
    weatherforecast = wresponse.json()

    hourly_data = weatherforecast['hourly']['data']
    daily_data = weatherforecast['hourly']['data']

    # store the day "today"
    current_day  = datetime.datetime.today().weekday()
    current_hour = datetime.datetime.today().hour()

    # determine the gap in hours between now and the prediction time. (weather forecast data bedomes daily after 48.)
    time_diff = 0

    if H > current_hour:
        time_diff += H - current_hour
    else:
        time_diff += 24 - H - current_hour

    for index, day in enumerate(dayslist):
        if day == D:
            dayslist[index] = 1

            # hours between now and the prediction (havent accounted for time yet)
            if (current_day - index < 0):
                time_diff += (7*24) - 24*(current_day-index)
            else:
                time_diff += 24*(current_day-index)
        else:
            dayslist[index] = 0

    mid = calendar.timegm(datetime.date.today().timetuple())
    
    if time_diff > 48:        
        # find the time at midnight tonight and add the number of days to it. 
        # Account for time zone difference. 
        mid += 86400*(time_diff//24)
        mid -= 3600 

        data = daily_data

        for dayrow in data:
            if dayrow['time']==mid:
                data = dayrow

        # construct input from data
        if data['icon'] in icons:
            inputs[data['icon']] = 1.0

        # input does not match up with daily data.
        for col in wcols:
            if col in data:
                inputs[col] = data[col]
        
        # dont match on temperature or apparent temperature
        inputs['apparentTemperature'] = data['apparentTemperatureHigh']
        inputs['temperature'] = data['temperatureHigh']

    else:
        mid += 86400 * (time_diff//24) 
        mid += 3600 * time_diff%24
        mid -= 3600

        data = hourly_data

        for hourrow in data:
            if hourrow['time']==mid:
                data = hourrow
        
        # construct input from data
        if data['icon'] in icons:
            inputs[data['icon']] = 1.0

        # inputs matches up with the hourly data
        for col in wcols:
            inputs[col] = data[col]


    #=================================== Model application ===============================#


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
    weatherforecast = r.get(f"""https://api.darksky.net/forecast/{darksky_key}/53.34481, -6.266209?
                            units=si&
                            exclude=currently,flags,alerts,minutely""")

    t = weatherforecast.json()
    
    test = list(t['daily']['data'][0].keys())
    
    test2 = {
        'Mon':0.0,
        'Tue':0.0,
        'Wed':0.0,
        'Thu':0.0,
        'Fri':0.0,
        'Sat':0.0,
        'Sun':0.0,
        'hour_x':0.0,
        'partly-cloudy-day':0.0,
        'partly-cloudy-night':0.0,
        'clear-night':0.0,
        'clear-day':0.0,
        'fog':0.0,
        'wind':0.0,
        'cloudy':0.0,
        'rain':0.0,
        'apparentTemperature':0.0,
        'cloudCover':0.0,
        'dewPoint':0.0,
        'humidity':0.0,
        'precipIntensity':0.0,
        'precipProbability':0.0,
        'pressure':0.0,
        'temperature':0.0,
        'windBearing':0.0,
        'windGust':0.0,
        'windSpeed':0.0,
        'uvIndex':0.0,
        'visibility':0.0
    }

    return render_template("testpage.html", **{'WeatherForecast': test, 'res':test2})


