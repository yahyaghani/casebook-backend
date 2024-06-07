from __future__ import absolute_import, division, print_function, unicode_literals
import json
import os
from os import listdir
from os.path import isfile, join, dirname
from time import time
from flask import g, Flask, request, jsonify, make_response, url_for, flash, send_file, abort
from werkzeug.security import check_password_hash
from werkzeug.datastructures import ImmutableMultiDict
from werkzeug.utils import secure_filename
from src.routes.pdf_api import bp_api
from flask_migrate import Migrate
from engineio.payload import Payload
from flask_cors import CORS, cross_origin
from flask import session

from datetime import timedelta, datetime
import pandas as pd
import numpy as np
import re
import uuid
import jwt
from functools import wraps
import spacy

from dotenv import load_dotenv
from neo4j import GraphDatabase, basic_auth
from pdfminer.layout import LAParams, LTTextBox
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator

from src.db.main_model import *
from src.openai_funcs import * 
from src.entity_parse import *
from src.core.prompts.search_prompt import search_sample
from src.core.agents.open_agent import process_user_instruction
from src.textAnonymizer import text_anonymizer
from src.utils import check_password_and_generate_hash, check_password
from src.socketio_instance import socketio_instance  # Import from the new module
from src.core.multi_mode.video_pipe import *

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
# ALLOWED_EXTENSIONS = ['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif']
ALLOWED_EXTENSIONS = {
    'pdf': 'pdf', 'docx': 'docx', 'mp4': 'mp4', 'avi': 'avi', 'mov': 'mov',
    'jpg': 'jpg', 'jpeg': 'jpeg', 'aac': 'aac', 'wav': 'wav', 'png': 'png','txt': 'txt'
}


app = Flask(__name__)
app.config['CORS_HEADERS'] = 'Content-Type'
cors = CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})

UPLOAD_FOLDER = os.path.join(f'{os.path.dirname(__file__)}/static/uploads')
STATIC_FOLDER = os.path.join(f'{os.path.dirname(__file__)}/static')

app.config.from_pyfile('settings.py')
app.register_blueprint(bp_api, url_prefix="/api/v1/")
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['STATIC_FOLDER'] = STATIC_FOLDER
# socketio_instance = SocketIO(app, cors_allowed_origins="http://localhost:3000", ping_interval=2000, ping_timeout=30000)
socketio_instance.init_app(app)
emit=socketio_instance.emit


# db = SQLAlchemy(app)

# migrate = Migrate(app, db)
# init_db(app)

init_db(app)  # Initialize the database with the app
setup_database(app)  # Now it's safe to setup the database

citation_regex = r"((?:PLD|SCMR|CLC|PCrLJ|PTD|PLC|CLD|YLR|GBLR|AIR|AC|Q\.B|PCr\.LJ|MLD|P Cr\. L J|ER|KB|Lloyd’s Rep|SCC|F\.R\.D|F\.3d)\s\d{4}\s(?:[^\d]+)?\d{1,3}|\d{4}\s(?:PLD|SCMR|CLC|PCrLJ|PTD|PLC|CLD|YLR|GBLR|AIR|AC|Q\.B|PCr\.LJ|MLD|P Cr\. L J|ER|KB|Lloyd’s Rep|SCC|F\.R\.D|F\.3d)\s(?:[^\d]+)?\d{1,4})"

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'neo4j_db'):
        g.neo4j_db.close()


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
            ) + timedelta(hours=24)}, app.config['SECRET_KEY'])

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


@app.route('/user/<int:user_id>/cases', methods=['GET'])
@token_required
def get_user_cases(currentuser):
    # if currentuser.id != user_id:
    #     return jsonify({'message': 'Unauthorized access'}), 403
    
    cases = Caselog.query.filter_by(user_id=currentuser.id).all()
    case_list = [{'id': case.id, 'description': case.case_description} for case in cases]

    return jsonify(case_list), 200


@app.route('/upload/multiple-files', methods=['POST'])
@token_required
def upload_multiple_files(currentuser):
    try:
        print("Retrieving case name from form data...")
        case_name = request.form.get('case_name')  # Retrieve case_name from form data
        print(f"Case name received: {case_name}")

        case_id = None
        if case_name:
            print("Checking for existing case in the database...")
            existing_case = Caselog.query.filter_by(case_description=case_name, user_id=currentuser.id).first()
            if not existing_case:
                print("No existing case found, creating a new case...")
                new_case = Caselog(case_description=case_name, user_id=currentuser.id)
                db.session.add(new_case)
                db.session.commit()
                case_id = new_case.id
                print(f"New case created with ID: {case_id}")
            else:
                case_id = existing_case.id
                print(f"Existing case found with ID: {case_id}")

        print("Checking if files are included in the request...")
        if 'files' not in request.files:
            print("No file part in the request")
            return jsonify({'message': 'No file part in the request'}), 400

        files = request.files.getlist('files')
        if not files:
            print("No files selected for uploading")
            return jsonify({'message': 'No files selected for uploading'}), 400

        print(f"Creating upload directory for user {currentuser.public_id}...")
        upload_dir = os.path.join(os.path.dirname(__file__), 'static/uploads/', currentuser.public_id)
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir, exist_ok=True)
            print(f"Upload directory created at {upload_dir}")

        uploaded_files = []
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(upload_dir, filename)
                print(f"Saving file: {filename} to {file_path}")
                file.save(file_path)
                file_extension = os.path.splitext(filename)[1].lower()
                print(f"Processing file {filename} with extension {file_extension}")
                summary = file_handler(file_path, file_extension, currentuser.public_id, filename, case_id)
                short_sum = summary[:200] if summary else "No summary available"
                uploaded_files.append({
                    'name': filename,
                    'category': 'Determined by file type',
                    'summary': short_sum,
                    'type': file_extension
                })
                print(f"File {filename} processed and added to the response")
            else:
                print(f"File {file.filename} is not an allowed file type")
                return jsonify({'message': f'Allowed file types are {", ".join(ALLOWED_EXTENSIONS)}'}), 400
        
        print("All files successfully uploaded")
        return jsonify({'message': 'Files successfully uploaded', 'files': uploaded_files}), 201

    except Exception as err:
        print('An exception occurred!!')
        print(err)
        return make_response('Something went wrong!!', 500)


# def file_handler(file_path, file_type,public_id,file_name):
    
#     if file_type in ['.mp4']:
#         frames, audio_path = process_video(file_path)
#         video_summary = generate_video_summary(frames)
#         if audio_path:
#             text = transcribe_audio(file_path)
#             video_summary=text+'\n\n'+video_summary
        
#         return video_summary
    
#     elif file_type in ['.mp3', '.wav']:
#         text = transcribe_audio(file_path)
#         return text
#     elif file_type in ['.jpg', '.png']:
#         base64_image = encode_image(file_path)
#         return base64_image
#     elif file_type in ['.pdf']:
#         text =get_user_pdf2(public_id, file_name,inbound=True)
#         return text
#     elif file_type in ['.txt']:
#         text = process_text_file(file_path)
#         return text
#     else:
#         return "Unsupported file type."



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
        #### total rating has been removed from schema ###
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


sample_accordion_data={
    "sections": [
      {
        "clause": "Section 1",
        "text": "This is the content of section 1."
      },
      {
        "clause": "Section 2",
        "text": "This is the content of section 2."
      }
    ]
  }
  

@app.route('/highlights-json/<path:userPublicId>/<path:filename>', methods=['GET'])
def get_user_pdf2(userPublicId, filename,inbound=False):
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
        newFile = {"highlights": proccessed_data[filename], "name": filename, "entities": entities, "sections": sample_accordion_data['sections']}
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
    if inbound:
        return full_text

    return response


###socket calls for dynamic content###

@socketio_instance.on('openai_appeal_call')
def handle_openai_call(data):
    ## this is the appeal call ##
    print("Received appeal openai_call with data:", data)
    documentId = data['documentId']
    filename = data['filename']
  
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



@socketio_instance.on('openai-query')
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


@socketio_instance.on('openai-get-recommendation')
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



@socketio_instance.on('openai-get-caselaw')
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


@socketio_instance.on('openai-get-clause')
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



@socketio_instance.on('openai-chat')
def handle_openai_chat(data):
    print('incoming data:', data)
    print(type(data))

    query = data['query']

    query_id = query['id']
    nick_name = query['nickName']
    message_type = query['type']
    question = query['message']  # renaming message to question
    pdf_document_names = query.get('pdfDocumentName')

    if not isinstance(pdf_document_names, list):
        pdf_document_names = [pdf_document_names]

    parsed_contents = []

    for pdf_document_name in pdf_document_names:
        public_id = query.get('publicId')
        if not public_id:
            continue

        dir_path = os.path.join(os.path.dirname(__file__), 'static', 'notes', public_id)
        if not os.path.isdir(dir_path):
            os.makedirs(dir_path, exist_ok=True)

        filepath = os.path.join(dir_path, f'{pdf_document_name}.json')
        if os.path.isfile(filepath):
            print(f"\nReading file: {filepath}\n")
            with open(filepath, 'r') as json_file:
                data = json.load(json_file)
                parsed_text = data.get('text_body', '')
                parsed_contents.append(parsed_text)
        else:
            print(f"\nFile not found: {filepath}\n")

    combined_content = "\n\n".join(parsed_contents)
    combined_input = f"{question}\n\nAdditional context from provided documents:\n{combined_content}"
    
    res_summary, messages = process_user_instruction(combined_input)
    print('done')

    
@socketio_instance.on('connect')
def test_connect():
    session['sid'] = request.sid
    print(f"New connection: {request.sid}")


    @socketio_instance.on('get-document')
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
            @socketio_instance.on('send-changes')
            def sendChanges(delta):
                emit('receive-changes', delta, broadcast=True, include_self=False)

            @socketio_instance.on('save-document')
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

            @socketio_instance.on('disconnect')
            def disconnect():
                print('disconnected!')
        except Exception as err:
            print('An exception occured!!')
            print(err)
            return 'Something went wrong!!'


# if __name__ == "__main__":
#     socketio.run(host='0.0.0.0', debug=True)
    
if __name__ == '__main__':
    socketio_instance.run(app, async_mode='gevent', host='0.0.0.0', port=5000)
