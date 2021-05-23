from time import time
from flask import Flask, request, jsonify, make_response, url_for, flash
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename
from .routes.pdf_api import bp_api
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, emit
from engineio.payload import Payload
from flask_cors import CORS, cross_origin
from .utils import check_password_and_generate_hash, check_password
from datetime import timedelta, datetime
import json
import os
import uuid
import jwt
from functools import wraps

Payload.max_decode_packets = 50
ALLOWED_EXTENSIONS = ['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif']
app = Flask(__name__)
app.config['CORS_HEADERS'] = 'Content-Type'
cors = CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})

UPLOAD_FOLDER = os.path.join(f'{os.path.dirname(__file__)}/uploads')
app.config.from_pyfile('settings.py')
app.register_blueprint(bp_api, url_prefix="/api/v1/")
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


db = SQLAlchemy(app)
socketio = SocketIO(app, ping_interval=2000,
                    ping_timeout=5000)


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
@cross_origin(origin='localhost', headers=['Content-Type', 'application/json'])
def register_user():
    temp_data = request.data
    data = json.loads(temp_data)
    print(data)
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


@app.route('/api/user/login', methods=['GET'])
@cross_origin(origin='localhost', headers=['Content-Type', 'Authorization'])
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


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/upload/file', methods=['POST'])
@token_required
def upload_file(currentuser):
    global UPLOAD_FOLDER
    if 'file' not in request.files:
        resp = jsonify({'message': 'No file part in the request'})
        resp.status_code = 400
        return resp
    file = request.files['file']
    if file.filename == '':
        resp = jsonify({'message': 'No file selected for uploading'})
        resp.status_code = 400
        return resp
    if file and allowed_file(file.filename):
        dir = os.path.join(os.path.dirname(__file__) +
                           '/uploads/', currentuser.public_id)
        if os.path.isdir(dir):
            print("doesnt exist")
        else:
            os.mkdir(dir)
            UPLOAD_FOLDER = dir

        filename = secure_filename(file.filename)
        file.save(os.path.join(dir, filename))
        resp = jsonify({'message': 'File successfully uploaded'})
        resp.status_code = 201
        return resp
    else:
        resp = jsonify(
            {'message': 'Allowed file types are txt, pdf, png, jpg, jpeg, gif'})
        resp.status_code = 400
        return resp


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
