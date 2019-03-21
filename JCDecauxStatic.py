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

# Connect to SQL database
ENG = "mysql+mysqldb://{0}:{1}@{2}:{3}/{4}".format(LOG, PWD, URL, PORT, DB)
engine = sqla.create_engine(ENG, echo=False)