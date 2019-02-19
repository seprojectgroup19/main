'''
Created on 12 Feb 2019

@author: Ciaran Barron

Retrieve data from DublinBikes API and store in Amazon RDS DB
'''

import sqlalchemy as sqla
import requests as req
import pandas as pd
import time

with open('authentication.txt') as f:
    auth=f.read().split('\n')
    
Key=auth[0]
Contract=auth[1]
URL =auth[2]
LOG =auth[3]
PWD =auth[4]
DB  =auth[5]
TAB =auth[6]
PORT=auth[7]

ENG ="mysql+mysqldb://{0}:{1}@{2}:{3}/{4}".format(LOG,PWD,URL,PORT,DB)

engine = sqla.create_engine(ENG,echo=False)

def scrape_dynamic_data():
    
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

        except Exception as e:
            
            dtime=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            with open('Error_log.txt','r') as f:
                f.write('Error detected at {}\n'.format(dtime))
                f.write('=' * 10,'\n')
                f.write(e,'\n')
                f.write('=' * 10,'\n')
            continue
            
def continuous_scrape():
    
    while True:
        
        # start timer to time how long script takes
        S = time.time()      

        #scrape data and write to RDS DB
        scrape_dynamic_data()

        # end timer
        E = time.time()

        # Print update message
        dtime=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        print('Data written to DublinBikesDB.dynamic at {0}'.format(dtime))

        # sleep for 1 min
        time.sleep(60)
        

        

if __name__ == '__main__':
    
    continuous_scrape()