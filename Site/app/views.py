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
import numpy as np
import threading
import datetime
import calendar
import json
import time


# @app.before_first_request
# def setup():
allmodels = {}
StationNumbers = []

#=================================== find all station numbers ===============================#
with open("./app/static/localjson.json") as f:
    localjson = json.loads(f.read())

data_nums = localjson['features']

for idx in range(len(data_nums)):
    StationNumbers.append(int(data_nums[idx]['properties']['number']))

#=================================== load all models ===============================#
for station_number in StationNumbers:

    model = xgb.Booster()
    model.load_model(f'./app/static/Model/station{station_number}.model')

    allmodels[f"model{station_number}"] = model

#=================================== Auto refresh weather information ===============================#
class WeatherForecast():
    """ Threading example class
    The run() method will be started and it will run in the background
    until the application exits.
    """

    def __init__(self, interval):
        """ Constructor: Make a background job whihch automatically updates the weather infomration.

        (int) Interval: time to sleep after running update function
        """
        self.interval = interval

        thread = threading.Thread(target=self.update_information, args=())
        thread.start()

    def update_information(self):
        """ Method that runs in background updating global variable weatherinformation """
        
        with open("./app/static/DB/authentication.txt") as f:
            auth = f.read().split('\n')
        darksky_key = auth[2]
        
        while True:

            #  hour-by-hour forecast for the next 48 hours, and a day-by-day forecast for the next week.
            wresponse = r.get(f"""
                                https://api.darksky.net/forecast/{darksky_key}/53.34481, -6.266209?
                                units=si&
                                exclude=currently,flags,alerts,minutely
                                """)
            
            weatherforecast = wresponse.json()
            self.update = weatherforecast
            print("UPDATED WEATHER INFORMATION")
            #sleep for set interval (~ 30min/ 1hr)
            time.sleep(self.interval)

# Access forecast information via Weather.update
Weather = WeatherForecast(1800)

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
    
    global allmodels
    global Weather

    # Required forecast day and hour and station to choose model. One for each station.
    D = request.args.get('Day')
    H = request.args.get('Time')
    station_number = request.args.get('Station')

    # generate list of 1s and 0s for building input to model
    dayslist = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun']

    inputs = {
        'weekday':0.0,
        'weekend':0.0,
        'hour_x':0.0,
        'cloudy':0.0,
        'clear':0.0,
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

    icons_cloudy = [
        'partly-cloudy-day',
        'partly-cloudy-night',
        'cloudy',
    ]

    icons_clear =[
        'clear-night',
        'clear-day',
    ]

    icons_rain = [
        'fog',
        'wind',
        'rain'
    ]

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
    if D in ['Mon','Tue','Wed','Thu','Fri']:
        inputs['weekday'] = 1.0
    else:
        inputs['weekend'] = 1.0

    inputs['hour_x'] = float(H)
    

    #=================================== get weather information ===============================#
    weatherforecast = Weather.update

    hourly_data = weatherforecast['hourly']['data']
    daily_data = weatherforecast['daily']['data']

    # store the day "today" and  current hour. 
    now = datetime.datetime.now()
    current_day  = float(now.weekday())
    current_hour = float(now.hour)

    #=================================== find timestamp of prediction ===============================#
    time_diff = 0

    H = float(H)
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

    if time_diff <= 0:
        return json.dumps("Please select a time in the Future for predictions.")

    #=================================== Weekly weather available ===============================#
    if time_diff > 48:        
        # find the time at midnight tonight and add the number of days to it. 
        # Account for time zone difference. 
        mid += 86400*(time_diff//24)
        mid -= 3600 

        data = daily_data

        closest_dayrow = 0
        closest_timestamp = 10000000000000
        smallest_diff = 100000000000

        # select the closes time stamp to use as the weather data
        for dayrow in data:
            diff = abs(dayrow['time'] - mid)
            if diff < smallest_diff:
                smallest_diff =  diff
                closest_timestamp = dayrow['time']
                closest_dayrow = dayrow

        ndata = closest_dayrow

        ################## test
        # return json.dumps(mid)

        # construct input from data (data[2] is the 'icon')
        if ndata['icon'] in icons_cloudy:
            inputs['cloudy'] = 1.0

        if ndata['icon'] in icons_clear:
            inputs['clear'] = 1.0
        
        if ndata['icon'] in icons_rain:
            inputs['rain'] = 1.0

        # input does not match up with daily data.
        for col in wcols:
            if col in ndata:
                inputs[col] = ndata[col]
        
        # dont match on temperature or apparent temperature
        if (H > 8 or H < 20):
            inputs['apparentTemperature'] = ndata['apparentTemperatureHigh']
            inputs['temperature'] = ndata['temperatureHigh']
        else: 
            inputs['apparentTemperature'] = ndata['apparentTemperatureLow']
            inputs['temperature'] = ndata['temperatureLow']        

     #=================================== Daily Weather available ===============================#
    else:
        mid += 86400 * (time_diff//24) 
        mid += 3600 * time_diff%24
        mid -= 3600

        data = hourly_data

        closest_hourrow = 0
        closest_timestamp = 10000000000000
        smallest_diff = 100000000000
        # select the closes time stamp to use as the weather data
        for hourrow in data:
            diff = abs(hourrow['time'] - mid)
            if diff < smallest_diff:
                smallest_diff = diff
                closest_timestamp = hourrow['time']
                closest_hourrow = hourrow

        ndata = closest_hourrow
        
        ############### test
        # return json.dumps(hourrow)

        # construct input from data
        if ndata['icon'] in icons_cloudy:
            inputs['cloudy'] = 1.0

        if ndata['icon'] in icons_clear:
            inputs['clear'] = 1.0
        
        if ndata['icon'] in icons_rain:
            inputs['rain'] = 1.0

        # inputs matches up with the hourly data
        for col in wcols:
            inputs[col] = ndata[col]

    # dataframe of information ready for model application.
    inputs = pd.DataFrame(inputs, index=[0])

    #=================================== Model application ===============================#

    model = allmodels[f"model{station_number}"]

    # What is the format of the inputs ?

    modeldata = xgb.DMatrix(inputs)
    predictions = model.predict(modeldata)
    predicted_available_bikes = predictions.tolist()
     
    #=================================== Model stands ===============================#
    sql = f"""
    SELECT bike_stands
    FROM DublinBikesDB.dynamic
    WHERE number={station_number}
    LIMIT 1;
    """
    stands = int(eq.execute_sql(sql)[0][0])

     #=================================== return data ===============================#
    preds = tuple([predicted_available_bikes, stands])

    return json.dumps(preds)

@app.route('/model_all_stations', methods=["GET"])
def model_all_stations():

    global StationNumbers
    global allmodels
    global Weather

    # Required forecast day and hour and station to choose model. One for each station.
    D = request.args.get('Day')
    H = request.args.get('Time')

    # generate list of 1s and 0s for building input to model
    dayslist = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun']

    inputs = {
        'weekday':0.0,
        'weekend':0.0,
        'hour_x':0.0,
        'cloudy':0.0,
        'clear':0.0,
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

    icons_cloudy = [
        'partly-cloudy-day',
        'partly-cloudy-night',
        'cloudy',
    ]

    icons_clear =[
        'clear-night',
        'clear-day',
    ]

    icons_rain = [
        'fog',
        'wind',
        'rain'
    ]

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
    if D in ['Mon','Tue','Wed','Thu','Fri']:
        inputs['weekday'] = 1.0
    else:
        inputs['weekend'] = 1.0

    inputs['hour_x'] = float(H)
    
    #=================================== Weather information ===============================#
    weatherforecast = Weather.update

    hourly_data = weatherforecast['hourly']['data']
    daily_data = weatherforecast['daily']['data']

    # store the day "today"
    now = datetime.datetime.now()
    current_day  = float(now.weekday())
    current_hour = float(now.hour)

    #=================================== find timestamp of prediction ===============================#
    time_diff = 0

    H = float(H)
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

    if time_diff <= 0:
        return json.dumps("Please select a time in the Future for predictions.")

    #=================================== Weekly weather available ===============================#
    if time_diff > 48:        
        # find the time at midnight tonight and add the number of days to it. 
        # Account for time zone difference. 
        mid += 86400*(time_diff//24)
        mid -= 3600 

        data = daily_data

        closest_dayrow = 0
        closest_timestamp = 10000000000000
        smallest_diff = 100000000000
        # select the closes time stamp to use as the weather data
        for dayrow in data:
            diff = abs(dayrow['time'] - mid)
            if diff < smallest_diff:
                smallest_diff =  diff
                closest_timestamp = dayrow['time']
                closest_dayrow = dayrow

        ndata = closest_dayrow

        ################## test
        # return json.dumps(mid)

        # construct input from data (data[2] is the 'icon')
        if ndata['icon'] in icons_cloudy:
            inputs['cloudy'] = 1.0

        if ndata['icon'] in icons_clear:
            inputs['clear'] = 1.0
        
        if ndata['icon'] in icons_rain:
            inputs['rain'] = 1.0

        # input does not match up with daily data.
        for col in wcols:
            if col in ndata:
                inputs[col] = ndata[col]
        
        # dont match on temperature or apparent temperature
        if (H > 8 or H < 20):
            inputs['apparentTemperature'] = ndata['apparentTemperatureHigh']
            inputs['temperature'] = ndata['temperatureHigh']
        else: 
            inputs['apparentTemperature'] = ndata['apparentTemperatureLow']
            inputs['temperature'] = ndata['temperatureLow']        

     #=================================== Daily Weather available ===============================#
    else:
        mid += 86400 * (time_diff//24) 
        mid += 3600 * time_diff%24
        mid -= 3600

        data = hourly_data

        closest_hourrow = 0
        closest_timestamp = 10000000000000
        smallest_diff = 100000000000
        # select the closes time stamp to use as the weather data
        for hourrow in data:
            diff = abs(hourrow['time'] - mid)
            if diff < smallest_diff:
                smallest_diff = diff
                closest_timestamp = hourrow['time']
                closest_hourrow = hourrow

        ndata = closest_hourrow
        
        ############### test
        # return json.dumps(hourrow)

        # construct input from data
        if ndata['icon'] in icons_cloudy:
            inputs['cloudy'] = 1.0

        if ndata['icon'] in icons_clear:
            inputs['clear'] = 1.0
        
        if ndata['icon'] in icons_rain:
            inputs['rain'] = 1.0

        # inputs matches up with the hourly data
        for col in wcols:
            inputs[col] = ndata[col]

    # dataframe of information ready for model application.
    inputs = pd.DataFrame(inputs, index=[0])

    #=================================== Model application ===============================#
    predicted_available_bikes = {}

    for station_number in StationNumbers:

        model = allmodels[f"model{station_number}"]

        modeldata = xgb.DMatrix(inputs)
        predictions = model.predict(modeldata)
        predicted_bikes = predictions.tolist()

        predicted_available_bikes[station_number] = predicted_bikes

     #=================================== return data ===============================#
    preds = tuple(predicted_available_bikes.items())

    return json.dumps(preds)

@app.route('/make_charts', methods=["GET"])
def make_charts():

    days = float(request.args.get("Days"))
    snum = int(request.args.get("Station"))
    step = request.args.get("TimeStep")
    limit= int(days*288)
    
    sql = f"""
    SELECT *
    FROM DublinBikesDB.dynamic
    WHERE number={snum}
    ORDER BY last_update DESC
    LIMIT {limit};
    """
    stands = eq.execute_sql(sql)

    Ab=[]
    As=[]
    Ts=[]

    for stand in stands:
        Ab.append(stand[4])
        As.append(stand[3])
        Ts.append(stand[5])

    # Allow for adjusted timstep resolution.
    df = pd.DataFrame({
        'Bikes':Ab,
        'Stand':As,
        'Times':Ts
    })

    # convert epoch time to datetime object for use in resampling.
    convertTS = (lambda x : datetime.datetime.utcfromtimestamp((int(x)/1000)).strftime('%Y-%m-%d %H:%M:%S'))

    df.Times = df.Times.apply(convertTS)
    df.Times = pd.to_datetime(df.Times)

    # resample the data to hourly
    df.set_index(['Times'], inplace=True)
    df.index.name='Times'

    if step:
        step = int(step)
        df = df.resample(rule=f'{step}T').mean()

    Ts = list(np.array(pd.DatetimeIndex(df.index).astype(int))/10**6)
    Ab = list(df.Bikes)
    As = list(df.Stand)

    return json.dumps(tuple([As,Ab,Ts]))

@app.route('/fullmodelgraph', methods=["GET"])
def fullmodelgraph():
    
    global StationNumbers
    global allmodels
    global Weather

    # generate predictions for all times up to time frame given station and variables
    variable = request.args.get('variable')
    timeframe = request.args.get('TimeFrame')
    station_number = request.args.get('Station')

    #=================================== Weather Information ===============================#
    weatherforecast = Weather.update

    hourly_data = weatherforecast['hourly']['data']
    daily_data = weatherforecast['daily']['data']

    # store the day "today"
    now = datetime.datetime.now()
    current_day  = float(now.weekday())
    current_hour = float(now.hour)
    
    # generate list of 1s and 0s for building input to model
    dayslist = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun']

    inputdict = {'timestamp':'inputs'}
    resultsdict = {'timestamp':'value'}

    inputs = {
        'weekday':0.0,
        'weekend':0.0,
        'hour_x':0.0,
        'cloudy':0.0,
        'clear':0.0,
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

    icons_cloudy = [
        'partly-cloudy-day',
        'partly-cloudy-night',
        'cloudy',
    ]

    icons_clear =[
        'clear-night',
        'clear-day',
    ]

    icons_rain = [
        'fog',
        'wind',
        'rain'
    ]

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
    if D in ['Mon','Tue','Wed','Thu','Fri']:
        inputs['weekday'] = 1.0
    else:
        inputs['weekend'] = 1.0

    inputs['hour_x'] = float(H)
    

    #=================================== find timestamp of prediction ===============================#
    time_diff = 0

    H = float(H)
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

    if time_diff <= 0:
        return json.dumps("Please select a time in the Future for predictions.")

    #=================================== Weekly weather available ===============================#
    if time_diff > 48:        
        # find the time at midnight tonight and add the number of days to it. 
        # Account for time zone difference. 
        mid += 86400*(time_diff//24)
        mid -= 3600 

        data = daily_data

        closest_dayrow = 0
        closest_timestamp = 10000000000000
        smallest_diff = 100000000000
        # select the closes time stamp to use as the weather data
        for dayrow in data:
            diff = abs(dayrow['time'] - mid)
            if diff < smallest_diff:
                smallest_diff =  diff
                closest_timestamp = dayrow['time']
                closest_dayrow = dayrow

        ndata = closest_dayrow

        ################## test
        # return json.dumps(mid)

        # construct input from data (data[2] is the 'icon')
        if ndata['icon'] in icons_cloudy:
            inputs['cloudy'] = 1.0

        if ndata['icon'] in icons_clear:
            inputs['clear'] = 1.0
        
        if ndata['icon'] in icons_rain:
            inputs['rain'] = 1.0

        # input does not match up with daily data.
        for col in wcols:
            if col in ndata:
                inputs[col] = ndata[col]
        
        # dont match on temperature or apparent temperature
        if (H > 8 or H < 20):
            inputs['apparentTemperature'] = ndata['apparentTemperatureHigh']
            inputs['temperature'] = ndata['temperatureHigh']
        else: 
            inputs['apparentTemperature'] = ndata['apparentTemperatureLow']
            inputs['temperature'] = ndata['temperatureLow']        

     #=================================== Daily Weather available ===============================#
    else:
        mid += 86400 * (time_diff//24) 
        mid += 3600 * time_diff%24
        mid -= 3600

        data = hourly_data

        closest_hourrow = 0
        closest_timestamp = 10000000000000
        smallest_diff = 100000000000
        # select the closes time stamp to use as the weather data
        for hourrow in data:
            diff = abs(hourrow['time'] - mid)
            if diff < smallest_diff:
                smallest_diff = diff
                closest_timestamp = hourrow['time']
                closest_hourrow = hourrow

        ndata = closest_hourrow
        
        ############### test
        # return json.dumps(hourrow)

        # construct input from data
        if ndata['icon'] in icons_cloudy:
            inputs['cloudy'] = 1.0

        if ndata['icon'] in icons_clear:
            inputs['clear'] = 1.0
        
        if ndata['icon'] in icons_rain:
            inputs['rain'] = 1.0

        # inputs matches up with the hourly data
        for col in wcols:
            inputs[col] = ndata[col]

    # dataframe of information ready for model application.
    inputs = pd.DataFrame(inputs, index=[0])

    #=================================== Model application ===============================#

    model = xgb.Booster()
    model.load_model(f'./app/static/Model/station{station_number}.model')

    # What is the format of the inputs ?

    modeldata = xgb.DMatrix(inputs)
    predictions = model.predict(modeldata)
    predicted_available_bikes = predictions.tolist()
     
    #=================================== Model stands ===============================#
    sql = f"""
    SELECT bike_stands
    FROM DublinBikesDB.dynamic
    WHERE number={station_number}
    LIMIT 1;
    """
    stands = int(eq.execute_sql(sql)[0][0])

     #=================================== return data ===============================#
    preds = tuple([predicted_available_bikes, stands])

    return json.dumps(preds)


@app.route('/testpage')
def testpage():

    days = 7
    station = 5
    limit = 288*days

    sql = f"""
    SELECT *
    FROM DublinBikesDB.dynamic
    WHERE number={station}
    LIMIT {limit};
    """
    stands = eq.execute_sql(sql)

    Ab=[]
    As=[]
    Ts=[]

    for stand in stands:
        Ab.append(stand[4])
        As.append(stand[3])
        Ts.append(stand[5])

    returndict={'abikes':As,'astands':Ab,'times':Ts}

    return render_template("testpage.html", **returndict)


