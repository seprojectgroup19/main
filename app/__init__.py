from flask import Flask
from flask_cors import CORS
app = Flask(__name__)
CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

@cross_origin(origins=['http://localhost:5000',"http://3.80.56.170:5000/"])

from app import views
