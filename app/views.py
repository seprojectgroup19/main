from flask import render_template
from flask import request, make_response,current_app
from app import app
from functools import update_wrapper
from datetime import timedelta
import mysql.connector
import os
import requests as r
import json


@app.route('/')
def index():
 returnDict = {}
 returnDict['user'] = 'Cormac' # Feel free to put your name here!
 returnDict['title'] = 'Home'
 return render_template("index.html", **returnDict)





