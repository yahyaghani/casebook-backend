import os
from datetime import datetime
from flask import Blueprint, jsonify, request
from src.endpoints.data import json_data
from src.endpoints.data import graph_data
from src.endpoints.data import search_data
from flask import make_response
from flask import send_file
from elasticsearch import Elasticsearch
import json

es = Elasticsearch()
bp_api = Blueprint(name="blueprint_api", import_name=__name__)


@bp_api.route('/graph', methods=['GET', 'OPTION'])
def get_graph_data():
    """ get json data """
    output1 = graph_data()
    response = jsonify(output1)
    return response


@bp_api.route('/json', methods=['GET'])
def get_json_data():
    """ get json data """
    output = json_data()
    return jsonify(output)


@bp_api.route('/search', methods=['GET'])
def get_search_data():
    """ get search """
    output = search_data()
    return jsonify(output)


@bp_api.route('/jsondata', methods=['GET', 'POST'])
def get_json_state():
    if request.method == 'POST':
        content = request.get_json()
        print(content)
        with open('savedjsonhighlights.json', 'w') as f:
            json.dump(content, f)
        return 'JSON posted'


@bp_api.route('/pdf/<path:filename>', methods=['GET'])
def get_pdf(filename):
    """ get pdf file """
    # retrieve body data from input JSON

    dir_path = os.path.dirname(os.path.realpath(__file__))
    return send_file(dir_path + '/pdf_files/{}'.format(filename), attachment_filename=filename)
