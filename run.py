import os
from app import app
if __name__ == "__main__":
 app.run(host='0.0.0.0', threaded=True, port=5000, ssl_context='adhoc')
