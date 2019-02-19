'''
Created on 12 Feb 2019

@author: Ciaran Barron

Retrieve data from DublinBikes API and store in Amazon RDS DB
'''

import sqlalchemy as sqla
import requests as req
import pandas as pd
import time

Key="92ded68b5bc1323a166df2a454415c5658b8f7af"
Contract="Dublin"

URL ="dublinbikesdb.ckigaawhnr98.us-east-2.rds.amazonaws.com"
LOG ="DBAdmin"
PWD ="dublinbikesdatabase"
DB  ="DublinBikesDB"
TAB ="dynamic"
PORT="3306"
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

if __name__ == '__main__':
    
    pass