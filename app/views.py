from flask import render_template
from app import app
@app.route('/')
def index():
 returnDict = {}
 returnDict['user'] = 'Cormac' # Feel free to put your name here!
 returnDict['title'] = 'Home'
 return render_template("index.php", **returnDict)
