import matplotlib.pyplot as plt
import numpy as np


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
            available_bikes_avg.append(np.mean(df[df.hour == i][df.day == str(day)].available_bikes))
            available_stands_avg.append(np.mean(df[df.hour == i][df.day == str(day)].available_bike_stands))
        else:
            available_bikes_avg.append(np.mean(df[df.hour == i].available_bikes))
            available_stands_avg.append(np.mean(df[df.hour == i].available_bike_stands))

    total_stands = max(df.bike_stands)
    width = 0.5
    idx = np.asarray([i for i in range(24)])
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(20, 8))

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
        if bar.get_height() < total_stands * 0.2:
            bar.set_color('red')
        elif bar.get_height() < total_stands * 0.5:
            bar.set_color('yellow')
        else:
            bar.set_color('green')

    bars2 = ax2.bar(idx, available_stands_avg, alpha=0.5, label='Available Stands', width=width)
    ax2.set_ylim([0, max(df.bike_stands)])
    ax2.set_xticks(idx)
    ax2.set_xlabel('Hour', fontsize=16)
    ax2.set_ylabel('Available Stands', fontsize=16)

    for bar in bars2:
        if bar.get_height() < total_stands * 0.2:
            bar.set_color('red')
        elif bar.get_height() < total_stands * 0.5:
            bar.set_color('yellow')
        else:
            bar.set_color('green')

    plt.show()
