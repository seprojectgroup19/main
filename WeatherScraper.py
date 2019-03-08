import requests as r
import json
import numpy as np
import pandas as pd
import mysql.connector
import time

mydb = mysql.connector.connect(
  host="dublinbikesdb.ckigaawhnr98.us-east-2.rds.amazonaws.com",
  user="DBAdmin",
  passwd="dublinbikesdatabase",
  database="DublinBikesDB"
)
mycursor = mydb.cursor()

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

def weather_scrape(df, i):
    current_conditions = df['currently']
    for_sql = current_conditions.drop(['data', 'meteoalarm-license', 'nearest-station', 'sources', 'units'])
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
    """.format(i[0], for_sql[0], for_sql[1], for_sql[2], for_sql[3], 
               for_sql[4], for_sql[5], for_sql[6], for_sql[7], 
               for_sql[8], for_sql[9], for_sql[10], for_sql[11], 
               for_sql[12], for_sql[13], for_sql[14], for_sql[15], 
               for_sql[16], for_sql[17], for_sql[18])
    mycursor.execute(sql)

mycursor.execute("select number, latitude, longitude from static")
positions = mycursor.fetchall()
region_dict = {}
for n in (positions):
    region_dict[n[0]] = area_classifier(n[1], n[2])[0]
	
darksky_key = "bdad3a845436438e4e6342babd20e131"

while True:
	start = time.time()
    response_A = r.get("https://api.darksky.net/forecast/{}/53.344743,-6.290209?units=si".format(darksky_key))
    response_B = r.get("https://api.darksky.net/forecast/{}/53.353709,-6.268752?units=si".format(darksky_key))
    response_C = r.get("https://api.darksky.net/forecast/{}/53.338747,-6.252959?units=si".format(darksky_key))
    data_A = response_A.json()
    data_B = response_B.json()
    data_C = response_C.json()
    df_A = pd.DataFrame(data_A)
    df_B = pd.DataFrame(data_B)
    df_C = pd.DataFrame(data_C)
	
	for i in positions:
		if region_dict[i[0]] == "region_A":
			weather_scrape(df_A, i)
		elif region_dict[i[0]] == "region_B":
			weather_scrape(df_B, i)
		elif region_dict[i[0]] == "region_C":
			weather_scrape(df_C, i)
		mydb.commit()
		
	end = time.time()
	time.sleep(300-(end-start))