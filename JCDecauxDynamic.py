import sqlalchemy as sqla
import time
import requests as r
import pandas as pd

with open("C:/Users/Daniel/Documents/MSc/Semester 2/Software Engineering Project/authentication.txt") as f:
    auth = f.read().split("\n")

# Authentication data from file
bikes_key = auth[0]
contract = auth[1]
URL = auth[3]
LOG = auth[4]
PWD = auth[5]
PORT = auth[6]
DB = auth[7]
TAB = auth[10]

# Connect to SQL database
ENG = "mysql+mysqldb://{0}:{1}@{2}:{3}/{4}".format(LOG, PWD, URL, PORT, DB)
engine = sqla.create_engine(ENG, echo=False)


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
                    VALUES ({2},{3],{4},{5},{6},{7})
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


dynamic_scraper()