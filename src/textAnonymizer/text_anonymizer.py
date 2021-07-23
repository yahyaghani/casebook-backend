'''
To install spacy model use either of the following approaches:

Approach 1:
    pip install spacy
    python -m spacy download en_core_web_sm

Approach 2:
    pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-2.1.0/en_core_web_sm-2.1.0.tar.gz

'''

'''
To do:
    - Create stand-alone API
    - match gender for fictional name
    - anonymize gender (including pronouns)
'''


import en_core_web_sm, random
import os
# reset random seed generator
random.seed(0)
fileDir = os.path.dirname(os.path.abspath(__file__))


with open(fileDir+'\\characters_hg2g.txt','r') as f:
    fictional_person = [x.strip() for x in f.readlines()]

with open(fileDir+'\\fictional_races.txt','r') as f:
    fictional_norp = [x.strip() for x in f.readlines()]

with open(fileDir+'\\fictional_organization.txt','r') as f:
    fictional_org = [x.strip() for x in f.readlines()]

with open(fileDir+'\\locations_hg2g.txt','r') as f:
    fictional_gpe = [x.strip() for x in f.readlines()]

with open(fileDir+'\\fictional_language.txt','r') as f:
    fictional_language = [x.strip() for x in f.readlines()]

# list of all the names seen so far.
# Unlike fictional_person_assignment.keys(), this list includes repeated
# occurances. It is used to distinguish ambiguity when there are multiple people
# with the same first or last name.
seen_people=[]

# dictionary of the actual names (as key)
# and the assigned fictional names (as values)
fictional_person_assignment=dict()

# count used to generate "person" if ran out of fictional names
xcess_person_count = 0

fictional_norp_assignment=dict()
xcess_norp_count = 0

fictional_org_assignment=dict()
xcess_org_count = 0

fictional_gpe_assignment=dict()
xcess_gpe_count = 0

fictional_language_assignment=dict()
xcess_language_count = 0


def name_seen(s,l):
    '''
    Check if a name has been seen befere, and if it has,
    return the full name.
    The goal is to address the following scenarios:
    (1) A name, e.g., John Smith, has been seen before but
    instead of the full name, only part of it appears again,
    e.g., only John. (The first appearance of a name is
    usually the full name.)
    (2) Return the last seen full name. This is useful when
    there are different people with the same first or last name,
    in which case we are probably referring to the last one mentioned.

    '''
    seen = False
    full_name = None
    for x in l:
        if s in x:
            seen = True
            full_name = x
    return seen, full_name

def match_fictional_name(text, full_name, full_fictional_name):
    '''
    match fictional name with how the real name was called - e.g., if only
    called by first name, return only the first name of the fictional name.
    Inputs:
        text: string - the original name as called in the text
        full_name: string - the original full name
        full_fictional_name: string - the full fictional name
    Output: string - the matched fictional name
    '''
    if text == full_name:
        return full_fictional_name
    l_name = full_name.split()
    l_fictional_name = full_fictional_name.split()
    if l_name.index(text) == 0:
        return l_fictional_name[0]
    else:
        return l_fictional_name[1]
    
    
def get_fictional_person(text):
    global fictional_person_assignment
    global xcess_person_count
    global seen_people
    
    # ckeck to see if the person has been seen before
    seen, full_name = name_seen(text, seen_people)
    
    if not seen:
        full_name = text # assume the first mention includes the full name
       
        # check to see if there is any unused fictional name left in the list
        # if not return [REDACTED]
        if len(fictional_person_assignment)<len(fictional_person):
            while True:
                x = fictional_person[random.randint(0,len(fictional_person)-1)]
                if not x in fictional_person_assignment.values():
                    break
            fictional_person_assignment[full_name]=x
        else:
            xcess_person_count += 1
            fictional_person_assignment[full_name]='FIRSTNAME'+str(xcess_person_count)+' '+'LASTNAME'+str(xcess_person_count)
    
    seen_people.append(full_name)
    return match_fictional_name(text, full_name, fictional_person_assignment[full_name])
        
def get_fictional_norp(text):
    global fictional_norp_assignment
    global xcess_norp_count
    if text in fictional_norp_assignment:
        return fictional_norp_assignment[text]
    else:
        # check to see if there is any unused fictional name left in the list
        # if not return a counting placeholder
        if len(fictional_norp_assignment)<len(fictional_norp):
            while True:
                x = fictional_norp[random.randint(0,len(fictional_norp)-1)]
                if not x in fictional_norp_assignment.values():
                    break
            fictional_norp_assignment[text]=x
            return fictional_norp_assignment[text]
        else:
            xcess_norp_count += 1
            fictional_norp_assignment[text]='[GROUP'+str(xcess_norp_count)+']'
            return fictional_norp_assignment[text]

def get_fictional_org(text):
    global fictional_org_assignment
    global xcess_org_count
    if text in fictional_org_assignment:
        return fictional_org_assignment[text]
    else:
        # check to see if there is any unused fictional name left in the list
        # if not return a counting placeholder
        if len(fictional_org_assignment)<len(fictional_org):
            while True:
                x = fictional_org[random.randint(0,len(fictional_org)-1)]
                if not x in fictional_org_assignment.values():
                    break
            fictional_org_assignment[text]=x
            return fictional_org_assignment[text]
        else:
            xcess_org_count += 1
            fictional_org_assignment[text]='[ORGANIZAION'+str(xcess_org_count)+']'
            return fictional_org_assignment[text]

def get_fictional_gpe(text):
    global fictional_gpe_assignment
    global xcess_gpe_count
    if text in fictional_gpe_assignment:
        return fictional_gpe_assignment[text]
    else:
        # check to see if there is any unused fictional name left in the list
        # if not return a counting placeholder
        if len(fictional_gpe_assignment)<len(fictional_gpe):
            while True:
                x = fictional_gpe[random.randint(0,len(fictional_gpe)-1)]
                if not x in fictional_gpe_assignment.values():
                    break
            fictional_gpe_assignment[text]=x
            return fictional_gpe_assignment[text]
        else:
            xcess_gpe_count += 1
            fictional_gpe_assignment[text]='[COUNTRY'+str(xcess_gpe_count)+']'
            return fictional_gpe_assignment[text]

def get_fictional_language(text):
    global fictional_language_assignment
    global xcess_language_count
    if text in fictional_language_assignment:
        return fictional_language_assignment[text]
    else:
        # check to see if there is any unused fictional name left in the list
        # if not return a counting placeholder
        if len(fictional_language_assignment)<len(fictional_language):
            while True:
                x = fictional_language[random.randint(0,len(fictional_language)-1)]
                if not x in fictional_language_assignment.values():
                    break
            fictional_language_assignment[text]=x
            return fictional_language_assignment[text]
        else:
            xcess_language_count += 1
            fictional_language_assignment[text]='[LANGUAGE'+str(xcess_language_count)+']'
            return fictional_language_assignment[text]

def replace_name(token, name_types=["PERSON"], fictional=False):
    '''
    For a given token, return the token text or a place holder depending on the
    token type.
    Inputs:
        token: spaCy token object
        name_types: name types to be annonymized (default = "PERSON")
                    valid types include:
                        PERSON	People, including fictional.
                        NORP	Nationalities or religious or political groups.
                        FAC	Buildings, airports, highways, bridges, etc.
                        ORG	Companies, agencies, institutions, etc.
                        GPE	Countries, cities, states.
                        LOC	Non-GPE locations, mountain ranges, bodies of water.
                        PRODUCT	Objects, vehicles, foods, etc. (Not services.)
                        EVENT	Named hurricanes, battles, wars, sports events, etc.
                        WORK_OF_ART	Titles of books, songs, etc.
                        LAW	Named documents made into laws.
                        LANGUAGE	Any named language.
                        DATE	Absolute or relative dates or periods.
                        TIME	Times smaller than a day.
                        PERCENT	Percentage, including ”%“.
                        MONEY	Monetary values, including unit.
                        QUANTITY	Measurements, as of weight or distance.
                        ORDINAL	“first”, “second”, etc.
                        CARDINAL	Numerals that do not fall under another type.
        fictional: if True, names are replaces with fictional names rather than place holders
    Outputs:
        text: either the origin token text or a place holder
    '''
    if token.ent_iob != 0 and token.ent_type_ in name_types:
        if fictional:
            if token.ent_type_ == "PERSON":
                txt = get_fictional_person(token.text)
            elif token.ent_type_ == "NORP":
                txt = get_fictional_norp(token.text)
            elif token.ent_type_ == "ORG":
                txt = get_fictional_org(token.text)
            elif token.ent_type_ == "GPE":
                txt = get_fictional_gpe(token.text)
            elif token.ent_type_ == "LANGUAGE":
                txt = get_fictional_language(token.text)
            else:
                txt = "[REDACTED]"
        else:                
            txt = "[REDACTED]"
    else:
        txt = token.text
    return txt + token.whitespace_


def anonymize(text, name_types=["PERSON"], fictional=False):
    '''
    Annonymize a piece of text by replacing names with a place holder.
    Inputs:
        text: input text
        name_types: name types to be annonymized (default = "PERSON")
                    valid types include:
                        PERSON	People, including fictional.
                        NORP	Nationalities or religious or political groups.
                        FAC	Buildings, airports, highways, bridges, etc.
                        ORG	Companies, agencies, institutions, etc.
                        GPE	Countries, cities, states.
                        LOC	Non-GPE locations, mountain ranges, bodies of water.
                        PRODUCT	Objects, vehicles, foods, etc. (Not services.)
                        EVENT	Named hurricanes, battles, wars, sports events, etc.
                        WORK_OF_ART	Titles of books, songs, etc.
                        LAW	Named documents made into laws.
                        LANGUAGE	Any named language.
                        DATE	Absolute or relative dates or periods.
                        TIME	Times smaller than a day.
                        PERCENT	Percentage, including ”%“.
                        MONEY	Monetary values, including unit.
                        QUANTITY	Measurements, as of weight or distance.
                        ORDINAL	“first”, “second”, etc.
                        CARDINAL	Numerals that do not fall under another type.
        fictional: if True, names are replaces with fictional names rather than place holders
    Outputs:
        text: annonymized text
    '''
    nlp = en_core_web_sm.load()
    
    # parse the text with spacy
    doc = nlp(text)
    
    for ent in doc.ents:
        ent.merge()
    tokens = [replace_name(t, name_types=name_types, fictional=fictional) for t in doc]
    return "".join(tokens) 