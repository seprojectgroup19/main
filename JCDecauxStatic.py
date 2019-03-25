import pandas as pd
import requests as r
from Authenticator import read_auth


def static_scraper():
    """
    Update static table in SQL database with data scraped from JCDecaux
    """
    # Connect to JCDecaux
    response = r.get("https://api.jcdecaux.com/vls/v1/stations?contract={0}&apiKey={1}".format(contract, bikes_key))
    data = response.json()
    df = pd.DataFrame(data)

    # Begin populating table
    for i, row in df.iterrows():
        sql = """UPDATE {0}.{1}
        SET contract_name='Dublin',
        banking=""" + str(row.banking) + """,
        bonus=""" + str(row.bonus) + """
        WHERE number=""" + str(row.number)

        engine.execute(sql)

    # Requires correct .csv file in same directory
    static_data = pd.read_csv("Dublin.csv")
    for i, row in static_data.iterrows():
        sql = """INSERT INTO {0}.{1} (number, name, address, latitude, longitude)
        VALUES ({2}, {3}, {4}, {5}, {6})
        """.format(DB, TAB, int(row[0]), row[1], row[2], float(row[3])), float(row[4])
        engine.execute(sql)

TAB = "static"
[bikes_key, contract], [DB, engine] = read_auth()[:2], read_auth()[3:]

# ONLY RUN ONCE
static_scraper()
