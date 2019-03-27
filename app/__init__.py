from flask import Flask
from flask_cors import CORS
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins":["http://localhost:8000", "http://mywebsite.example.com"]}})

from app import views
