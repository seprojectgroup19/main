from Authenticator import read_auth
from datetime import datetime
import numpy as np
import pandas as pd


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


def weather_times(df, **kwargs):
    """
    Converts column 'last_updated' from ms to s, adds columns for date/day/hour/min/sec. Adds a column specifying
    if each row lies in the first or second 30 minutes of an hour.
    """
    reindex = False
    if "reindex" in kwargs:
        reindex = kwargs["reindex"]

    times = df.time
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
        df.index = pd.to_datetime(df.time, unit='s')
    return df