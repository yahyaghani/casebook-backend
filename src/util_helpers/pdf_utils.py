
import json
import os
from os.path import isfile, join, dirname
from flask import jsonify
from flask import current_app

from pdfminer.high_level import extract_text
from pdfminer.layout import LAParams, LTTextBox
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
import spacy


from src.db.main_model import *  # Adjust import according to your project structure
from src.openai_funcs import write_summary,make_summary_json
nlp = spacy.load("en_blackstone_proto")

def ensure_directory_exists(path):
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)


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


sample_accordion_data={
    "sections": [
      {
        "clause": "Case Summary",
        "text": "This is the Summary of this case"
      },
      {
        "clause": "Issues",
        "text": "These are the Legal Issues in this judgement...."
      },
      {
        "clause": "Legal Tests",
        "text": "These are the Legal Tests ascribed in this judgement...."
      },
      {
        "clause": "Appeal",
        "text": "These are the considerations for us to write an Appeal."
      }


    ]
  }
  
instruction_for_entities=instruction=""" as a legal copilot, please extract the following and provide them in seperate lists ; 
# CITATIONs, JUDGEs, CASENAMEs,COURTs,LEGAL PROVISIONs"""

my_labels = ["CITATION", "CASENAME", "PROVISION", "JUDGE", "COURT","INSTRUMENT"]



def process_pdf(userPublicId, filename):
  # retrieve body data from input JSON
    print(userPublicId)
    print(filename)

    base_dir = current_app.config['STATIC_FOLDER']
    upload_dir = join(base_dir, 'uploads', userPublicId)
    filePath = join(upload_dir, filename)
    summary_dir = join(base_dir, 'summary', userPublicId)
    ensure_directory_exists(summary_dir)

    summary_file_path = join(summary_dir, f'{filename}.txt')

    print(filePath)

    dir = join(base_dir, 'highlights', userPublicId)
    if os.path.isdir(dir) == False:
        print("doesnt exist")
        os.makedirs(dir, exist_ok=True)
    filepath = join(dir, filename + '.json')

    isHighlightsAvailable = False
    data = {}
    # If summary file exists, read from it and return
    if os.path.isfile(summary_file_path):
        print(f"Summary file {summary_file_path} exists, reading...")
        with open(summary_file_path, 'r', encoding='utf-8') as file:
            summary_text = file.read()
        return summary_text

    # Directory for storing highlights
    highlights_dir = join(base_dir, 'highlights', userPublicId)
    ensure_directory_exists(highlights_dir)
    highlights_file_path = join(highlights_dir, f'{filename}.json')
    graphDir = join(base_dir, 'graphData', userPublicId)

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
                    # print (f"\"{sentence}\" {top_category}\n")
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
    summary_text=write_summary(full_text)
    get_sections=make_summary_json(summary_text,sample_accordion_data)
    sections_dict = json.loads(get_sections)
    sections_data = sections_dict['sections']

    if os.path.isdir(graphDir) == False:
        print("doesnt exist")
        os.makedirs(graphDir, exist_ok=True)
    if filename in proccessed_data:
        newFile = {"highlights": proccessed_data[filename], "name": filename, "entities": entities, "sections": sections_data}
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

    with open(join(highlights_dir,filename + '.json'), 'w') as json_file:
        json.dump(newFile, json_file)
        
    notesDir =     join(base_dir, 'notes', userPublicId)
    if not os.path.isdir(notesDir):
        os.makedirs(notesDir, exist_ok=True)
    notesFilePath = os.path.join(notesDir, filename + '.json')

    # Save the full_text into a JSON file
    with open(notesFilePath, 'w') as notes_file:
        json.dump({"text_body": full_text}, notes_file)
    print('done processing file')
    return full_text

