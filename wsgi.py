"""Web Server Gateway Interface"""

##################
# FOR PRODUCTION
####################
# from src.app import app
from src.app import app
from src.app import socketio  # Import socketio instance

# No need for app.run() here; Gunicorn will serve the app

# if __name__ == "__main__":
#     ####################
#     # FOR DEVELOPMENT
#     ####################
#     app.run(host='0.0.0.0', debug=True)

