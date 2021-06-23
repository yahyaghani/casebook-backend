from time import time
from flask import Flask, request, jsonify, make_response, url_for, flash, send_file
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename
from .routes.pdf_api import bp_api
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.inspection import inspect
from flask_migrate import Migrate
from flask_socketio import SocketIO, emit
from engineio.payload import Payload
from flask_cors import CORS, cross_origin
from .utils import check_password_and_generate_hash, check_password
from datetime import timedelta, datetime
import json
import os
from os import listdir
from os.path import isfile, join
import uuid
import jwt
from functools import wraps
import spacy 
from pdfminer.layout import LAParams, LTTextBox
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from collections import Counter
from typing import Pattern 
import pandas as pd
import sys
from .textAnonymizer import text_anonymizer

output_dir="./judgclsfymodel8"
nlp = spacy.load(output_dir)

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

migrate = Migrate(app, db)
socketio = SocketIO(app,  cors_allowed_origins="http://localhost:3000", ping_interval=2000, ping_timeout=30000)


# all the models

class UserModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True)
    fname = db.Column(db.String(80))
    lname = db.Column(db.String(80))
    username = db.Column(db.String(80), unique=True)
    city = db.Column(db.String(80))
    country = db.Column(db.String(80))
    organisation = db.Column(db.String(80))
    email = db.Column(db.String(80))
    password = db.Column(db.String(500))
    admin = db.Column(db.Boolean)
    FilePosts = db.relationship('FilePost', backref=db.backref('user_model', lazy='joined'), lazy='select')
    Ratings = db.relationship('Rating', backref=db.backref('user_model', lazy='select'), lazy='select')

    def __repr__(self):
        return f'{self.public_id}'

class FilePost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fileName = db.Column(db.String(80))
    user_id = db.Column(db.Integer, db.ForeignKey('user_model.id'), nullable=False)
    total_rating = db.Column(db.Integer)
    ratings = db.relationship('Rating', backref=db.backref('file_post', lazy='select'), lazy='joined')
    
    def __repr__(self):
        return f'{self.id}'
    
    def serialize(self):
        post = {c: getattr(self, c) for c in inspect(self).attrs.keys()}
        if 'user_model' in post and getattr(self, 'user_model'):
            del post['user_model']
            post['user_info'] = {}
            for c in inspect(self.user_model).attrs.keys():
                post['user_info'][c] = getattr(self.user_model, c)
            del post['user_info']['FilePosts']
            del post['user_info']['Ratings']
            del post['user_info']['password']
        if 'ratings' in post:
            post['all_ratings'] = []
            for rating in post['ratings']:
                newRating = {}
                newRating['rating'] = getattr(rating, 'rating')
                newRating['review'] = getattr(rating, 'review')
                newRating['id'] = getattr(rating, 'id')
                newRating['user_id'] = getattr(rating, 'user_id')
                post['all_ratings'].append(newRating)
            del post['ratings']
        return post

class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer)
    review = db.Column(db.String(80))
    post_id = db.Column(db.Integer, db.ForeignKey('file_post.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user_model.id'), nullable=False)

    def __repr__(self):
        return f'{self.id}'

    def serialize(self):
        return {c: getattr(self, c) for c in inspect(self).attrs.keys()}

# custom decorators

db.create_all()

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
@cross_origin(origin="localhost", headers=['Content-Type', 'application/json'])
def register_user():
    temp_data = request.data
    data = json.loads(temp_data)
    print(data)
    try:
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
            )), username=data["username"], email=data["email"], password=hashed_data, admin=False,
            fname=data["fname"], lname=data["lname"], city=data["city"], country=data["country"],
            organisation=data["organisation"])
            db.session.add(newuser)
            db.session.commit()
            return jsonify({"message": f"account created welcome {newuser.username} "})
        return jsonify(data)
    except Exception as err:
        print('An exception occured!!')
        print(err)
        return make_response('Something went wrong!!', 500)

@app.route('/api/user/login', methods=['POST'])
@cross_origin(origin='localhost', headers=['Content-Type', 'Authorization'])
def login_user():
    try:
        auth = request.data
        auth = json.loads(auth)
        print(auth)
        if not auth or not auth['username'] or not auth['password']:
            return make_response('Couldnt verify', 401, {'WWW-Authenticate': 'Basic relam =  "Login required!"'})
        user = UserModel.query.filter_by(username=auth['username']).first()
        print(user)
        if not user:
            return make_response('Couldnt verify', 401, {'WWW-Authenticate': 'Basic relam =  "Login required!"'})

        if check_password_hash(user.password, auth['password']):
            token = jwt.encode({'public_id': user.public_id, 'exp': datetime.utcnow(
            ) + timedelta(minutes=30)}, app.config['SECRET_KEY'])
            return jsonify({'auth_token': token.decode('UTF-8'), 'userId': user.id, 'userPublicId': user.public_id, 
            'username': user.username, 'email': user.email,
            'city': user.city, 'country': user.country,
            'fname': user.fname, 'lname': user.lname,
            'organisation': user.organisation})
    except Exception as err:
        print('An exception occured!!')
        print(err)
        return make_response('Something went wrong!!', 500)

    return make_response('Couldnt verify', 401, {'WWW-Authenticate': 'Basic relam =  "Login required!"'})


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/upload/file', methods=['POST'])
@token_required
def upload_file(currentuser):
    global UPLOAD_FOLDER
    try:
        if 'file' not in request.files:
            print('No files found')
            resp = jsonify({'message': 'No file part in the request'})
            resp.status_code = 400
            return resp
        file = request.files['file']
        if file.filename == '':
            print('No filename selected')
            resp = jsonify({'message': 'No file selected for uploading'})
            resp.status_code = 400
            return resp
        if file and allowed_file(file.filename):
            dir = os.path.join(os.path.dirname(__file__) +
                            '/uploads/', currentuser.public_id)
            if os.path.isdir(dir) == False:
                print("doesnt exist")
                os.makedirs(dir, exist_ok=True)
                UPLOAD_FOLDER = dir

            # filename = secure_filename(file.filename)
            filename = file.filename
            file.save(os.path.join(dir, filename))
            resp = jsonify({'message': 'File successfully uploaded'})
            resp.status_code = 201
            return resp
        else:
            resp = jsonify(
                {'message': 'Allowed file types are txt, pdf, png, jpg, jpeg, gif'})
            resp.status_code = 400
            return resp
    except Exception as err:
        print('An exception occured!!')
        print(err)
        return make_response('Something went wrong!!', 500)

@app.route('/get/files', methods=['GET'])
@token_required
def get_user_files(currentuser):
    try:
        dir = os.path.join(os.path.dirname(__file__) + '/uploads/', currentuser.public_id)
        if os.path.isdir(dir) == False:
            print('No files found')
            resp = jsonify({'message': 'No files available for the user'})
            resp.status_code = 400
            return resp
        else:
            userFiles = [{ 'name': f, 'url': join('uploads', currentuser.public_id, f) } for f in listdir(dir) if isfile(join(dir, f))]
            resp = jsonify({ 'files': userFiles })
            resp.status_code = 201
            return resp
    except Exception as err:
        print('An exception occured!!')
        print(err)
        return make_response('Something went wrong!!', 500)

@app.route('/file/share/<path:userPublicId>/<path:filename>', methods=['GET'])
def create_file_post(userPublicId, filename):
    try:
        print(userPublicId)
        print(filename)
        dir_path = join(os.path.dirname(__file__), 'uploads', userPublicId)
        filePath = dir_path + '/{}'.format(filename)
        print(filePath)
        if os.path.isfile(filePath) == False:
            print('No files found')
            resp = jsonify({'message': 'File Not Found!!'})
            resp.status_code = 404
            return resp
        user = UserModel.query.filter_by(public_id=userPublicId).first()
        post = FilePost.query.filter_by(fileName=filename, user_id=user.id).first()
        print(post)
        if not user:
            resp = jsonify({'message': 'No user found with given publicId!'})
            resp.status_code = 404
            return resp
        if post:
            resp = jsonify({'message': 'File already shared!'})
            resp.status_code = 400
            return resp
        newPost = FilePost(fileName=filename, total_rating=0, user_id=user.id)
        db.session.add(newPost)
        db.session.commit()
        return jsonify({'message': 'file shared successfully', 'post': {'fileName': newPost.fileName,
        'tatalRating': newPost.total_rating, 'user_id': newPost.user_id, 'ratings': newPost.ratings}})
    except Exception as err:
        print('An exception occured!!')
        print(err)
        return make_response('Something went wrong!!', 500)

@app.route('/rating/create', methods=['POST'])
@token_required
def create_post_rating(currentuser):
    try:
        # data = json.load(request.data)
        data = json.loads(request.data)
        print(data)
        rating = data['rating']
        review = data['review']
        post_id = data['post_id']
        
        print(rating)
        print(review)
        print(post_id)
        if not rating or not post_id:
            resp = jsonify({'message': 'Post Id or Rating is not available!'})
            resp.status_code = 400
            return resp
        ratingObj = Rating.query.filter_by(post_id=post_id).all()
        postRating = {}
        for item in ratingObj:
            if item.user_id == currentuser.id:
                postRating = item
                break
        print(postRating)
        if postRating:
            resp = jsonify({'message': 'User already rated this post!'})
            resp.status_code = 400
            return resp
        post = FilePost.query.filter_by(id=post_id).first()
        postObj = post.serialize()
        total_rating = (
            postObj['total_rating']*len(postObj['all_ratings']) + rating)/(len(postObj['all_ratings'])+ 1)
        setattr(post, 'total_rating', total_rating)
        db.session.commit()
        newRating = Rating(review=review, rating=rating, user_id=currentuser.id, post_id=post_id)
        db.session.add(newRating)
        db.session.commit()
        return jsonify({'message': 'Rating saved successfully'})
    except Exception as err:
        print('An exception occured!!')
        print(err)
        return make_response('Something went wrong!!', 500)

@app.route('/get/posts', methods=['GET'])
@token_required
def get_file_post(currentuser):
    try:
        print(currentuser)
        posts = FilePost.query.filter_by().all()

        if not posts:
            print('posts not available!')
            resp = jsonify({'message': 'No posts available!'}) 
            resp.status_code = 404
            return resp
        
        all_posts = []

        for post in posts:
            post = post.serialize()
            # print(post)
            post['fileUrl'] = join('uploads', post['user_info']['public_id'], post['fileName'])
            all_posts.append(post)
        return jsonify({ 'allPosts': all_posts })
    except Exception as err:
        print('An exception occured!!')
        print(err)
        return make_response('Something went wrong!!', 500)

@app.route('/get/ratings/<path:postId>', methods=['GET'])
def get_file_post_ratings(postId):
    try:
        ratings = Rating.query.filter_by(post_id=postId).all()
        # posts = posts.to_dict()
        # users_posts = users_posts.to_dict()
        if not ratings:
            print('ratings not available!')
            resp = jsonify({'message': 'No ratings available!'})
            resp.status_code = 404
            return resp
        
        all_ratings = []

        for rating in ratings:
            rating = rating.serialize()
            print(rating)
            all_ratings.append(rating)
        return jsonify({'allRatings': all_ratings})
    except Exception as err:
        print('An exception occured!!')
        print(err)
        return make_response('Something went wrong!!', 500)

@app.route('/save-highlights', methods=['POST'])
@token_required
def save_user_highlights(currentuser):
    try:
        highlights = request.data
        highlights = json.loads(highlights)
        dir = os.path.join(os.path.dirname(__file__) + '/highlights/'+ currentuser.public_id)
        if os.path.isdir(dir) == False:
            print("doesnt exist")
            os.makedirs(dir, exist_ok=True)
        if not highlights:
            print('No Highlights found')
            resp = jsonify({'message': 'No Highlights sent in request!'})
            resp.status_code = 400
            return resp
        else:
            for fileHighlight in highlights:
                filepath = join(dir, fileHighlight['name'] + '.json')
                with open(filepath, 'w') as outfile:
                    json.dump(fileHighlight, outfile)
            resp = jsonify({ 'message': 'highlights saved successfully!' })
            resp.status_code = 201
            return resp
    except Exception as err:
        print('An exception occured!!')
        print(err)
        return make_response('Something went wrong!!', 500)

@app.route('/get-highlights', methods=['GET'])
@token_required
def get_user_highlights(currentuser):
    try:
        dir = os.path.join(os.path.dirname(__file__) + '/highlights/' + currentuser.public_id )
        if os.path.isdir(dir) == False:
            print("doesnt exist")
            os.makedirs(dir, exist_ok=True)
            resp = jsonify({'message': 'No highlights available for the user'})
            resp.status_code = 400
            return resp
        
        data = [json.load(open(join(dir, f))) for f in listdir(dir) if isfile(join(dir, f))]

        resp = jsonify({ 'highlights': data })
        resp.status_code = 200
        return resp
    except Exception as err:
        print('An exception occured!!')
        print(err)
        return make_response('Something went wrong!!', 500)


@app.route('/uploads/<path:userPublicId>/<path:filename>', methods=['GET'])
def get_user_pdf(userPublicId, filename):
    """ get pdf file """
    # retrieve body data from input JSON
    print(userPublicId)
    print(filename)
    dir_path = join(os.path.dirname(__file__), 'uploads', userPublicId)
    filePath = dir_path + '/{}'.format(filename)
    print(filePath)
    if os.path.isfile(filePath) == False:
        print('No files found')
        resp = jsonify({'message': 'File Not Found!!'})
        resp.status_code = 404
        return resp
    return send_file(filePath, attachment_filename=filename)

def get_top_cat(doc):
    """
    Function to identify the highest scoring category
    prediction generated by the text categoriser.
    """
    cats = doc.cats
    # doc.cats.pop('OTHER')
    max_score = max(cats.values())
    max_cats = [k for k, v in cats.items() if v == max_score]
    # max_cats = [v for v, k in cats.items() if k != 'OTHER' ]

    max_cat = max_cats[0]
    return (max_cat, max_score)

@app.route('/highlights-json/<path:userPublicId>/<path:filename>', methods=['GET'])
def get_user_pdf2(userPublicId, filename):
    """ get pdf file """
    # retrieve body data from input JSON
    print(userPublicId)
    print(filename)

    dir_path = join(os.path.dirname(__file__), 'uploads', userPublicId)
    filePath = dir_path + '/{}'.format(filename)
    print(filePath)

    if os.path.isfile(filePath) == False:
        print('No files found')
        resp = jsonify({'message': 'File Not Found!!'})
        resp.status_code = 404
        return resp

    dir = os.path.join(os.path.dirname(__file__) + '/highlights/' + userPublicId)
    if os.path.isdir(dir) == False:
        print("doesnt exist")
        os.makedirs(dir, exist_ok=True)
    filepath = join(dir, filename + '.json')
    
    isHighlightsAvailable = False
    data = {}
    if os.path.isfile(filepath):
        print("\nFile exists\n")
        with open(filepath, 'r') as json_file:
            data = json.load(json_file)
            if data['name'] == filename:
                isHighlightsAvailable = True
    
    if isHighlightsAvailable == True:
        print("Highlights already present for pdf: " + filename)
        response = app.response_class(
                    response=json.dumps({ "highlights": data }),
                    status=200,
                    mimetype='application/json',
                )
        return response

    rsrcmgr = PDFResourceManager()
    laparams = LAParams()
    device = PDFPageAggregator(rsrcmgr, laparams=laparams)
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    fp = open(filePath, 'rb')
    pages = PDFPage.get_pages(fp)
    check = "Disclosure"
    counter = 0
    id_counter = 0
    proccessed_data = {}

    pageSizesList = []
 
    for page in pages:
        counter += 1
        print('Processing ', counter, 'page...')
        # size=page.mediabox
        # print(size)
        interpreter.process_page(page)
        layout = device.get_result()
        for lobj in layout:
            if isinstance(lobj, LTTextBox):
                x1, y0_orig, x2, y1_orig, text = lobj.bbox[0], lobj.bbox[1], lobj.bbox[2], lobj.bbox[3], lobj.get_text(
                )
                y1 = page.mediabox[3] - y1_orig
                y2 = page.mediabox[3] - y0_orig

                


                text = text.strip()
                doc = nlp(text)

                sentences = [sent.string.strip() for sent in doc.sents]
                json_dump = []
                # for sentence in sentences:

                if len(text) > 43:
                    # doc2 = nlp(sentence)
                    # doc2.cats.pop('ISSUE')
                    # doc2.cats.pop('OTHER')
                    # doc2.cats=total(doc2.cats)
                    c = Counter(doc.cats)
                    most_common = c.most_common(1)  # returns top 3 pairs
                    # my_keys = [key for key, val in most_common]
                    # top_category = get_top_cat(doc2)
                    # result = re.findall(pattern, sentence, re.M|re.I)
                    id_counter += 1
                    jsont = {
                        "comment": {
                            "emoji":"",
                            "text": most_common[0][0],
                        },
                        "content": {
                            "text": text,
                        },
                        "id": str(id_counter),
                        "position": {
                            "boundingRect": {
                              
                                "x1": x1,
                                "y1": y1,
                                "x2": x2,
                                "y2": y2,
                                  "height":  page.mediabox[3],
                                "width":  page.mediabox[2]
                            },
                            "pageNumber": counter,
                            "rects": [
                                {
                         
                                    "x1": x1,
                                    "y1": y1,
                                    "x2": x2,
                                    "y2": y2,
                                               "height":  page.mediabox[3], # get height of each page
                                "width":  page.mediabox[2]# get width of each page
                                }
                            ]
                        }
                    }
                    arr = proccessed_data.setdefault(filename, [])
                    arr.append(jsont)
    if filename in proccessed_data:
        newFile = { "highlights": proccessed_data[filename], "name": filename }

    with open(filepath, 'w') as json_file:
        json.dump(newFile, json_file)
    
    response = app.response_class(
                    response=json.dumps({ "highlights": newFile }),
                    status=200,
                    mimetype='application/json',
                )
    return response


@app.route('/textanonymizer', methods=['POST'])
def text_anonymizer_post():
    # input data in json format
    input_json = request.json
    # parse json data
    d = input_json

    # anonymize text
    anonymized_text = text_anonymizer.anonymize(d['text'],
                                                name_types=d['entities'],
                                                fictional = d['fake_names'])
    
    # convert the output into a json file
    response = json.dumps(anonymized_text)

    # return the json file
    return response

@socketio.on('connect')
def test_connect():
    print('Connection is on!!')

    @socketio.on('get-document')
    def getDocumentId(documentId):
        try:
            dir = os.path.join(os.path.dirname(__file__) + '/notes')
            if os.path.isdir(dir) == False:
                os.makedirs(dir, exist_ok=True)
            filepath = dir + '/' + documentId + '.json'
            if os.path.isfile(filepath):
                print("\nFile exists\n")
                with open(filepath) as json_file:
                    data = json.load(json_file)
                    emit('load-document', data)
            else:
                print('\nFile does not exist\n')
                with open(filepath, 'w') as outfile:
                    json.dump({'data': {'ops': []}}, outfile)
                    emit('load-document', {'data': {'ops': []}})

            @socketio.on('send-changes')
            def sendChanges(delta):
                emit('receive-changes', delta, broadcast=True, include_self=False)

            @socketio.on('save-document')
            def saveData(data):
                with open(filepath, 'w') as outfile:
                    json.dump(data, outfile)

            @socketio.on('disconnect')
            def disconnect():
                print('disconnected!')
        except Exception as err:
            print('An exception occured!!')
            print(err)
            return 'Something went wrong!!'


if __name__ == "__main__":
    socketio.run(host='0.0.0.0', debug=True)
