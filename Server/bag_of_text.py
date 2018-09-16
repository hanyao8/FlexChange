#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep 16 00:43:09 2018

@author: jia_qu
"""

import pandas as pd
import re
import string
import nltk
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer
sw=stopwords.words("english")
positive=pd.read_csv("Positive.csv")

posit=positive["ABLE"].tolist()

positive=[]

for i in range(len(posit)):
    positive.append(posit[i].lower())
    
positive.append('able')    
negative=pd.read_csv("Negative.csv")

neg=negative["ABANDON"].tolist()

negative=[]

for i in range(len(neg)):
    negative.append(neg[i].lower())
negative.append("abandon")

def files(text):
    filename = text
    file=open(filename,'rt')
    text=file.read()
    file.close()
    words = text.split()
    
    table = str.maketrans('', '', string.punctuation)
    stripped = [w.translate(table) for w in words]
    words = re.split(r'\W+', text)
    words = [word.lower() for word in words]

    for word in words:
        if word in sw:
            words.remove(word)
    return words

def optimism(words):
    count=0
    countn=0
    for i in range(len(words)):
        if words[i] in positive:
            count+=1
        elif words[i] in negative:
            countn+=1


    return count/(count+countn)
