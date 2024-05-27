from flask_socketio import SocketIO
from flask import Flask

app = Flask(__name__)
socketio_instance = SocketIO(app, cors_allowed_origins="http://localhost:3000", ping_interval=2000, ping_timeout=30000)
