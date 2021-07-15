import spacy 



nlp3=spacy.load("/home/taymur/Documents/legal2/DATA/spacymodelner/core_law_md5")


text = """ 
ABDUL RAHIM VS U.B.
Downloaded from
PakCaselaw.com
P L D 1997 Karachi 62
Before Ghulam Haider Lakho and Dr. Ghous Muhammad, JJ
ABDUL RAHIM and 2 others-- -APPELLANTS
versus
Messrs UNITED BANK LTD. OF PAKISTAN---Respondent
First Appeals Nos. 26, 27, 29 to 61 of 1995, decided on 02/07/1996.
(a) Banking Tribunals Ordinance (LVIII of 1984)---
----S. 9(1), first proviso---Appeal---Proviso to S.9(1), Banking Tribunals Ordinance, 1984 is rot mandatory but directory in
nature---Just because the said proviso expresses a consequence that an appeal shall not be entertained unless the defendant
first deposits the decretal or other amount would not make the proviso mandatory in nature---Word "shall" will not make a
particular provision mandatory in nature.
Maple Leaf Cement Factory v. The Collector of Centra"""

doc3=nlp3(text)
entities = [(ent.text, ent.label_) for ent in doc3.ents ]

print(entities)

