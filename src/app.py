from time import time
from flask import Flask, request, jsonify, make_response
from werkzeug.security import check_password_hash
from .routes.pdf_api import bp_api
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, emit
from engineio.payload import Payload
from flask_cors import CORS
from .utils import check_password_and_generate_hash, check_password
from datetime import timedelta, datetime
import json
import os
import uuid
import jwt
from functools import wraps

Payload.max_decode_packets = 50
app = Flask(__name__)
app.config.from_pyfile('settings.py')
app.register_blueprint(bp_api, url_prefix="/api/v1/")

db = SQLAlchemy(app)
socketio = SocketIO(app, ping_interval=2000,
                    ping_timeout=5000, cors_allowed_origins="*")
CORS(app)


# all the models

class UserModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True)
    username = db.Column(db.String(80))
    email = db.Column(db.String(80))
    password = db.Column(db.String(500))
    admin = db.Column(db.Boolean)

    def __repr__(self):
        return f'{self.public_id}'

# custom decorators


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        if not token:
            return jsonify({'message': 'Token required'})
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
            currentuser = UserModel.query.filter_by(
                public_id=data['public_id']).first()
        except:
            print(jwt.decode(token, app.config['SECRET_KEY']))
            return jsonify({'message': 'Token is invalid'}), 401

        return f(currentuser, *args, **kwargs)
    return decorated


# all the app configurations above


@app.route('/api/user/register', methods=['POST'])
def register_user():
    data = request.get_json()
    users = UserModel.query.all()
    for user in users:
        if user.email == data['email']:
            return jsonify({'message': 'email already exists'}), 404
        if user.username == data['username']:
            return jsonify({'message': 'username already exists'}), 404

    hashed_data = check_password_and_generate_hash(
        data['password1'], data['password2'])

    if hashed_data:
        newuser = UserModel(public_id=str(uuid.uuid4(
        )), username=data["username"], email=data["email"], password=hashed_data, admin=False)
        db.session.add(newuser)
        db.session.commit()
        return jsonify({"message": f"account created welcome {newuser.username} "})
    return jsonify(data)


@app.route('/api/user/login')
def login_user():
    auth = request.authorization
    print(auth)
    if not auth or not auth.username or not auth.password:
        return make_response('Couldnt verify', 401, {'WWW-Authenticate': 'Basic relam =  "Login required!"'})
    user = UserModel.query.filter_by(username=auth.username).first()
    print(user)

    if not user:
        return make_response('Couldnt verify', 401, {'WWW-Authenticate': 'Basic relam =  "Login required!"'})

    if check_password_hash(user.password, auth.password):
        token = jwt.encode({'public_id': user.public_id, 'exp': datetime.utcnow(
        ) + timedelta(minutes=30)}, app.config['SECRET_KEY'])

        return jsonify({'auth_token': token.decode('UTF-8')})

    return make_response('Couldnt verify', 401, {'WWW-Authenticate': 'Basic relam =  "Login required!"'})


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
