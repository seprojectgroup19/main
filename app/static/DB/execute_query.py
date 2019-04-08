"""
Script to execute a given sql query for the database

Author: Ciaran
Date: 08.04.2019
"""

import sqlalchemy as sqla

with open("authentication.txt") as f:
    auth = f.read().split("\n")

# Authentication data from file
url = auth[3]
log = auth[4]
pwd = auth[5]
port = auth[6]
db = auth[7]

# Engine to Connect to SQL database
eng = "mysql+mysqldb://{0}:{1}@{2}:{3}/{4}".format(log, pwd, url, port, db)
engine = sqla.create_engine(eng, echo=False)


def execute(query):

    # Attempt to connect to the database (return 0 if false)
    try:
        connection = engine.connect()
    except Exception as ex:
        print(repr(ex))
        return 0

    # Attempt to execute the gievn Query (return 0 if false)
    try:
        result = connection.execute(query)
    
    except Exception as e:
        print(repr(e))
        return 0

    # Close connection to the database
    connection.close()

    return result