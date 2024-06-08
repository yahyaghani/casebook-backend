
from openai import OpenAI

import json
import backoff
import spacy
import os 


client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@backoff.on_exception(backoff.expo, Exception, max_tries=5)
def get_rec(instruction,page):
    # prompt = f"""Analyze the legal page :\n\n
    # {page}"""
    prompt = f"""{instruction} :- {page} """
    try:
        response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": f"You are a legal copilot, called Casebook AI, your aim is to help lawyers digest information and answer their queries to help them in their preparation for cases"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=1800,
                n=1,
                temperature=0.96,
            )
        answer_json_string=(response.model_dump_json(indent=2))
        answer_dict = json.loads(answer_json_string)
        answer = answer_dict['choices'][0]['message']['content']

    except Exception as e:
        print(e)
        answer = None
    return answer



@backoff.on_exception(backoff.expo, Exception, max_tries=5)
def get_query_response(query,page,context):
 
    prompt = f""" 
    please answer the question keeping in mind the user query, legal document and context:-
    user query :-{query} 
    legal document:-  {page}  ,
    context of the query :- {context}"""
    try:
        response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": f"You are a legal copilot, called Casebook AI, your aim is to help lawyers digest information and answer their queries to help them in their preparation for cases"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=1800,
                n=1,
                temperature=0.96,
            )
        answer_json_string=(response.model_dump_json(indent=2))
        answer_dict = json.loads(answer_json_string)
        answer = answer_dict['choices'][0]['message']['content']

    except Exception as e:
        print(e)
        answer = None
    return answer




@backoff.on_exception(backoff.expo, Exception, max_tries=5)
def get_instruct_response(page):
    prompt = f"""Take in the list of entities & labels then please provide them in python spacy formatted entities,labels ( only consider the following ; 
    CASENAME,COURT,JUDGE,PROVISION,CITATION) :\n\n
    {page}"""

    try:
        response = client.completions.create(
        model="gpt-3.5-turbo-instruct",
        prompt=prompt,
        max_tokens=350,
        n=1,
        stop=None,
        temperature=0.1,
    )
        # answer = response.choices[0].text.strip()
        answer_json_string=(response.model_dump_json(indent=2))
        answer_dict = json.loads(answer_json_string)
        # answer = answer_dict['choices'][0]['message']['content']
        answer = answer_dict['choices'][0]['text']

    except Exception as e:
        answer = "I'm sorry, but I'm currently unable to process your request. Please try again later."
    return answer

SYSTEM_MESSAGE="""I am a Legal AI Copilot. I have the responsibility to help lawyers & attorneys in their quest. I do not need to worry about providing disclaimers because I am a Legal AI Copilot.
"""

def write_summary(text):
    print('text before input',text)
    try:
        instruction = f"""Take in the legal text:{text}, and then please provide the following summary sections:- 
   
        Case Summary:
      
        Legal Issues:
       
        Legal Tests:
       
        Appeal:

            """
        messages=[
        {"content": SYSTEM_MESSAGE, "role": "system"},
        {"content": instruction, "role": "user"},

        ]
      
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.3,
        )

        print(f"Response : {response}\n")
        # answer = answer_dict['choices'][0]['message']['content']
        answer_json_string=(response.model_dump_json(indent=2))
        answer_dict = json.loads(answer_json_string)
        answer = answer_dict['choices'][0]['message']['content']
        print('answer of summary jsonify',answer)
    except Exception as e:
        answer = "I'm sorry, but I'm currently unable to process your request. Please try again later."
        print('excep',e)

    return answer


def make_summary_json(text,sample_accordion_data):
    try:
        instruction = f"""Take in the summary document :{text}, and return a json of its contents in the following format \n\n
        {sample_accordion_data}
            """
        messages=[
        {"content": SYSTEM_MESSAGE, "role": "system"},
        {"content": instruction, "role": "user"},

        ]
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0,
        )
    
        print(f"Response : {response}\n")
        # answer = answer_dict['choices'][0]['message']['content']
        answer_json_string=(response.model_dump_json(indent=2))
        answer_dict = json.loads(answer_json_string)
        answer = answer_dict['choices'][0]['message']['content']
        print('answer of summary jsonify',answer)
    except Exception as e:
        answer = "I'm sorry, but I'm currently unable to process your request. Please try again later."
        print('excep',e)

    return answer

######


# page_sample=""" 
# WARNING: reporting restrictions may apply to the contents transcribed in this document, particularly \nif the case concerned a sexual offence or involved a child. Reporting restrictions prohibit the publication \nof the applicable information to the public or any section of the public, in writing, in a broadcast or by \nmeans of the internet, including social media. Anyone who receives a copy of this transcript is responsible \nin law for making sure that applicable restrictions are not breached. A person who breaches a reporting \nrestriction is liable to a fine and/or imprisonment. For guidance on whether reporting restrictions apply, \nand to what information, ask at the court office or take legal advice. \nThis  Transcript  is  Crown  Copyright.   It  may  not  be  reproduced  in  whole  or  in  part  other  than  in \naccordance with relevant licence or with the express consent of the Authority.  All rights are reserved.\nIN THE COURT OF APPEAL \nCRIMINAL DIVISION \n \nCase No: 2024/00172/B3 \n[2024] EWCA Crim 312\n\nRoyal Courts of Justice \nThe Strand \nLondon \nWC2A 2LL \n \nThursday  25th  January  2024\n\n\n\n\n\n\n\nB e f o r e:\nVICE PRESIDENT OF THE COURT OF APPEAL CRIMINAL DIVISION\n\n(Lord Justice Holroyde)\nMR  JUSTICE  PICKEN\nMRS  JUSTICE  FARBEY  DBE\n__________________\nR E X\n- v -\nKATHLEEN  CRANE \n____________________\n\n\n\n\n\n\n\n\n\n\n\nComputer Aided Transcription of Epiq Europe Ltd,\nLower Ground Floor, 46 Chancery Lane, London WC2A 1JE\nTel No: 020 7404 1400; Email: rcj@epiqglobal.co.uk (Official Shorthand Writers to the Court)\n_____________________\nMiss F Page appeared on behalf of the Applicant\nMr S Baker KC appeared on behalf of the Crown\n____________________\nJ U D G M E N T\n(Approved)\n____________________\nThursday  25th  January  2024\n\n\nLORD JUSTICE HOLROYDE:\n1.  In 2010 this applicant, Mrs Kathleen Crane, was prosecuted by her employers, the Post\nOffice (\"POL\"), for an alleged offence of fraud by representation, contrary to section 1 of the\nFraud Act 2006.  It was alleged that her actions had resulted in a loss to POL of \u00a318,721.52.\nShe pleaded guilty to that offence, and on 30th July 2010 in the Crown Court at Lewes she was\nsentenced  to  a  community  order,  with  a  requirement  of  200  hours'  unpaid  work.    A\ncompensation order in the sum of \u00a318,721.52 was made against her, although in fact that full\namount had already been paid to POL, even before the prosecution was commenced.  She was\nalso ordered to pay the prosecution costs of \u00a31,550.\n\n2.  Mrs Crane now applies for a long extension of time in which to apply for leave to appeal\nagainst her conviction.  Her applications have been referred to the full court by the Registrar.\n\n3.  The applicant's case has been swiftly processed by the Criminal Appeal Office (the \"CAO\"),\nwhich is experienced in dealing with applications of this nature.   The respondent has helpfully\nmade clear that the applications and appeal are not opposed.  It is, nonetheless, a matter for this\ncourt alone to consider the applications and to decide in accordance with the Criminal Appeal\nAct 1968 whether the conviction is unsafe.  We have been able to do so at today's hearing just\n14 days after the Notice of Appeal was received in the CAO.\n\n4.  We can summarise the facts briefly.  Mrs Crane's husband was the sub-postmaster at the\nOld  Town  sub-Post  Office  in  Eastbourne  (\"the  Post  Office\").    POL's  Horizon  accounting\nsystem (\"Horizon\") was in use at the Post Office.  Mr Crane unfortunately suffered health\nproblems which restricted his ability to work, and for several years the applicant ran the Post\nOffice on his behalf.\n\n2\n\n5.  In January 2010, POL conducted an audit of the accounts of the Post Office.  That audit\nshowed an apparent shortfall of \u00a318,721.52.  The existence of that shortfall was treated by POL\ninvestigators as an incontrovertible fact.  Mr and Mrs Crane were both suspended and were\nrequired to close the Post Office immediately.\n\n6.  Criminal proceedings followed in relation to Mrs Crane.  It appears that her husband was\nnot made the subject of a criminal investigation, but was not formally notified that no such\ninvestigation  would  be  made  against  him.    Mrs  Crane  was  interviewed  under  caution  the\nfollowing month, February 2010.  She accepted that she had been aware of a discrepancy in\nthe accounts and that she had declared a false figure for the cash in hand in order to achieve\nthe balance, which was essential if the account was to be rolled over to the next accounting\nperiod and the operation of the Post Office continued.  She emphasised, however, that she was\nno thief.  She pointed out that for 25 years before assisting her husband with the Post Office\nshe had worked in a job which required her to handle cash daily.  She said that she did not\nknow how the alleged shortfall had arisen, but that she had been aware for many months that\nthere was something wrong somewhere.\n\n7.  The prosecution was commenced in March 2010.  The applicant was charged with one\noffence of fraud by false representation between 28th September and 19th January 2010.  She\ninitially pleaded not guilty, but entered her guilty plea on her first appearance in the Crown\nCourt, having previously indicated her intention to do so.  She was sentenced on the same day.\n\n8.  No leap of the imagination is needed to understand the anxiety and fear which Mrs Crane,\nher husband (since sadly deceased) and their two daughters must have experienced in the period\nbetween the arrival of the auditors and the day of her guilty plea in the Crown Court.  Although\nthe sentence imposed upon her did not involve loss of liberty, it involved her performing 200\n\n3\nhours of unpaid work in the local community which she and her husband had served at the Post\nOffice.  As has been well said in the submissions on her behalf today, that brought with it its\nown humiliations.\n\n9.  As is well known, this court has heard a series of cases in which former sub-postmasters,\nsub-postmistresses and other Post Office employees (collectively referred to for convenience\nas \"SPMs\") have challenged their criminal convictions on the basis of the unreliability of data\nproduced  by  Horizon.    The  series  began  with  R  v  Josephine  Hamilton  and  Others  [2021]\nEWCA Crim 577.  Subsequent cases in the series included R v Margaret White and Others\n[2022] EWCA Crim 435.  The judgments in all of those cases are publicly available.  It is\nsufficient for present purposes for us to summarise their effect very briefly.\n\n10.  In each of those earlier cases this court has had to consider whether the prosecution of the\napplicant or appellant concerned was an abuse of the process, and whether the conviction is\nunsafe.  The principles on which the court has acted and the reasons why a guilty plea did not\nnecessarily bar an appeal against conviction were explained in Hamilton.  The court there used\nthe shorthand term \"Horizon case\" to identify a case in which the reliability of Horizon data\nwas essential to the prosecution and there was no independent evidence of an actual loss from\nthe account of the post office concerned, as opposed to a Horizon-generated shortage.\n\n11.  The court referred to and adopted findings made by Fraser J (as he then was) in civil\nproceedings brought in the High Court by SPMs against POL.  Those findings established two\nkey features which were in existence throughout the period of many years with which the High\nCourt was concerned: first, that there had been serious problems with Horizon which gave rise\nto a material risk that an apparent shortfall in the accounts of a branch Post Office did not in\nfact reflect missing cash or stock, but was caused by one of the known bugs, errors or defects\nin Horizon; secondly, that POL, despite knowing of the serious problems, had failed to consider\n\n4\nor  to  make  appropriate  disclosure  of  those  problems  to  the  employees  who  were  being\nprosecuted.  POL had, on the contrary, asserted that Horizon was robust and reliable, and had\neffectively steamrolled over any SPM who sought to challenge its accuracy.\n\n12.  In the same year as the prosecution of this applicant, POL produced a report asserting the\nrobust reliability of Horizon and, amongst other things, prosecuted a trial against Mrs Misra\nwhich, as has been submitted to us, appears to have been intended to discourage others.\n\n13.  This court found, in the series of cases to which we have referred, that in cases where\nHorizon data was essential to the prosecution, there was no basis for the criminal proceedings\nif the Horizon data was not reliable.  POL's failures of investigation and disclosure prevented\nthe  accused  SPMs  from  challenging  \u2013  or  at  any  rate  from  challenging  effectively  \u2013  the\nreliability of the data.  In short, the court observed, POL as prosecutor brought serious criminal\ncharges against the SPMs on the basis of Horizon data, and by failing to discharge its duties of\ndisclosure it prevented them from having a fair trial on the issue of whether that data was\nreliable.    This  court  further  found  that  by  representing  Horizon  as  reliable  and  refusing  to\ncountenance any suggestion to the contrary, POL effectively sought to reverse the burden of\nproof.  It treated what was no more than a shortfall shown by an unreliable accounting system\nas an incontrovertible loss, and proceeded as if it were for the accused to prove that no such\nloss had occurred.\n\n14.  Denied any disclosure of material capable of undermining the prosecution case, defendants\nwere inevitably unable to discharge that improper burden.  As each prosecution proceeded to\nits successful conclusion, the asserted reliability of Horizon was, on the face of it, reinforced.\nDefendants were prosecuted, convicted and sentenced on the basis that the Horizon data must\nbe correct, and cash must therefore be missing, when in fact there could be no confidence as to\nthat foundation.\n\n5\n\n15.  The court concluded that in Horizon cases the prosecutions were an abuse of the process\nof the court, both because it was not possible for the trial process to be fair and because it was\nan affront to the conscience of the court for the defendant concerned to face prosecution.\n\n16.    Returning  to  this  applicant's  case,  we  have  been  assisted  by  the  written  and  oral\nsubmissions of Miss Page for the applicant and Mr Baker KC for the respondent.  We are\ngrateful to them and to all the legal representatives on both sides.  We are particularly grateful\nfor the admirably focused oral submissions which we have heard this morning.\n\n17.  On behalf of the applicant, Miss Page assists us with her carefully worded summary of the\nmisery heaped on Mrs Crane and her family.  She points out the fear which has prevented Mrs\nCrane from involving herself in any form of challenge to her conviction until very recently.\nMiss Page draw attention, as an example of the continuing consequences of a conviction such\nas this, to the fact that Mrs Crane, now employed in a care home, has had to disclose her\nconviction annually as part of normal vetting processes, no doubt feeling further anxiety each\ntime  as  to  whether  in  some  way  that  conviction  would  come  back  to  impede  her  present\nemployment.\n\n18.  On behalf of the respondent, Mr Baker KC again confirms that the appeal is not opposed.\nHe draws to our attention that this appeal is the first appeal to come before the court as a result\nof  a  new  proactive  process  undertaken  by  the  present  legal  representatives  of  POL.    The\nrespondent's  review  of  conviction  cases  identified  this  applicant's  position  as  a  possible\nHorizon  case.    That  was  a  proactive  review  commissioned  by  POL's  present  solicitors,\ninvolving a team of independent counsel reviewing the files in cases of SPMs convicted during\nthe relevant period who had not thus far brought any appeal against conviction.  Where that\nreview indicated on the face of it that it was a Horizon case, POL has been proactive in writing\n\n6\nto  the  former  SPM  concerned,  drawing  attention  to  the  findings  of  the  review  and,  where\nappropriate,  indicating  that  if  an  appeal  were  to  be  brought,  it  would  not  be  opposed.\nObviously, there will be cases where the initial review cannot immediately enable a conclusion\nto be drawn as to whether that stance should be adopted by POL.  But as Mr Baker rightly\nreminds us, in such cases the former SPM concerned can of course still pursue an application\nfor leave to appeal against conviction, which can then be considered in detail on its merits.  But\nthis case is a first example of what Mr Baker understandably suggests may be many cases in\nwhich  POL  has  taken  the  initiative  in  identifying  a  Horizon  case  and  informing  the  SPM\nconcerned that the appeal would not be opposed.  It is that process which has enabled the matter\nto come before the court so quickly, for the court to deal with this as quickly as it has done,\nand for the court to feel confident that it will be able to process very expeditiously any further\nappeals which may arise from this process.\n\n19.  In Mrs Crane's case, the letter informing her of the findings of the initial review and the\nfact that an appeal would not be opposed was sent in the summer of 2023.  Thereafter, the\napplicant and her representatives proceeded efficiently to prepare and commence the appeal.\n\n20.    It  is  accepted  by  the  respondent  that  this  is  a  Horizon  case,  as  we  have  defined  that\nshorthand  term.    Although  Mrs  Crane  admitted  making  false  declarations,  her  account  in\ninterview was that she had concerns that something was wrong with the shortfall shown by\nHorizon  and  that  she  had  only  falsified  the  accounts  in  order  to  roll  over  into  the  next\naccounting period.  She made it clear in interview that she had been experiencing shortfalls for\nwhich  she  could  find  no  explanation  since  at  least  2008,  and  she  explicitly  asked  the\ninvestigators to look into the reliability of Horizon's indications of those shortfalls.  There is\nnothing to indicate that any such investigation of Horizon's reliability in this case was carried\nout.  The alleged shortfall was based solely on Horizon data, and there was no independent of\nHorizon to show that there was a genuine loss.\n\n7\n\n21.  In those circumstances the respondent accepts that POL was under a duty of investigation\nand disclosure in relation to the reliability of Horizon, but had not discharged that duty.  Mrs\nCrane's appeal is therefore not opposed.\n\n22.    Having  considered  the  evidence  and  the  material  before  us,  we  are  satisfied  that  the\nrespondent's concessions are rightly and properly made.  This is indeed a Horizon case, in\nwhich  the  reliability  of  Horizon  data  was  essential  to  the  prosecution  and  there  was  no\nindependent evidence of the alleged or any actual loss.\n\n23.  The applicant in interview explained why she had acted as she did and  asked  for the\nreliability of Horizon to be investigated.  She and her husband paid the full sum said to be\nmissing.  She was, nonetheless, prosecuted.   No relevant investigation was carried out and no\ndisclosure was made of the known concerns about Horizon.  She pleaded guilty because she\nand those representing her had been kept in ignorance of material evidence which went directly\nto the issue of her alleged guilt.\n\n24.  We have no doubt that her prosecution was an abuse of the process on both of the grounds\nwe have mentioned.  Nor do we have  any doubt that, notwithstanding her guilty plea, her\nconviction is unsafe\n\n25.  We therefore grant Mrs Crane the extension of time which she seeks.  We grant leave to\nappeal.  We allow her appeal and we quash her conviction.\n\n26.  MISS PAGE:  My Lord, may I apply for a defendant's costs order?\n\n27.  LORD JUSTICE HOLROYDE:  The usual course is for you to submit a note of the\n\n8\nexpenses which can properly be claimed which, as you will know (but not everyone will know),\nI am afraid is only very limited.  But what can properly be claimed, if you provide the Registrar\nwith a note, it will be attended to.\n\n28.  MISS PAGE:  I am very grateful.\n\n29.  LORD JUSTICE HOLROYDE:  And in the highly unlikely event that any problem\narises, written submissions can be made to the court.\n\n30. MISS PAGE:  I am very grateful.\n\n31. LORD JUSTICE HOLROYDE:  We do not anticipate for a moment that that will be\nnecessary.\n\n____________________________________\n\nEpiq Europe Ltd hereby certify that the above  is an accurate and  complete record of the\nproceedings or part thereof.\n\nLower Ground, 18-22 Furnival Street, London EC4A 1JS\nTel No: 020 7404 1400\nEmail: rcj@epiqglobal.co.uk\n\n\n______________________________\n\n9\n
# """
# instruction=""" as a legal copilot, please extract the following and provide them in seperate lists ; 
# CITATIONs, JUDGEs, CASENAMEs,COURTs,LEGAL PROVISIONs"""





# #####
# output_dir = "../judgclsfymodel12"
# output_dir3 = "../cite_law_sm8"
# nlp = spacy.load(output_dir)
# nlp3 = spacy.load(output_dir3)

# doc3 = nlp3(returned)
# ents = [(ent.text, ent.label_) for ent in doc3.ents]
# entities=[]
# labels=[]
# # testing output of classifier core_law_md5
# # print(ents)
# for ent in doc3.ents:
#     entities.append(str(ent.text))
#     labels.append(str(ent.label_))

# print(entities)