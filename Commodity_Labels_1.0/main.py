## MODULES ##

from __future__ import division # for division, forces floating result
import matplotlib
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap, cm
from matplotlib.path import Path

matplotlib.style.use('ggplot')

import math
import time
import datetime
import json

from pandas import DataFrame, Series
import pandas as pd
import numpy as np

import nltk
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('vader_lexicon')

from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.stem.snowball import SnowballStemmer

import re
import string
regex = re.compile('[%s]' % re.escape(string.punctuation)) 

import csv

import collections

## DATA LOADING ##

#version = ""
version = "_28_07_2016"         # Change the version if the database version changes!
with open('amis_articles{0}.jsonl'.format(version)) as f:
    articles = pd.DataFrame(json.loads(line) for line in f)

articles['date'] = pd.to_datetime(articles['date'])
articles['timestamp'] = articles['date'].apply(lambda d: time.mktime(d.timetuple()))
articles = articles.sort('date', ascending=1)

articles['raw_article'] = articles['article']

sources = list(articles['source'].unique())

articles1 = articles.sample(n=4000) # takes a randomized articles sample (test purposes, to be removed or converted to training set)

## ARTICLES PROCESSING ## 

stemmer = SnowballStemmer("english")     # define the stemming system

def clean_and_tokenize_article(article):
    tokenized_article = word_tokenize(article)
    tokenized_article = [regex.sub(u'', token).lower() for token in tokenized_article]
    tokenized_article = filter(lambda x: not x in stopwords.words('english') + [u''], tokenized_article)
    stemmed_article = [ stemmer.stem(x) for x in tokenized_article]
    #return tokenized_article
    return stemmed_article   # either tokenized_article or stemmed_article

# articles['article'] = articles['raw_article'].apply(clean_and_tokenize_article) 1 hour and 20 min
articles1['article'] = articles1['raw_article'].apply(clean_and_tokenize_article)
# articles['article'].head(5)
articles1['article'].head(5)
# put articles.article[1]

def NA(article):
   if len(article) == 0:
        article = ['NA','NA','NA','NA','NA','this','this','this','this','article','article','article','is','is','missing']
   return article

def short(article):   
   if len(article) < 6:
        article = ['NA','NA','NA','NA','NA','this','this','this','this','article','article','article','is','is','too short']
   return article

articles1['article'] = articles1['article'].apply(NA)
articles1['article'] = articles1['article'].apply(short)


##############################################  LABELS  ###############################################

labels_matrix = np.zeros(shape=(articles1['article'].shape[0],5))

for i in range(0,labels_matrix.shape[0]):
        c = collections.Counter(articles1['article'][articles1.index[i]])
        labels_matrix[i,0] = c['wheat'] + c['crop'] + c['grain'] + c['cereal'] + c['grass'] + c['durum'] + c['gluten'] + c['semolina'] + c['spelt'] + c['harvest'] + c['farm'] + c['agricoltur']
        labels_matrix[i,1] = c['maiz'] + c['corn'] + c['crop'] + c['grain'] + c['cereal'] + c['harvest'] + c['farm'] + c['agricoltur']
        labels_matrix[i,2] = c['soybean'] + c['soy'] + c['crop'] + c['harvest'] + c['farm'] + c['agricoltur']
        labels_matrix[i,3] = c['rice'] + c['paddi'] + c['crop'] + c['grain'] + c['harvest'] + c['farm'] + c['agricoltur'] + c['mill'] + c['kernel']
        if np.sum(labels_matrix[i,0:3]) > 10:
            if labels_matrix[i,0] > labels_matrix[i,1] and labels_matrix[i,0] >labels_matrix[i,2] and labels_matrix[i,0] >labels_matrix[i,3]:
               labels_matrix[i,4] = 0
            elif labels_matrix[i,1] > labels_matrix[i,0] and labels_matrix[i,1] > labels_matrix[i,2] and labels_matrix[i,1] > labels_matrix[i,3]:
                      labels_matrix[i,4] = 1
            elif labels_matrix[i,2] > labels_matrix[i,0] and labels_matrix[i,2] > labels_matrix[i,1] and labels_matrix[i,2] > labels_matrix[i,3]:
                      labels_matrix[i,4] = 2
            elif labels_matrix[i,3] > labels_matrix[i,0] and labels_matrix[i,3] > labels_matrix[i,1] and labels_matrix[i,3] > labels_matrix[i,2]:
                      labels_matrix[i,4] = 3
            else:
                labels_matrix[i,4] = 4
        else:
                labels_matrix[i,4] = 5


np.size(np.compress((labels_matrix[:,4] <= 3),labels_matrix))/(np.size(np.compress((labels_matrix[:,4] > 4),labels_matrix))+np.size(np.compress((labels_matrix[:,4] <= 4),labels_matrix)))
np.size(np.compress((labels_matrix[:,4] <= 4),labels_matrix))/(np.size(np.compress((labels_matrix[:,4] > 4),labels_matrix))+np.size(np.compress((labels_matrix[:,4] <= 4),labels_matrix)))

word1 = [0 for i in range(articles1['article'].shape[0])]
word2 = [0 for i in range(articles1['article'].shape[0])]
word3 = [0 for i in range(articles1['article'].shape[0])]
word4 = [0 for i in range(articles1['article'].shape[0])]
word5 = [0 for i in range(articles1['article'].shape[0])]
for i in range(articles1['article'].shape[0]):
       word1[i] = collections.Counter(articles1['article'][articles1.index[i]]).most_common(5)[0][0]
       word2[i] = collections.Counter(articles1['article'][articles1.index[i]]).most_common(5)[1][0]
       word3[i] = collections.Counter(articles1['article'][articles1.index[i]]).most_common(5)[2][0]
       word4[i] = collections.Counter(articles1['article'][articles1.index[i]]).most_common(5)[3][0]
       word5[i] = collections.Counter(articles1['article'][articles1.index[i]]).most_common(5)[4][0]

#######################################     OUTPUT     #################################################
       
names = ['Index' , 'wheat','maize','soybeans','rice','class','Word1','Word2','Word3','Word4','Word5']
df_labels = pd.DataFrame(labels_matrix, columns=names[1:6])
word1 = pd.DataFrame(word1)
word2 = pd.DataFrame(word2)
word3 = pd.DataFrame(word3)
word4 = pd.DataFrame(word4)
word5 = pd.DataFrame(word5)
index = pd.DataFrame(articles1.index)
df = pd.concat([index , df_labels , word1 , word2 , word3 , word4 , word5], axis=1)
df.columns = names

df.to_csv('df.csv', index=True, header=True, sep=';')
