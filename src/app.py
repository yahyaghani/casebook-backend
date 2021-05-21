from src.endpoints.routes.blueprint_api import bp_api
from flask import Flask, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from engineio.payload import Payload
import json
import os

Payload.max_decode_packets = 50

app = Flask(__name__)
socketio = SocketIO(app, ping_interval=2000,
                    ping_timeout=5000, cors_allowed_origins="*")
CORS(app)

# CORS(socketio)
app.config['CORS_HEADERS'] = 'application/json'

app.register_blueprint(bp_api, url_prefix="/api/v1/")


@socketio.on('connect')
def test_connect():
    print('Connection is on!!')

    @socketio.on('get-document')
    def getDocumentId(documentId):
        if os.path.isfile(documentId + '.json'):
            print("\nFile exists\n")
            with open(documentId + '.json') as json_file:
                data = json.load(json_file)
                emit('load-document', data)
        else:
            print('\nFile does not exist\n')
            with open(documentId + '.json', 'w') as outfile:
                json.dump({'data': {'ops': []}}, outfile)
                emit('load-document', {'data': {'ops': []}})

        @socketio.on('send-changes')
        def sendChanges(delta):
            emit('receive-changes', delta, broadcast=True, include_self=False)

        @socketio.on('save-document')
        def saveData(data):
            with open(documentId + '.json', 'w') as outfile:
                json.dump(data, outfile)

        @socketio.on('disconnect')
        def disconnect():
            print('disconnected!')


if __name__ == "__main__":
    socketio.run(host='0.0.0.0', debug=True)
