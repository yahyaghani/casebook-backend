#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 26 22:05:38 2019

@author: mkayvanrad
"""

with open('fictional_person_raw.txt','r') as f:
    lines = f.readlines()

clean_lines = [x[0:x.find('(')].strip() for x in lines]

with open('fictional_person.txt','w') as f:
    for s in clean_lines:
        l = s.split()
        if len(s)>1 and len(l)==2 and not '.' in s and not ',' in s \
            and not l[0].lower() in ['miss','sir','big'] \
            and not l[1].lower() in ['family']:
            f.write(f"{s}\n")

