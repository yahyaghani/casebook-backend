"""Flask Application"""

# load libaries
from flask import Flask, jsonify
from flask_cors import CORS
import sys

# load modules
from src.endpoints.blueprint_api import bp_api

# init Flask app
app = Flask(__name__)
CORS(app) # This will enable CORS for all routes
app.config['CORS_HEADERS'] = 'application/json'

# register blueprints. ensure that all paths are versioned!
app.register_blueprint(bp_api, url_prefix="/api/v1/")


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
