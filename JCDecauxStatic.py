import pandas as pd
import requests as r
import sqlalchemy as sqla

with open("C:/Users/Daniel/Documents/MSc/Semester 2/Software Engineering Project/authentication.txt") as f:
    auth = f.read().split("\n")

bikes_key = auth[0]
contract = auth[1]
URL = auth[3]
LOG = auth[4]
PWD = auth[5]
PORT = auth[6]
DB = auth[7]
TAB = auth[9]

# Connect to SQL database
ENG = "mysql+mysqldb://{0}:{1}@{2}:{3}/{4}".format(LOG, PWD, URL, PORT, DB)
engine = sqla.create_engine(ENG, echo=False)


def static_scraper():
    """
    Update static table in SQL database with data scraped from JCDecaux
    :return:
    """
    response = r.get("https://api.jcdecaux.com/vls/v1/stations?contract={0}&apiKey={1}".format(contract, bikes_key))
    data = response.json()
    df = pd.DataFrame(data)
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

static_scraper(df)
