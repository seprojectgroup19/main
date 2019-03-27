@app.route('/lookup', methods=[GET])
import mysql.connector
import os
import requests as r
import json

def lookup(n):
    val_list = []
    validator = open("validation.txt", "r")
    for line in validator:
        val_list.append(line.rstrip())

    mydb = mysql.connector.connect(
      host=val_list[0],
      user=val_list[1],
      passwd=val_list[2],
      database=val_list[3]
    )

    id = n
    mycursor = mydb.cursor()
    result_list = []

    sql = "SELECT available_bike_stands, available_bikes, last_update FROM DublinBikesDB.dynamic WHERE number = '"+str(n)+"' ORDER BY last_update DESC LIMIT 1"
    mycursor.execute(sql)

    for (available_bike_stands,  available_bikes, last_update) in mycursor:
        result_list.extend( [available_bike_stands,  available_bikes, last_update])

    return result_list

print(lookup(4))


