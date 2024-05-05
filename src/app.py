from __future__ import absolute_import, division, print_function, unicode_literals
from time import time
from flask import g, Flask, request, jsonify, make_response, url_for, flash, send_file, abort
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename
from src.routes.pdf_api import bp_api
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.inspection import inspect
from flask_migrate import Migrate
from flask_socketio import SocketIO, emit
from engineio.payload import Payload
from flask_cors import CORS, cross_origin
from src.utils import check_password_and_generate_hash, check_password
from datetime import timedelta, datetime
import json
import os
from os import listdir
from os.path import isfile, join, dirname
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
import numpy as np
import re
from flask_cors import CORS, cross_origin
import argparse
import logging
from tqdm import trange
from src.textAnonymizer import text_anonymizer
import numpy as np
from dotenv import load_dotenv
from neo4j import GraphDatabase, basic_auth
import openai
from src.openai_funcs import * 
from src.entity_parse import *



dotenv_path = join(dirname(__file__), '..', '.env')
load_dotenv(dotenv_path)

# ## custom spacy models##
# output_dir = "./judgclsfymodel12"
# output_dir3 = "./cite_law_sm22"
# nlp = spacy.load(output_dir)
# nlp3 = spacy.load(output_dir3)

# output_dir2 = os.path.dirname(os.path.realpath(__file__)) + "/../cite_law_sm22"
# nlp3 = spacy.load(output_dir2)

## blackstone spacy models
nlp = spacy.load("en_blackstone_proto")



Payload.max_decode_packets = 50
ALLOWED_EXTENSIONS = ['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif']
app = Flask(__name__)
app.config['CORS_HEADERS'] = 'Content-Type'
cors = CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})

UPLOAD_FOLDER = os.path.join(f'{os.path.dirname(__file__)}/static/uploads')
app.config.from_pyfile('settings.py')
app.register_blueprint(bp_api, url_prefix="/api/v1/")
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# DATABASE_URL = os.environ.get('HIGHLIGHT_DATABASE_URL')
# DATABASE_USERNAME = os.environ.get('HIGHLIGHT_DATABASE_USERNAME')
# DATABASE_PASSWORD = os.environ.get('HIGHLIGHT_DATABASE_PASSWORD')
# driver = GraphDatabase.driver(uri=DATABASE_URL, auth=basic_auth(DATABASE_USERNAME, DATABASE_PASSWORD))

uri = "neo4j+s://051aed9a.databases.neo4j.io:7687"
username = "neo4j"
password = "1Ok-ILv1z4Ele9OLE8Hk9F9rDKuggp7Lr_IAjXZsvkk"

driver = GraphDatabase.driver(uri, auth=(username, password))



db = SQLAlchemy(app)

migrate = Migrate(app, db)
socketio = SocketIO(app, cors_allowed_origins="http://localhost:3000", ping_interval=2000, ping_timeout=30000)

citation_regex = r"((?:PLD|SCMR|CLC|PCrLJ|PTD|PLC|CLD|YLR|GBLR|AIR|AC|Q\.B|PCr\.LJ|MLD|P Cr\. L J|ER|KB|Lloyd’s Rep|SCC|F\.R\.D|F\.3d)\s\d{4}\s(?:[^\d]+)?\d{1,3}|\d{4}\s(?:PLD|SCMR|CLC|PCrLJ|PTD|PLC|CLD|YLR|GBLR|AIR|AC|Q\.B|PCr\.LJ|MLD|P Cr\. L J|ER|KB|Lloyd’s Rep|SCC|F\.R\.D|F\.3d)\s(?:[^\d]+)?\d{1,4})"

def get_db():
    if not hasattr(g, 'neo4j_db'):
        g.neo4j_db = driver.session()
        return g.neo4j_db


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'neo4j_db'):
        g.neo4j_db.close()


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
        print(request.data)
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


from werkzeug.datastructures import ImmutableMultiDict


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
        # file = request.files['file']
        # if file.filename == '':
        #     print('No filename selected')
        #     resp = jsonify({'message': 'No file selected for uploading'})
        #     resp.status_code = 400
        #     return resp
        files = request.files.getlist('file')
        # d = ImmutableMultiDict(files)
        # files = dict(d.lists())

        # print(request.files)
        print(files)
        # print(type(file))

        for file in files:
            if file and allowed_file(file.filename):
                dir = os.path.join(os.path.dirname(__file__) +'/static' + 
                                   '/uploads/', currentuser.public_id)
                # dir = os.path.join(os.path.dirname(__file__) +
                #                 '/uploads/', "123")
                if os.path.isdir(dir) == False:
                    print("doesnt exist")
                    os.makedirs(dir, exist_ok=True)
                    UPLOAD_FOLDER = dir

                # filename = secure_filename(file.filename)
                filename = file.filename
                file.save(os.path.join(dir, filename))
            else:
                resp = jsonify(
                    {'message': 'Allowed file types are txt, pdf, png, jpg, jpeg, gif'})
                resp.status_code = 400
                return resp
        resp = jsonify({'message': 'File successfully uploaded'})
        resp.status_code = 201
        return resp

    except Exception as err:
        print('An exception occured!!')
        print(err)
        return make_response('Something went wrong!!', 500)


@app.route('/get/files', methods=['GET'])
@token_required
def get_user_files(currentuser):
    try:
        dir = os.path.join(os.path.dirname(__file__)+'/static'  + '/uploads/', currentuser.public_id)
        if os.path.isdir(dir) == False:
            print('No files found')
            resp = jsonify({'message': 'No files available for the user'})
            resp.status_code = 400
            return resp
        else:
            userFiles = [{'name': f, 'url': join('static','uploads', currentuser.public_id, f)} for f in listdir(dir) if
                         isfile(join(dir, f))]
            resp = jsonify({'files': userFiles})
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
        dir_path = join(os.path.dirname(__file__),'static', 'uploads', userPublicId)
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
                                                                        'tatalRating': newPost.total_rating,
                                                                        'user_id': newPost.user_id,
                                                                        'ratings': newPost.ratings}})
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
                               postObj['total_rating'] * len(postObj['all_ratings']) + rating) / (
                               len(postObj['all_ratings']) + 1)
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
        return jsonify({'allPosts': all_posts})
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
        dir = os.path.join(os.path.dirname(__file__) +'/static'  + '/highlights/' + currentuser.public_id)
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
            resp = jsonify({'message': 'highlights saved successfully!'})
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
        dir = os.path.join(os.path.dirname(__file__)+'/static'  + '/highlights/' + currentuser.public_id)
        if os.path.isdir(dir) == False:
            print("doesnt exist")
            os.makedirs(dir, exist_ok=True)
            resp = jsonify({'message': 'No highlights available for the user'})
            resp.status_code = 400
            return resp

        data = [json.load(open(join(dir, f))) for f in listdir(dir) if isfile(join(dir, f))]

        resp = jsonify({'highlights': data})
        resp.status_code = 200
        return resp
    except Exception as err:
        print('An exception occured!!')
        print(err)
        return make_response('Something went wrong!!', 500)


@app.route('/get-graphdata', methods=['GET'])
@token_required
def get_user_graphdata(currentuser):
    try:
        dir = os.path.join(os.path.dirname(__file__)+'/static' + '/graphData/' + currentuser.public_id)
        if os.path.isdir(dir) == False:
            print("doesnt exist")
            os.makedirs(dir, exist_ok=True)
            resp = jsonify({'message': 'No graphdata available for the user'})
            resp.status_code = 400
            return resp

        data = [json.load(open(join(dir, f))) for f in listdir(dir) if isfile(join(dir, f))]

        resp = jsonify({'graphdata': data})
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
    dir_path = join(os.path.dirname(__file__), 'static','uploads', userPublicId)
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



def textSegmentation(string):
    indices = []
    start_index = 0
    lst = re.finditer("\n[0-9.]+|\n\([0-9]+\)|^[0-9]+", string)
    for itr in lst:
        indices.append(itr.start(0))
    parts = [string[i:j] for i, j in zip(indices, indices[1:] + [None])]
    for part in parts:
        print(part)


# get relationships for each node
@app.route('/get/relationships/<path:node>', methods=['POST'])
def get_relationships(node):
    nodes = ['source', 'citation']
    if not node in nodes:
        return "Invalid Node", 400

    citation_filter = "CITED" if node=="source" else "CITED_BY"
    
    data = json.loads(request.data)
    query = data['query']
    cypher_query = '''MATCH p=({'''+node+": '"+query+"'"+ "})-[r:" +citation_filter+"]->() RETURN p LIMIT 250"
    print(cypher_query)
    db = get_db()
    results = db.read_transaction(
        lambda tx: tx.run(cypher_query).data())
    response = jsonify(results)
    response.status_code = 200
    return response

def has_forbidden_label(entities, forbidden_labels=['OTHER', 'ISSUE']):
    return any(label in forbidden_labels for  label in entities)


instruction_for_entities=instruction=""" as a legal copilot, please extract the following and provide them in seperate lists ; 
# CITATIONs, JUDGEs, CASENAMEs,COURTs,LEGAL PROVISIONs"""

my_labels = ["CITATION", "CASENAME", "PROVISION", "JUDGE", "COURT","INSTRUMENT"]


@app.route('/highlights-json/<path:userPublicId>/<path:filename>', methods=['GET'])
def get_user_pdf2(userPublicId, filename):
    ## get pdf file ##
    # retrieve body data from input JSON
    print(userPublicId)
    print(filename)

    dir_path = join(os.path.dirname(__file__),'static', 'uploads', userPublicId)
    filePath = dir_path + '/{}'.format(filename)
    print(filePath)

    if os.path.isfile(filePath) == False:
        print('No files found')
        resp = jsonify({'message': 'File Not Found!!'})
        resp.status_code = 404
        return resp

    dir = os.path.join(os.path.dirname(__file__) +'/static'+ '/highlights/' + userPublicId)
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
            response=json.dumps({"highlights": data}),
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
    provision_entities = []
    labels = []
    memory = 0  # memorize how many occurance it has seen.
    prev_text = ""
    current_text = ""
    pageSizesList = []

    entities = []
    labels = []
    full_text = ""

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
                # textSegmentation(text)
                # Append extracted text to the full_text variable
                full_text += text + "\n"  # Adding a newline for readability

                ## custom models split for NER and cat
                # doc = nlp(text)
                # doc3 = nlp3(text)
                # ents = [(ent.text, ent.label_) for ent in doc.ents]
                ## blackstone models 
                doc = nlp(text)
                ##added conditional for making sure just my_labels are parsed from blackstone model
                ents = [(ent.text, ent.label_) for ent in doc.ents if ent.label_ in my_labels]
                # testing output of classifier core_law_md5
                # print(ents)
                ## added conditional for parsing my_labels only
                for ent in doc.ents:
                    if ent.label_ in my_labels:
                        entities.append(str(ent.text))
                        labels.append(str(ent.label_))

                sentences = [sent.string.strip() for sent in doc.sents]
                json_dump = []
                ## added sentence parsing categorisation via blackstone 
                for sentence in sentences:
                    doc = nlp(sentence)
                    doc.cats.pop('UNCAT')

                    top_category = get_top_cat(doc)
                    print (f"\"{sentence}\" {top_category}\n")
                    most_common=top_category
                if len(text) > 50:
                    # doc2 = nlp(sentence)
                    # doc2.cats.pop('OTHER')
                    # doc2.cats=total(doc2.cats)
                    # doc.cats={k: v for k, v in doc.cats.items() if v < 1 and v > 0.73} #FILTERS DOC CATEGORIES BUT FRONTE WONT PRINT 

                    # c = Counter(doc.cats)
                    # most_common = c.most_common(1)  # returns top 3 pairs
                    # if most_common[0][0]=='CONCLUSION':
                    #     most_common[0][0]=='OPINION'
                    # my_keys = [key for key, val in most_common]
                    # top_category = get_top_cat(doc2)
                    # result = re.findall(pattern, sentence, re.M|re.I)
                    id_counter += 1
                    jsont = {
                        "comment": {
                            "emoji": "",
                            # "text": most_common[0][0],
                            "text": most_common[0],

                            "classifier_score": 0
                        },
                        "content": {
                            "text": text,
                            "entities": ents,
                        },
                        "id": str(id_counter),
                        "position": {
                            "boundingRect": {

                                "x1": x1,
                                "y1": y1,
                                "x2": x2,
                                "y2": y2,
                                "height": page.mediabox[3],
                                "width": page.mediabox[2]
                            },
                            "pageNumber": counter,
                            "rects": [
                                {

                                    "x1": x1,
                                    "y1": y1,
                                    "x2": x2,
                                    "y2": y2,
                                    "height": page.mediabox[3],  # get height of each page
                                    "width": page.mediabox[2]  # get width of each page

                                }
                            ]
                        }
                    }
                    arr = proccessed_data.setdefault(filename, [])
                    current_text = jsont["comment"]["text"]
                    if prev_text == current_text:
                        memory += 1
                    elif prev_text != current_text:
                        memory = 0  # increment memory
              
                    jsont["comment"]["classifier_score"] = (memory)
                    prev_text = current_text
                    current_text = ""
                  # Filtering based directly on comment["text"] containing 'OTHER' or 'ISSUE'
                    forbidden_texts = ['UNCAT']
                    if jsont["comment"]["classifier_score"] >= 1 and not any(forbidden_text in jsont["comment"]["text"] for forbidden_text in forbidden_texts):
                #         arr.append(jsont)
                        arr.append(jsont)

    newFile = {}
    graphData = {}
    graphDir = os.path.join(os.path.dirname(__file__) + '/static'+ '/graphData/' + userPublicId)
    if os.path.isdir(graphDir) == False:
        print("doesnt exist")
        os.makedirs(graphDir, exist_ok=True)
    if filename in proccessed_data:
        newFile = {"highlights": proccessed_data[filename], "name": filename, "entities": entities}
        print('THE NO. OF LABELS IN THIS PDF', len(labels))
        print('THE NO. OF ENTITIES IN THIS PDF', len(entities))
        print('entities before graph call',entities)
        print('labels before graph call',labels)
        print('type entities',type(entities))
        print('type labels',type(labels))

        filenamelist = [filename, filename, filename, filename, filename,filename]
        nodes = [{"id": x} for x in (entities + my_labels)]
        nodes2 = [{"id": filename}]
        nodes = (nodes + nodes2)
        centerlabel = [{"source": filenamelist, "target": my_labels} for filenamelist, my_labels in
                       zip(filenamelist, my_labels)]
        # print(centerlabel)
        labels = [{"source": label, "target": target} for label, target in zip(labels, entities)]
        labels = (labels + centerlabel)
        print(type(entities))
        # print(nodes)
        # print(labels)
        graphData = {
            "fileName": filename,
            "nodes": nodes,
            "links": labels
        }
    with open(join(graphDir, filename + '.json'), 'w') as graph_file:
        json.dump(graphData, graph_file)

    with open(filepath, 'w') as json_file:
        json.dump(newFile, json_file)
    response = app.response_class(
        response=json.dumps({"highlights": newFile}),
        status=200,
        mimetype='application/json',
    )
    notesDir = os.path.join(os.path.dirname(__file__),'static', 'notes', userPublicId)
    if not os.path.isdir(notesDir):
        os.makedirs(notesDir, exist_ok=True)
    notesFilePath = os.path.join(notesDir, filename + '.json')

    # Save the full_text into a JSON file
    with open(notesFilePath, 'w') as notes_file:
        json.dump({"text_body": full_text}, notes_file)
    print('done processing file')
    return response

@socketio.on('openai_appeal_call')
def handle_openai_call(data):
    ## this is the appeal call ##
    print("Received appeal openai_call with data:", data)
    documentId = data['documentId']
    filename = data['filename']
    request_count = data['requestCount']
    
    if filename in filename_to_responses:
        responses = filename_to_responses[filename]
        counter = min(request_count, 3) - 1
        response = responses["insights"][counter]
    else:
        # If filename not found, handle misc_call to retrieve the response
        dir_path = os.path.join(os.path.dirname(__file__),'static', 'notes', documentId)
        if not os.path.isdir(dir_path):
            os.makedirs(dir_path, exist_ok=True)
        if not os.path.isdir(dir_path):
            os.makedirs(dir_path, exist_ok=True)
        filepath = os.path.join(dir_path, f'{documentId}.json')
        if filename:
            filepath = os.path.join(dir_path, f'{filename}.json')
            if os.path.isfile(filepath):
                    print("\nFile exists\n")
                    with open(filepath) as json_file:
                        data = json.load(json_file)
                        # print('data json',data)
                        full_text= data['text_body']
                        instruction_for_insights='please provide me an appeal draft for this judgement:-'
                        response = get_rec(instruction_for_insights,full_text)

 
    print('openai response',response)
    emit('openai_response', {'message': response})



@socketio.on('openai-query')
def handle_openai_call_query(data):
    ## this is the appeal call ##
    print("Received openai-query with data:", data)
    print(type(data))
    # data = json.loads(data)
    # print(type(data))
    documentId = data['documentId']
    fileName = data['filename']
    query=data['query']
    content=data['content']
    dir_path = os.path.join(os.path.dirname(__file__), 'static','notes', documentId)
    if not os.path.isdir(dir_path):
        os.makedirs(dir_path, exist_ok=True)
    if not os.path.isdir(dir_path):
        os.makedirs(dir_path, exist_ok=True)
    
    filepath = os.path.join(dir_path, f'{documentId}.json')
    if fileName:
        filepath = os.path.join(dir_path, f'{fileName}.json')
        if os.path.isfile(filepath):
                print("\nFile exists\n")
                with open(filepath) as json_file:
                    data = json.load(json_file)
                    # print('data json',data)
                    full_text= data['text_body']
                    response=get_query_response(query,full_text,content)

    # print('openai-query-response',response)
    emit('openai-query-response', {'recommendation': response})

filename_to_responses = {
    "Crane-K-25.01.24.pdf": {
        "insights": ["1. The Importance of Reliable Evidence and the Impact of its Unreliability on Convictions The case highlights the pivotal role of reliable evidence in securing convictions. The Post Office's Horizon system's unreliability, which led to wrongful convictions of several sub-postmasters, underscores the necessity of scrutinizing the evidence's integrity. For future appeals, this insight stresses the need to thoroughly investigate and challenge the reliability of the evidence presented at trial. If the evidence is found unreliable, it may form a strong basis for appealing against wrongful convictions.","2. Duty of Disclosure and Its Violation Constituting an Abuse of Process The judgment emphasizes the prosecution's duty to disclose all material evidence, including that which could undermine its case or support the defendant's case. Failure to disclose such evidence, as seen with the non-disclosure of issues related to the Horizon system, constitutes an abuse of process. This insight is crucial for legal professionals preparing for an appeal, as identifying instances where the duty of disclosure was not met could lead to convictions being overturned. This duty extends to ensuring that all evidence that could affect the outcome of the case, including potential flaws in the evidence's reliability, is shared with the defense.","3. The Potential for Appeals Based on New Evidence or Arguments The successful appeal in this case, based on the unreliability of the Horizon system evidence, showcases the appellate courts' openness to reconsidering convictions when new evidence or arguments emerge. This suggests a wider implication for similar cases where technology or specific evidence types were instrumental in securing convictions. Legal professionals should be encouraged to seek out new evidence or reevaluate the evidence used in the original trial that may not have been properly scrutinized or disclosed. Additionally, this insight highlights the importance of remaining vigilant about advances in technology and forensic methodologies that could cast doubt on the reliability of evidence used in past convictions."],
        "caselaw": ["1. R v Post Office Ltd (No 1) [2020] EWCA Crim 577 Summary: This case is pivotal in the context of the Post Office Horizon scandal. It involved the quashing of multiple convictions of sub-postmasters due to the unreliability of the Horizon system. The Court of Appeal held that the prosecutions were an abuse of process because the Post Office, acting as the prosecutor, failed to disclose evidence about the unreliability of the Horizon system, which could have affected the outcome of the trials.","2. R v Turnbull [1977] QB 224 Summary: Although not directly related to abuse of process, Turnbull is critical for cases relying on questionable evidence, especially identification. The guidelines set out in Turnbull, emphasizing the need for caution before convicting based on weak or unreliable evidence, could be analogously applied to cases involving technological or forensic evidence, arguing for rigorous scrutiny of such evidence's reliability.","3. R v Sang [1980] AC 402 Summary: This case discusses the admissibility of evidence and the discretion of the trial judge to exclude evidence that would have an adverse effect on the fairness of the trial. While it primarily deals with entrapment and evidence obtained in breach of the law, the principles regarding the judge's discretion to ensure a fair trial can extend to cases where convictions are based on unreliable or flawed evidence."],
        "clauses": ["Clause 1: Challenge Based on the Unreliability of Evidence :- Whereas the integrity and reliability of evidence used to secure a conviction are paramount to the fairness of the trial, it shall be grounds for appeal if it can be demonstrated that the conviction was significantly based on evidence later found to be unreliable. This is particularly pertinent in cases where the evidence in question was instrumental in the original conviction, analogous to the demonstrated unreliability of the Horizon system in the referenced judgment.","Clause 2: Duty of Disclosure and Abuse of Process :- Given the prosecutorial duty to disclose all material evidence, including that which might undermine the prosecution's case or support the defendant's case, failure to fulfil this duty shall constitute an abuse of process. An appeal may be sought if it can be proven that such a failure has occurred, affecting the fairness of the trial and the integrity of the conviction, as evidenced by the prosecutorial behavior in the referenced judgment.","Clause 3: Appeal Based on New Evidence or Arguments :- An appeal may be lodged on the basis of new evidence or arguments that come to light post-conviction, which could materially affect the outcome of the original trial. This clause is applicable in scenarios where the new evidence or arguments challenge the reliability of the evidence used in the conviction or highlight prosecutorial misconduct, including but not limited to failure in the duty of disclosure."],
        "appeal":[""" [Your Firm's Letterhead]

        [Date]

        Registrar of the Court of Appeal Criminal Division
        Royal Courts of Justice
        The Strand
        London
        WC2A 2LL

        Dear Registrar,

        Re: Appeal against Conviction of Kathleen Crane - Case No: 2024/00172/B3

        I am writing to formally appeal against the conviction of Mrs. Kathleen Crane in the case referenced above. The judgment handed down on Thursday, 25th January 2024, by Lord Justice Holroyde, Mr. Justice Picken, and Mrs. Justice Farbey, outlines compelling reasons why Mrs. Crane's conviction should be deemed unsafe and subsequently quashed.

        The judgment details the crucial aspect that this is indeed a Horizon case, where the reliability of Horizon data was fundamental to the prosecution. It is evident that there was a lack of independent evidence to substantiate the alleged loss associated with Mrs. Crane's actions. Furthermore, it is established that the prosecution failed to fulfill its duty of investigation and disclosure regarding the reliability of the Horizon system, which undermines the integrity of the conviction.

        In light of the circumstances presented in the judgment, it is clear that Mrs. Crane's conviction was an abuse of the process on multiple grounds. Her plea of guilty was made in the absence of essential information that would have significantly impacted the case against her. As such, I respectfully request an extension of time to apply for leave to appeal and urge the Court to grant leave to appeal and subsequently quash Mrs. Crane's conviction.

        Please let me know if there are any additional requirements or procedures to follow in this appeal process. I am committed to pursuing justice on behalf of Mrs. Kathleen Crane and ensuring that her rights are upheld in this matter.

        Thank you for your attention to this important issue.

        Yours sincerely,

        [Your Name]
        [Your Position]
        [Your Contact Information]"""],
    
    },
    "example_file2": {
        "caselaw": ["caselaw_response_1", "caselaw_response_2", "caselaw_response_3"],
        "insights": ["insights_response_1", "insights_response_2", "insights_response_3"],
        "clauses": ["clause_response_1", "clause_response_2", "clause_response_3"]
    },
}


@socketio.on('openai-get-recommendation')
def handle_openai_call_rec(data):
    documentId = data['documentId']
    filename = data['filename']
    request_count = data['requestCount']
    
    if filename in filename_to_responses:
        responses = filename_to_responses[filename]
        counter = min(request_count, 3) - 1
        response = responses["insights"][counter]
    else:
        # If filename not found, handle misc_call to retrieve the response
        dir_path = os.path.join(os.path.dirname(__file__),'static', 'notes', documentId)
        if not os.path.isdir(dir_path):
            os.makedirs(dir_path, exist_ok=True)
        if not os.path.isdir(dir_path):
            os.makedirs(dir_path, exist_ok=True)
        filepath = os.path.join(dir_path, f'{documentId}.json')
        if filename:
            filepath = os.path.join(dir_path, f'{filename}.json')
            if os.path.isfile(filepath):
                    print("\nFile exists\n")
                    with open(filepath) as json_file:
                        data = json.load(json_file)
                        # print('data json',data)
                        full_text= data['text_body']
                        # print('full_text',full_text)
                        instruction_for_insights='please provide me 5 relevant uk law insights after reading this recent judgement that can help challenge and prepare for an appeal '
                        response = get_rec(instruction_for_insights,full_text)

    emit('openai-recommendations', {'recommendation': response})



@socketio.on('openai-get-caselaw')
def handle_openai_caselaw_call(data):
    documentId = data['documentId']
    filename = data['filename']
    request_count = data['requestCount']
    
    if filename in filename_to_responses:
        responses = filename_to_responses[filename]
        counter = min(request_count, 3) - 1
        response = responses["caselaw"][counter]
    else:
        # If filename not found, handle misc_call to retrieve the response
        dir_path = os.path.join(os.path.dirname(__file__),'static', 'notes', documentId)
        if not os.path.isdir(dir_path):
            os.makedirs(dir_path, exist_ok=True)
        if not os.path.isdir(dir_path):
            os.makedirs(dir_path, exist_ok=True)
        filepath = os.path.join(dir_path, f'{documentId}.json')
        if filename:
            filepath = os.path.join(dir_path, f'{filename}.json')
            if os.path.isfile(filepath):
                    print("\nFile exists\n")
                    with open(filepath) as json_file:
                        data = json.load(json_file)
                        # print('data json',data)
                        full_text= data['text_body']
                        # print('full_text',full_text)
                        instruction_for_insights='please provide me 3 relevant uk caselaw after reading this recent judgement that can help challenge and prepare for an appeal '
                        response = get_rec(instruction_for_insights,full_text)

    # print('openai-caselaw',response)
    emit('openai-caselaw', {'recommendation': response})


@socketio.on('openai-get-clause')
def handle_openai_clause_call(data):
    documentId = data['documentId']
    filename = data['filename']
    request_count = data['requestCount']
    
    if filename in filename_to_responses:
        responses = filename_to_responses[filename]
        counter = min(request_count, 3) - 1
        response = responses["caselaw"][counter]
    else:
        # If filename not found, handle misc_call to retrieve the response
        dir_path = os.path.join(os.path.dirname(__file__),'static', 'notes', documentId)
        if not os.path.isdir(dir_path):
            os.makedirs(dir_path, exist_ok=True)
        if not os.path.isdir(dir_path):
            os.makedirs(dir_path, exist_ok=True)
        filepath = os.path.join(dir_path, f'{documentId}.json')
        if filename:
            filepath = os.path.join(dir_path, f'{filename}.json')
            if os.path.isfile(filepath):
                    print("\nFile exists\n")
                    with open(filepath) as json_file:
                        data = json.load(json_file)
                        # print('data json',data)
                        full_text= data['text_body']
                        # print('full_text',full_text)
                        instruction_for_insights='please provide me 3 relevant uk caselaw after reading this recent judgement that can help challenge and prepare for an appeal '
                        response = get_rec(instruction_for_insights,full_text)
        
    # print('openai-clause',response)
    emit('openai-clause', {'recommendation': response})


@socketio.on('connect')
def test_connect():
    print('Connection is on!!')

  

    @socketio.on('get-document')
    def getDocumentId(info):
        try:
            # Check if info is already a dictionary
            if not isinstance(info, dict):
                info = json.loads(info)  # Only parse if it's not already a dictionary
            
            documentId = info['documentId']
            fileName = info['fileName']
            print(info)
            
            dir_path = os.path.join(os.path.dirname(__file__),'static', 'notes', documentId)
            if not os.path.isdir(dir_path):
                os.makedirs(dir_path, exist_ok=True)
            
            filepath = os.path.join(dir_path, f'{documentId}.json')
            if fileName:
                filepath = os.path.join(dir_path, f'{fileName}.json')
            
            if os.path.isfile(filepath):
                print("\nFile exists\n")
                with open(filepath) as json_file:
                    data = json.load(json_file)
                    emit('document-loaded', data)
                    print('data',data)

            else:
                print('\nFile does not exist\n')
                with open(filepath, 'w') as outfile:
                    json.dump({'data': {'ops': []}}, outfile)
                    emit('document-loaded', {'data': {'ops': []}})
            @socketio.on('send-changes')
            def sendChanges(delta):
                emit('receive-changes', delta, broadcast=True, include_self=False)

            @socketio.on('save-document')
            def saveData(data):
                if os.path.isfile(filepath):
                    with open(filepath, 'r') as json_file:
                        existing_data = json.load(json_file)
                else:
                    existing_data = {}

                # Update 'existing_data' with the new content under 'new_text_body'
                # This keeps the original 'text_body' intact and adds the new data
                existing_data['new_text_body'] = data  # Or use data['ops'] if you need to store the ops array directly

                # Write the updated data back to the file
                with open(filepath, 'w') as json_file:
                    json.dump(existing_data, json_file)

            @socketio.on('disconnect')
            def disconnect():
                print('disconnected!')
        except Exception as err:
            print('An exception occured!!')
            print(err)
            return 'Something went wrong!!'



def interact_model(    
    model_name='contracts_model',
    seed=None,
    nsamples=3,
    batch_size=3,
    length=25,
    temperature=0.79,
    top_k=0,
    top_p=1,
    models_dir='./src/gptmodules/',
    input_text=None
):
    """
    Interactively run the model
    :model_name=124M : String, which model to use
    :seed=None : Integer seed for random number generators, fix seed to reproduce
     results
    :nsamples=1 : Number of samples to return total
    :batch_size=1 : Number of batches (only affects speed/memory).  Must divide nsamples.
    :length=None : Number of tokens in generated text, if None (default), is
     determined by model hyperparameters
    :temperature=1 : Float value controlling randomness in boltzmann
     distribution. Lower temperature results in less random completions. As the
     temperature approaches zero, the model will become deterministic and
     repetitive. Higher temperature results in more random completions.
    :top_k=0 : Integer value controlling diversity. 1 means only 1 word is
     considered for each step (token), resulting in deterministic completions,
     while 40 means 40 words are considered at each step. 0 (default) is a
     special setting meaning no restrictions. 40 generally is a good value.
     :models_dir : path to parent folder containing model subfolders
     (i.e. contains the <model_name> folder)
    """
    
    
    models_dir = os.path.expanduser(os.path.expandvars(models_dir))
    if batch_size is None:
        batch_size = 1
    assert nsamples % batch_size == 0

    enc = encoder.get_encoder(model_name, models_dir)
    hparams = model.default_hparams()
    with open(os.path.join(models_dir, model_name, 'hparams.json')) as f:
        hparams.override_from_dict(json.load(f))

    if length is None:
        length = hparams.n_ctx // 2
    elif length > hparams.n_ctx:
        raise ValueError("Can't get samples longer than window size: %s" % hparams.n_ctx)

    with tf.Session(graph=tf.Graph()) as sess:
        context = tf.placeholder(tf.int32, [batch_size, None])
        np.random.seed(seed)
        tf.set_random_seed(seed)
        output = sample.sample_sequence(
            hparams=hparams, length=length,
            context=context,
            batch_size=batch_size,
            temperature=temperature, top_k=top_k, top_p=top_p
        )

        saver = tf.train.Saver()
        ckpt = tf.train.latest_checkpoint(os.path.join(models_dir, model_name))
        saver.restore(sess, ckpt)
        result_dic={}
        result_text=[]
        sample_no=[]
        raw_text = input_text
        context_tokens = enc.encode(raw_text)
        generated = 0
        for _ in range(nsamples // batch_size):
           out = sess.run(output, feed_dict={
           context: [context_tokens for _ in range(batch_size)]
           })[:, len(context_tokens):]
        for i in range(batch_size):
           generated += 1
           text = enc.decode(out[i])

           print("=" * 40 + " SAMPLE " + str(generated) + " " + "=" * 40)
        #    fullsample = ("=" * 40 + " SAMPLE " + str(generated) + " " + "=" * 40)

           print(text)
       
           result_text.append(text)
           sample_no.append("SAMPLE"+ str (generated))
        #    result_dic= {k:v for k,v in zip (sample_no,result_text)}
        #    result_dic= {
            #    "text": result_text,
        #    }

        print(result_text)
        print("=" * 80)

        return result_text


@app.route("/generate", methods=['GET', 'POST'])
@token_required
def get_gen(user=None):
    data = request.get_json()

    if 'text' not in data or len(data['text']) == 0 :
        abort(400)
    else:
        text = data['text']
        # model = data['model']

        result = interact_model(
            # model_type='gpt2',
            length=100,
            input_text=text,
            # model_name_or_path=model
        )

        return jsonify({'result': result})


# if __name__ == "__main__":
#     socketio.run(host='0.0.0.0', debug=True)
    
if __name__ == '__main__':
    socketio.run(app, async_mode='gevent', host='0.0.0.0', port=5000)
