from Authenticator import read_auth
import pandas as pd


def station(i):
    [DB, engine] = read_auth()[3:]
    TAB = "dynamic"

    sql = """SELECT * FROM {0}.{1}
          WHERE number = {2}
          """.format(DB, TAB, i)
    result = engine.execute(sql)
    station = pd.DataFrame(result,
                           columns=['number',
                                    'status',
                                    'bike_stands',
                                    'available_bike_stands',
                                    'available_bikes',
                                    'last_updated',])
    station.drop('number', axis=1, inplace=True)
    return station


def create_station_dictionary(*argv):
    station_dict = {}

    if len(argv) == 1:
        for arg in argv:

            if type(arg) == int:
                station_dict[arg] = station(arg)

            elif type(arg) == range or type(arg) == list:
                for item in list(arg):
                    if not (type(item) == int):
                        raise Exception(
                            f"{item} must be of type int."
                        )
                    else:
                        station_dict[item] = station(item)
                if type(arg) == range:
                    station_dict[arg[-1]+1] = station(arg[-1]+1)
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
                station_dict[arg] = station(arg)

    else:
        raise Exception("Invalid number of arguments. Provide at least one argument.")

    return station_dict