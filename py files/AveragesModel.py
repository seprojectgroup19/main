import numpy as np
from ReadFromDB import station_dict_row as sdr


def get_hourly_average(df, weather_df, hour, type, half):
    """
    Returns the average bikes / available stands for a given station-day-hour(-half hour) combination

    :param df: station data frame
    :param weather_df: weather data frame with weather_times previously executed on it
    :param day: day of interest as a string ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")
    :param hour: hour of interest (integer from 0 - 23)
    :param type: specify "bikes" or "stands" to return just bikes/stands, any other input returns both
    :param kwargs: include which half of the hour you want to return

    E.g.: get_hourly_average(df, "Mon", 9, "bikes", "first") will return the average number of available bikes
    for 9:00am - 9:30am on Monday at the given station.
    """

    last_weather_row = sdr(weather_df, 'last')
    current_weather_type = last_weather_row['icon']

    dates = list()

    for i in zip(weather_df['icon'], weather_df['date']):
        if i[0] == current_weather_type:
            if i[1] not in dates:
                dates.append(i[1])
    bikes = list()
    stands = list()

    for i in zip(df['date'], df['hour'], df['first_half_hour'],
                 df['second_half_hour'], df['available_bikes'], df['available_bike_stands']):
        if i[0] in dates and i[1] == hour:
            if half == "first":
                if i[2]:
                    bikes.append(i[4])
                    stands.append(i[5])
            elif half == "second":
                if i[3]:
                    bikes.append(i[4])
                    stands.append(i[5])

    if type == "bikes":
        return np.mean(bikes)
    elif type == "stands":
        return np.mean(stands)
    else:
        return np.mean(bikes), np.mean(stands)