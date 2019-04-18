import sqlalchemy as sqla
import pandas as pd

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
    # dialect+driver://username:password@host:port/database
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
    sql = "SELECT * FROM {0}.{1};".format(db,tab)
    
    cols = ['number', 'contract_name', 'name', 'address', 
            'latitude', 'longitude', 'banking', 'bonus']
    
    static_data = pd.DataFrame(engine.execute(sql), columns=cols)
    
    static_data.drop(['contract_name','banking','bonus'], axis=1, inplace=True)
    
    return static_data

def read_weather(i):
    """
    Read weather real time (stored data not real time) data
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
        
