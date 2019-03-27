from flask import Flask
from flask_cors import CORS
app = Flask(__name__)
CORS(app, resources={r"/*": {["http://localhost:8000", "http://3.80.56.170:5000/"]}})

from app import views
