import sqlalchemy as sqla
import requests as r
import pandas as pd
import numpy as np
import smtplib
import time
#from tabulate import tabulate

URL="dublinbikesdb.ckigaawhnr98.us-east-2.rds.amazonaws.com"
LOG="DBAdmin"
PWD="dublinbikesdatabase"
DB="DublinBikesDB"
PORT='3306'

ENG ="mysql+pymysql://{0}:{1}@{2}:{3}/{4}".format(LOG,PWD,URL,PORT,DB)

engine = sqla.create_engine(ENG,echo=False)

def distance(x1, y1, x2, y2):
    xs = (x1-x2)**2
    ys = (y1-y2)**2
    d = np.sqrt(xs+ys)
    return d

def area_classifier(lat, lng):
    region_A = [53.344743, -6.290209]
    region_B = [53.353709, -6.268752]
    region_C = [53.338747, -6.252959]
    distance_A = distance(lat, lng, *region_A)
    distance_B = distance(lat, lng, *region_B)
    distance_C = distance(lat, lng, *region_C)
    df = pd.DataFrame(data=[distance_A, distance_B, distance_C],
                     index=['region_A', 'region_B', 'region_C'])
    return df.idxmin()

def log_message(message):
    with open('weather_update_log.txt','a') as upf:
        upf.write(message)

def weather_scrape(df, i):
    
    sql = """INSERT INTO DublinBikesDB.weather (number,
        apparentTemperature,
        cloudCover,
        dewPoint,
        humidity,
        icon,
        nearestStormBearing,
        nearestStormDistance,
        ozone,
        precipIntensity,
        precipProbability,
        pressure,
        summary,
        temperature,
        time,
        uvIndex,
        visibility,
        windBearing,
        windGust,
        windSpeed)
        VALUES ({0}, {1}, {2}, {3}, {4}, \"{5}\", {6}, {7}, {8}, {9}, {10}, 
                {11}, \"{12}\", {13}, {14}, {15}, {16}, {17}, {18}, {19})
    """.format(i[0], 
               df['apparentTemperature'].item(), 
               df['cloudCover'].item(), 
               df['dewPoint'].item(), 
               df['humidity'].item(), 
               df['icon'].item(), 
               df['nearestStormBearing'].item(), 
               df['nearestStormDistance'].item(), 
               df['ozone'].item(), 
               df['precipIntensity'].item(), 
               df['precipProbability'].item(), 
               df['pressure'].item(), 
               df['summary'].item(), 
               df['temperature'].item(),
               df['time'].item(), 
               df['uvIndex'].item(), 
               df['visibility'].item(), 
               df['windBearing'].item(), 
               df['windGust'].item(), 
               df['windSpeed'].item())
    
    try:
        engine.execute(sql)
        
    except Exception as e:
        log_message(str(repr(e)))

def scrape_data():
    
    positions = engine.execute("select number, latitude, longitude from static").fetchall()
    
    region_dict = {}
    for n in positions:
        region_dict[n[0]] = area_classifier(n[1], n[2])[0]
    
    darksky_key = "bdad3a845436438e4e6342babd20e131"
    
    while True:
        start = time.time()
    
        response_A = r.get("https://api.darksky.net/forecast/{}/53.344743,-6.290209?units=si".format(darksky_key))
        data_A = response_A.json()
        df_A = pd.DataFrame(data_A['currently'], index=[0])
        
        # shows table view of pandas table in console window.
        # print(tabulate(df_A, headers='keys', tablefmt='psql'))
        
        response_B = r.get("https://api.darksky.net/forecast/{}/53.353709,-6.268752?units=si".format(darksky_key))
        data_B = response_B.json()
        df_B = pd.DataFrame(data_B['currently'], index=[0])
    
        response_C = r.get("https://api.darksky.net/forecast/{}/53.338747,-6.252959?units=si".format(darksky_key))
        data_C = response_C.json()
        df_C = pd.DataFrame(data_C['currently'], index=[0])
        
        for i in positions:

            if region_dict[i[0]] == "region_A":
                weather_scrape(df_A, i)
            elif region_dict[i[0]] == "region_B":
                weather_scrape(df_B, i)
            elif region_dict[i[0]] == "region_C":
                weather_scrape(df_C, i)
        
        # setting up log file to see time write events.
        dtime = dtime=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        log = 'Weather data written to DublinBikesDB.weather at {}.\n'.format(dtime)
    
        log_message(log)
        
        end = time.time()
        time.sleep(300-(end-start))
     
def notify(message):
    
    mail = smtplib.SMTP('smtp.gmail.com',587)
    mail.ehlo()
    
    mail.starttls()
    mail.login('barronciaran@gmail.com', '*************')
    mail.sendmail('barronciaran@gmail.com','ciaran.barron1@ucdconnect.ie',message)
    
    mail.close()
        
try:
    scrape_data()
    
except Exception  as e:
#     
    message = 'EC2 Weather Scraper has stopped running. \n\n Error Message: ' + repr(e)
    notify(message)
#     print(repr(e))
#     print('Scraper stopped. Error message sent')