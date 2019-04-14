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
    dayslist = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun']

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
    with open("./app/static/DB/authentication.txt") as f:
        auth = f.read().split('\n')
    darksky_key = auth[2]
    
    #  hour-by-hour forecast for the next 48 hours, and a day-by-day forecast for the next week.
    wresponse = r.get(f"""
                        https://api.darksky.net/forecast/{darksky_key}/53.34481, -6.266209?
                        units=si&
                        exclude=currently,flags,alerts,minutely
                        """)
    
    weatherforecast = wresponse.json()

    hourly_data = weatherforecast['hourly']['data']
    daily_data = weatherforecast['hourly']['data']

    # store the day "today"
    now = datetime.datetime.now()
    current_day  = int(now.weekday())
    current_hour = int(now.hour)

    # determine the gap in hours between now and the prediction time. (weather forecast data bedomes daily after 48.)
    time_diff = 0

    H = int(H)
    if H >= current_hour:
        time_diff += H - current_hour 
    else:
        time_diff -= current_hour - H # minus as add to the day later.

    dayslist_index_predict_day = dayslist.index(D)
    
    if ((current_day != dayslist_index_predict_day) or (H < current_hour)):
        if current_day < dayslist_index_predict_day: 
            time_diff += (dayslist_index_predict_day - current_day)*24
        else:
            time_diff += (7*24) + (dayslist_index_predict_day - current_day)*24

    mid = calendar.timegm(datetime.date.today().timetuple())

    
    return json.dumps(tuple([mid, time_diff, current_day]))

    if time_diff > 48:        
        # find the time at midnight tonight and add the number of days to it. 
        # Account for time zone difference. 
        mid += 86400*(time_diff//24)
        mid -= 3600 

        data = daily_data

        for dayrow in data:
            if dayrow['time']==mid:
                ndata = dayrow

        ################## test
        return json.dumps(mid)

        # construct input from data (data[2] is the 'icon')
        if ndata['icon'] in icons:
            inputs[ndata['icon']] = 1.0

        # input does not match up with daily data.
        for col in wcols:
            if col in ndata:
                inputs[col] = ndata[col]
        
        # dont match on temperature or apparent temperature
        inputs['apparentTemperature'] = ndata['apparentTemperatureHigh']
        inputs['temperature'] = ndata['temperatureHigh']

    else:
        mid += 86400 * (time_diff//24) 
        mid += 3600 * time_diff%24
        mid -= 3600

        data = hourly_data

        for hourrow in data:
            if hourrow['time']==mid:
                ndata = hourrow
        
        ############### test
        # return json.dumps(hourrow)

        # construct input from data
        if ndata['icon'] in icons:
            inputs[ndata['icon']] = 1.0

        # inputs matches up with the hourly data
        for col in wcols:
            inputs[col] = ndata[col]

    # dataframe of information ready for model application.
    inputs = pd.DataFrame(inputs, index=[0])

    #=================================== Model application ===============================#

    model = xgb.Booster()
    model.load_model(f'./app/static/Model/station_{station_number}.model')

    # What is the format of the inputs ?

    data = xgb.DMatrix(inputs)
    predictions = model.predict(data)

    return json.dumps(predictions)

@app.route('/testpage')
def testpage():

    # get authentication information (api-key)
    with open("./app/static/DB/authentication.txt") as f:
        auth = f.read().split('\n')
    darksky_key = auth[2]
    
    #  hour-by-hour forecast for the next 48 hours, and a day-by-day forecast for the next week.
    wresponse = r.get(f"""
                        https://api.darksky.net/forecast/{darksky_key}/53.34481, -6.266209?
                        units=si&
                        exclude=currently,flags,alerts,minutely
                        """)
    
    weatherforecast = wresponse.json()

    hourly_data = weatherforecast['hourly']['data']
    daily_data = weatherforecast['hourly']['data']

    returndict = {
        'test': daily_data[0]
    }
    	
    return render_template("testpage.html", **returndict)


