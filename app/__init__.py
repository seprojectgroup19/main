from flask import Flask
app = Flask(__name__)

if __name__ == "__main__":
    app.run(ssl_context='adhoc')
from app import views
