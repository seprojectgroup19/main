from flask import Flask
from flask_cors import CORS
app = Flask(__name__)
cors = CORS(app, resources={r"/api/*": {"origins": ["http://localhost:5000", "http://3.80.56.170:5000/"]}})

from app import views
