from Authenticator import read_auth
import time
import requests as r
import pandas as pd


def dynamic_scraper():
    while True:
        # Start timer (only want to run function every 5 minutes - execution time)
        start = time.time()
        # Connect to JCDecaux API
        response = r.get("https://api.jcdecaux.com/vls/v1/stations?contract={0}&apiKey={1}".format(contract, bikes_key))
        data = response.json()
        df = pd.DataFrame(data)
        # Loop over rows in scraped data frame
        for i, row in df.iterrows():
            # Insert values into table in SQL databse
            sql = """INSERT INTO {0}.{1}
                        (available_bike_stands,
                        available_bikes,
                        bike_stands,
                        last_update,
                        number,
                        status)
                    VALUES ({2},{3},{4},{5},{6},{7})
                    """.format(DB,
                               TAB,
                               row.available_bike_stands,
                               row.available_bikes,
                               row.bike_stands,
                               row.last_update,
                               row.number,
                               row.status)
            engine.execute(sql)
        end = time.time()
        time.sleep(300-(end-start))


bikes_key, contract, engine, DB = read_auth()
TAB = "dynamic"
dynamic_scraper()