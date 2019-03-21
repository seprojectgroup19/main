import time
import numpy as np
import pandas as pd
import sqlalchemy as sqla
import requests as r

with open("C:/Users/Daniel/Documents/MSc/Semester 2/Software Engineering Project/authentication.txt") as f:
    auth = f.read().split("\n")

bikes_key = auth[0]
contract = auth[1]
darksky_key = auth[2]
URL = auth[3]
LOG = auth[4]
PWD = auth[5]
PORT = auth[6]
DB = auth[7]
TAB = auth[8]

ENG = "mysql+mysqldb://{0}:{1}@{2}:{3}/{4}".format(LOG, PWD, URL, PORT, DB)
engine = sqla.create_engine(ENG, echo=False)


def distance(x1, y1, x2, y2):
    """
    Returns distance between two points
    Assumes that locally (over <10 km) earth is flat,
    otherwise would use haversine formula to calculate great-circle distance
    :param x1: latitude of position 1
    :param y1: longitude of position 1
    :param x2: latitude of position 2
    :param y2: longitude of position 2
    :return: distance between position 1 and 2
    """
    xs = (x1 - x2) ** 2
    ys = (y1 - y2) ** 2
    d = np.sqrt(xs + ys)
    return d


def area_classifier(lat, lng):
    """
    Returns which region a latitude / longitude pair is closest to
    :param lat: latitude of position
    :param lng: longitude of position
    :return: region
    """
    region_a = [53.344743, -6.290209]
    region_b = [53.353709, -6.268752]
    region_c = [53.338747, -6.252959]
    distance_a = distance(lat, lng, *region_a)
    distance_b = distance(lat, lng, *region_b)
    distance_c = distance(lat, lng, *region_c)
    df = pd.DataFrame(data=[distance_a, distance_b, distance_c],
                      index=['region_a', 'region_b', 'region_c'])
    return df.idxmin()


def weather_scrape(df, i):
    current_conditions = df['currently']
    current_conditions.drop(['data', 'meteoalarm-license', 'nearest-station', 'sources', 'units'], inplace=True)
    sql = """INSERT INTO {0}.{1} (number,
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
    VALUES ({2}, {3}, {4}, {5}, {6}, \"{7}\", {8}, {9}, {10}, {11}, {12}, {13}, \"{14}\", {15}, {16}, {17}, {18}, {19}, {20}, {21})
    """.format(i[0], *current_conditions)
    '''[0], current_conditions[1], current_conditions[2], current_conditions[3],
               current_conditions[4], current_conditions[5],
               current_conditions[6], current_conditions[7], current_conditions[8], current_conditions[9],
               current_conditions[10], current_conditions[11],
               current_conditions[12], current_conditions[13], current_conditions[14], current_conditions[15],
               current_conditions[16], current_conditions[17],
               current_conditions[18]'''
    try:
        engine.execute(sql)
    except:
        pass


positions = engine.execute("SELECT number, latitude, longitude FROM static")
region_dict = {}
for n in positions:
    region_dict[n[0]] = area_classifier(n[1], n[2])[0]


def weather():
    while True:
        start = time.time()
        response_a = r.get("https://api.darksky.net/forecast/{}/53.344743,-6.290209?units=si".format(darksky_key))
        response_b = r.get("https://api.darksky.net/forecast/{}/53.353709,-6.268752?units=si".format(darksky_key))
        response_c = r.get("https://api.darksky.net/forecast/{}/53.338747,-6.252959?units=si".format(darksky_key))
        data_a = response_a.json()
        data_b = response_b.json()
        data_c = response_c.json()
        df_a = pd.DataFrame(data_a)
        df_b = pd.DataFrame(data_b)
        df_c = pd.DataFrame(data_c)

        for i in positions:
            if region_dict[i[0]] == "region_a":
                weather_scrape(df_a, i)
            elif region_dict[i[0]] == "region_b":
                weather_scrape(df_b, i)
            elif region_dict[i[0]] == "region_c":
                weather_scrape(df_c, i)
        end = time.time()
        time.sleep(300-(end-start))
weather()
