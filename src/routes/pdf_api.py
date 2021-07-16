from flask import Blueprint, jsonify, request, make_response
from src.endpoints.data import json_data, graph_data, search_data
from flask import send_file
import json
import os
import spacy 
from pdfminer.layout import LAParams, LTTextBox
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from collections import Counter
from typing import Pattern 
import pandas as pd
import spacy
import re
from typing import Pattern 
import pandas as pd


output_dir= os.path.dirname(os.path.realpath(__file__)) + "/../../judgclsfymodel8"
output_dir2= os.path.dirname(os.path.realpath(__file__)) + "/../../core_law_md5"

nlp = spacy.load(output_dir)
nlp3=spacy.load(output_dir2)

bp_api = Blueprint(name="pdf_api", import_name=__name__)


@bp_api.route('/graph', methods=['GET', 'OPTION'])
def get_graph_data():
    """ get json data """
    search_query = request.args.get("search_query")
    try:
        output1 = graph_data(search_query)
        response = jsonify(output1)
        return response
    except Exception as err:
        print('An exception occured!!')
        print(err)
        return make_response('Something went wrong!!', 500)

@bp_api.route('/json', methods=['GET'])
def get_json_data():
    """ get json data """
    filename = request.args.get('filename')
    print(filename)
    dir_path = os.path.dirname(os.path.realpath(__file__))
    filePath = dir_path + '/../uploads/8a6c08f0-2704-4b98-a181-ca48fd0592fa/{}'.format(filename)
    print(filePath)
    if os.path.isfile(filePath) == False:
        print('No files found')
        resp = jsonify({'message': 'File Not Found!!'})
        resp.status_code = 404
        return resp
    
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

    for page in pages:
        counter += 1
        print('Processing ', counter, 'page...')

        interpreter.process_page(page)
        layout = device.get_result()
        for lobj in layout:
            if isinstance(lobj, LTTextBox):
                x1, y1, x2, y2, text = lobj.bbox[0], lobj.bbox[1], lobj.bbox[2], lobj.bbox[3], lobj.get_text(
                )
                text = text.strip()
                doc = nlp(text)

                # doc3= nlp3(text)
                sentences = [sent.string.strip() for sent in doc.sents]
                json_dump = []
                for sentence in sentences:

                    if len(sentence) > 33:
                        # doc3=nlp3(sentence)
                        doc2 = nlp(sentence)

                        # doc2.cats.pop('ISSUE')
                        # doc2.cats.pop('OTHER')
                        # doc2.cats=total(doc2.cats)
                        c = Counter(doc2.cats)
                        most_common = c.most_common(1)  # returns top 3 pairs
                        # my_keys = [key for key, val in most_common]
                        # top_category = get_top_cat(doc2)
                        # result = re.findall(pattern, sentence, re.M|re.I)

                        id_counter += 1
                        jsont = {
                            "comment": {
                                "emoji": "NONE",
                                "text": most_common[0][0],
                            },
                            "content": {
                                "text": sentence,
                            },
                            "id": str(id_counter),
                            "position": {
                                "boundingRect": {
                                    "height": 1200,
                                    "width": 809.9999999999999,
                                    "x1": x1,
                                    "y1": y1,
                                    "x2": x2,
                                    "y2": y2,
                                },
                                "pageNumber": counter,
                                "rects": [
                                    {
                                        "height": 1200,
                                        "width": 809.9999999999999,
                                        "x1": x1,
                                        "y1": y1,
                                        "x2": x2,
                                        "y2": y2,
                                    }
                                ]
                            }
                        }

                        arr = proccessed_data.setdefault(filename, [])
                        arr.append(jsont)
    return jsonify(proccessed_data)
    
@bp_api.route('/2newjson', methods=['GET'])
def get_newjson_data():
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
