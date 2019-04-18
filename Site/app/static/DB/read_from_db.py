import matplotlib.pyplot as plt
from datetime import datetime
import sqlalchemy as sqla
import pandas as pd
import numpy as np

def read_auth():
    """
    Function to read authentication file to save time for each script
    :return: API key for JCDecaux, JCDecaux contract, API key for darksky, SQL database name, engine for SQL database
    """
    with open("authentication.txt") as f:
        auth = f.read().split("\n")

    # Authentication data from file
    bikes_key = auth[0]
    contract = auth[1]
    darksky_key = auth[2]
    url = auth[3]
    log = auth[4]
    pwd = auth[5]
    port = auth[6]
    db = auth[7]

    # Connect to SQL database
    eng = "mysql+mysqldb://{0}:{1}@{2}:{3}/{4}".format(log, pwd, url, port, db)
    engine = sqla.create_engine(eng, echo=False)
    return [bikes_key, contract, darksky_key, db, engine]

[db, engine] = read_auth()[3:]

def get_static_data():
    """
    Generate a dataframe containing all the static bikes data
    return:
    (dataframe) all static data
    """

    tab = "static"
    sql = "SELECT * FROM {0}.{1};".format(db, tab)

    cols = ['number', 'contract_name', 'name', 'address',
            'latitude', 'longitude', 'banking', 'bonus']

    static_data = pd.DataFrame(engine.execute(sql), columns=cols)

    static_data.drop(['contract_name', 'banking', 'bonus'], axis=1, inplace=True)

    return static_data


def read_weather(i):
    """
    Read weather real time data
    :param i: station number
    :return: weather df
    """
    tab = "weather"

    sql = """SELECT * FROM {0}.{1} WHERE number = {2}""".format(db, tab, i)
    result = engine.execute(sql)
    weather_df = pd.DataFrame(result,
                              columns=['number',
                                       'apparentTemperature',
                                       'cloudCover',
                                       'dewPoint',
                                       'humidity',
                                       'icon',
                                       'nearestStormBearing',
                                       'nearestStormDistance',
                                       'ozone',
                                       'precipIntensity',
                                       'precipProbability',
                                       'pressure',
                                       'summary',
                                       'temperature',
                                       'time',
                                       'uvIndex',
                                       'visibility',
                                       'windBearing',
                                       'windGust',
                                       'windSpeed'])
    weather_df.drop('number', axis=1, inplace=True)
    return weather_df


def station(i):
    """
    Pulls data from database for given station and stores in a data frame, dropping unnecessary columns.
    :param i: station number
    :return: returns data frame
    """

    tab = "dynamic"

    sql = """SELECT * FROM {0}.{1} WHERE number = {2}""".format(db, tab, i)
    result = engine.execute(sql)
    station_df = pd.DataFrame(result,
                           columns=['number',
                                    'status',
                                    'bike_stands',
                                    'available_bike_stands',
                                    'available_bikes',
                                    'last_updated', ])
    station_df.drop('number', axis=1, inplace=True)
    return station_df


def create_station_dictionary(*argv):
    """
    Returns a dictionary of data pulled from SQL database.
    Usage:
    from ReadFromDB import create_station_dictionary as csd
    stations = csd(x, y, z) OR stations = csd([x, y, z]) OR stations = csd(range(x, z)), where x, y, z are of type int
    :param argv: tuple of ints, list or range of station numbers
    :return: dictionary
    """
    station_dict = {}
    if len(argv) == 1:
        for arg in argv:
            if type(arg) == int:
                if arg == 20:
                    # Station 20 doesn't exist
                    continue
                else:
                    if not (2 <= arg <= 115):
                        raise Exception(
                            f"{arg} must be a station number in the range [2, 115]"
                        )
                    station_dict[arg] = station(arg)

            elif type(arg) == range or type(arg) == list:
                for item in list(arg):
                    if not (type(item) == int):
                        raise Exception(
                            f"{item} must be of type int."
                        )
                    elif item == 20:
                        # Station 20 doesn't exist
                        continue
                    else:
                        if not (2 <= item <= 115):
                            raise Exception(
                                f"{item} must be a station number in the range [2, 115]"
                            )
                        station_dict[item] = station(item)
                if type(arg) == range:
                    station_dict[arg[-1] + 1] = station(arg[-1] + 1)
            else:
                raise Exception(
                    f"{arg} must be of type int, range or list."
                )
    elif len(argv) >= 2:
        for arg in argv:
            if not (type(arg) == int):
                raise Exception(
                    f"{arg} must be of type int."
                )
            else:
                if not (2 <= arg <= 115):
                    raise Exception(
                        f"{arg} must be a station number in the range [2, 115]"
                    )
                station_dict[arg] = station(arg)

    else:
        raise Exception("Invalid number of arguments. Provide at least one argument.")

    return station_dict


def station_dict_row(station_dict, *argv):
    """
    Assumes station_dict is a dictionary of one or more data frames created using create_station_dictionary
    Usage:
    from ReadfromDB import station_dict_row as sdr
    rows = sdr(station) OR sdr(station, x) OR sdr(station, "last"), where x is a valid row index
    :param station_dict: dictionary containing a data frame of one or more stations
    :param argv: which row to output, can be an integer or "last" or "all" or left blank (default to "all")
    :return: returns dictionary of the specified rows
    """
    if len(argv) == 1:
        row = argv[0]
    elif len(argv) > 1:
        raise Exception(
            "Only one argument allowed for row number."
        )
    else:
        row = "all"

    if len(station_dict.keys()) == 1:
        for key in station_dict.keys():
            station = station_dict[key]

            if row == "last":
                return station.iloc[station.shape[0] - 1]
            elif row == "all":
                return station
            else:
                if not (0 <= row <= station.shape[0]):
                    raise Exception(
                        "Row kwarg must be valid."
                    )
                else:
                    return station.iloc[row]
    elif len(station_dict.keys()) > 1:
        row_dict = {}
        for key in station_dict.keys():
            station = station_dict[key]

            if row == "last":
                row_dict[key] = station.iloc[station.shape[0] - 1]
            elif row == "all":
                row_dict[key] = station
            else:
                if not (0 <= row <= station.shape[0]):
                    raise Exception(
                        "Row kwarg must be valid."
                    )
                else:
                    row_dict[key] = station.iloc[row]

        return row_dict
    
    
def add_times(df, **kwargs):
    """
    Converts column 'last_updated' from ms to s, adds columns for date/day/hour/min/sec. Adds a column specifying
    if each row lies in the first or second 30 minutes of an hour.
    """
    reindex = False
    if "reindex" in kwargs:
        reindex = kwargs["reindex"]

    make_timestamp = (lambda x: int(x / 1000))
    df.last_updated = df.last_updated.apply(make_timestamp)
    times = df.last_updated
    length = len(times)
    minute = list(np.zeros(length))
    hour = list(np.zeros(length))
    second = list(np.zeros(length))
    day = list(np.zeros(length))
    date = list(np.zeros(length))

    for i in range(length):
        date[i] = datetime.fromtimestamp(times[i]).strftime("%x")
        day[i] = datetime.fromtimestamp(times[i]).strftime("%a")
        hour[i] = int(datetime.fromtimestamp(times[i]).strftime("%H"))
        minute[i] = int(datetime.fromtimestamp(times[i]).strftime("%M"))
        second[i] = int(datetime.fromtimestamp(times[i]).strftime("%S"))

    first_half = []
    second_half = []

    for m in minute:
        if m < 30:
            first_half.append(True)
            second_half.append(False)
        else:
            first_half.append(False)
            second_half.append(True)

    df = df.assign(date=pd.Series(date, index=df.index),
                   day=pd.Series(day, index=df.index),
                   hour=pd.Series(hour, index=df.index),
                   minute=pd.Series(minute, index=df.index),
                   second=pd.Series(second, index=df.index),
                   first_half_hour=pd.Series(first_half, index=df.index),
                   second_half_hour=pd.Series(second_half, index=df.index))
    if reindex:
        df.index = pd.to_datetime(df.last_updated, unit='s')
    return df


def print_bikes_stands(df, number, **kwargs):
    """
    Returns subplots within figure showing the available bike stands and available stands at station[number]. Color
    coded - green indicates availability > 50%, yellow indicates 50%> availability >20%, red indicates
    availability < 20%`
    """
    if "day" in kwargs:
        day = kwargs["day"]
    else:
        day = False
    available_bikes_avg = list()
    available_stands_avg = list()
    for i in range(24):
        if day:
            available_bikes_avg.append(np.mean(df[df.hour==i][df.day==str(day)].available_bikes))
            available_stands_avg.append(np.mean(df[df.hour==i][df.day==str(day)].available_bike_stands))
        else:
            available_bikes_avg.append(np.mean(df[df.hour==i].available_bikes))
            available_stands_avg.append(np.mean(df[df.hour==i].available_bike_stands))

    total_stands = max(df.bike_stands)
    width = 0.5
    idx = np.asarray([i for i in range(24)])
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(20,8))

    if day:
        ax1.set_title("Station " + str(number) + ", " + str(day), fontsize=26)
    else:
        ax1.set_title("Station " + str(number), fontsize=26)

    bars1 = ax1.bar(idx, available_bikes_avg, alpha=0.5, label='Available Bikes', width=width)
    ax1.set_ylim([0, total_stands])
    ax1.set_xticks(idx)
    ax1.set_xlabel('Hour', fontsize=16)
    ax1.set_ylabel('Available Bikes', fontsize=16)

    for bar in bars1:
        if bar.get_height()<total_stands*0.2:
            bar.set_color('red')
        elif bar.get_height()<total_stands*0.5:
            bar.set_color('yellow')
        else:
            bar.set_color('green')

    bars2 = ax2.bar(idx, available_stands_avg, alpha=0.5, label='Available Stands', width=width)
    ax2.set_ylim([0, max(df.bike_stands)])
    ax2.set_xticks(idx)
    ax2.set_xlabel('Hour', fontsize=16)
    ax2.set_ylabel('Available Stands', fontsize=16)

    for bar in bars2:
        if bar.get_height()<total_stands*0.2:
            bar.set_color('red')
        elif bar.get_height()<total_stands*0.5:
            bar.set_color('yellow')
        else:
            bar.set_color('green')

    plt.show()


def get_hourly_average(df, day, hour, type, **kwargs):
    """
    Returns the average bikes / available stands for a given station-day-hour(-half hour) combination
    :param df: station data frame
    :param day: day of interest as a string ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")
    :param hour: hour of interest (integer from 0 - 23)
    :param type: specify "bikes" or "stands" to return just bikes/stands, any other input returns both
    :param kwargs: include which half of the hour you want to return
    E.g.: get_hourly_average(df, "Mon", 9, "bikes", "first") will return the average number of available bikes
    for 9:00am - 9:30am on Monday at the given station.
    """

    if "half" in kwargs:
        half = kwargs["half"]
    else:
        half = False

    if half == "first":
        hourly_bikes_avg = np.mean(df[df.hour == hour][df.day == str(day)][df.first_half_hour].available_bikes)
        hourly_stands_avg = np.mean(df[df.hour == hour][df.day == str(day)][df.first_half_hour].available_bike_stands)
    elif half == "second":
        hourly_bikes_avg = np.mean(df[df.hour == hour][df.day == str(day)][df.second_half_hour].available_bikes)
        hourly_stands_avg = np.mean(df[df.hour == hour][df.day == str(day)][df.second_half_hour].available_bike_stands)
    else:
        hourly_bikes_avg = np.mean(df[df.hour == hour][df.day == str(day)].available_bikes)
        hourly_stands_avg= np.mean(df[df.hour == hour][df.day == str(day)].available_bike_stands)

    if type == "bikes":
        return hourly_bikes_avg
    elif type == "stands":
        return hourly_stands_avg
    else:
        return hourly_bikes_avg, hourly_stands_avg