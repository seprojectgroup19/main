'''
Created on 19 Feb 2019

@author: Ciaran
'''

import sqlalchemy as sqla
import requests as req
import pandas as pd
import time

with open('../authentication.txt') as f:
    auth=f.read().split('\n')

Key=auth[0]
Contract=auth[1]
URL =auth[2]
LOG =auth[3]
PWD =auth[4]
DB  =auth[5]
TAB =auth[6]
PORT=auth[7]

# Use the version below for EC2 instance with pymysql installed
ENG ="mysql+pymysql://{0}:{1}@{2}:{3}/{4}".format(LOG,PWD,URL,PORT,DB)

engine = sqla.create_engine(ENG,echo=False)

def scrape_dynamic_data(count, err):

    response = req.get('https://api.jcdecaux.com/vls/v1/stations?contract={0}&apiKey={1}'.format(Contract,Key))
    Data = pd.DataFrame(response.json())

    available_bike_stands = Data['available_bike_stands']
    available_bikes = Data['available_bikes']
    bike_stands = Data['bike_stands']
    last_update = Data['last_update']
    number = Data['number']
    status = Data['status']

    for i in range(Data.shape[0]):

        SQL = """
        INSERT INTO {0}.{1} (available_bike_stands,
                   available_bikes,
                   bike_stands,
                   last_update,
                   number,
                   status)
        VALUES ({2}, {3}, {4}, {5}, {6}, \"{7}\")
        """.format(
            DB,
            TAB,
            available_bike_stands[i],
            available_bikes[i],
            bike_stands[i],
            last_update[i],
            number[i],
            status[i])

        try:
            engine.execute(SQL)
            count += 1

        except:
            err += 1
            pass

    return count,err

def continuous_scrape():

    while True:

        count, err = 0,0
        S = time.time()
        #scrape data and write to RDS DB
        count, err = scrape_dynamic_data(count,err)

        E = time.time()
        runtime = E - S

        dtime=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

        log = '\n{} lines ({} errors) written to DublinBikesDB.dynamic at {}. Run time: {:.4} Sec'.format(count, err, dtime, runtime)

        with open('update_log.txt','a') as uf:
            uf.write(log)

        time.sleep(300-(E-S))

continuous_scrape()
