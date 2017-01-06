import cPickle                           # Reads wheat_articles.txt
import pandas as pd                      # Reading, creating and writing dataframes
from nltk.tokenize import sent_tokenize  # tokenization (not so used at the moment)
from vaderSentiment.vaderSentiment import sentiment as vaderSentiment     # Sentiment analysis
from random import choice               # For taking samples
import httplib2                         # Google NLP Authetication
from googleapiclient import discovery
from oauth2client.client import GoogleCredentials
import numpy as np

# Initialization #
with open("wheat_articles.txt", "r") as fp:
    wheat_articles = cPickle.load(fp)
    
#test_sample_size = 1000
    

## SENTIMENT EXTRACTION ##

## Google NLP INITIALIZATION (Testing purposes) ##
#def retrieve_sentiment(string):
#    credentials = GoogleCredentials.get_application_default()
#    service = discovery.build('language', 'v1beta1', credentials=credentials)
#    service_request = service.documents().analyzeSentiment(
#        body={
#            'document': {
#                'type': 'PLAIN_TEXT',
#                'content': string,
#            }
#        }
#    )
import cPickle                                                            # Reads wheat_articles.txt
import pandas as pd                                                       # Reading, creating and writing dataframes
from nltk.tokenize import sent_tokenize                                   # tokenization (not so used at the moment)
from vaderSentiment.vaderSentiment import sentiment as vaderSentiment     # Sentiment analysis
from random import choice                                                 # For taking samples
import numpy as np
import csv

# Initialization
with open("wheat_articles.txt", "r") as fp:
    wheat_articles = cPickle.load(fp)

wheat_keywords = []    
with open('wheat_keywords.csv','rb') as csvfile:
     wheat_keywords = csv.reader(csvfile, delimiter=';')
     wheat_keywords = list(wheat_keywords)
     
wheat_keywords = list([j for i in wheat_keywords for j in i])
    
#test_sample_size = 1000
    
## SENTIMENT EXTRACTION ##

import cPickle                                                            # Reads wheat_articles.txt
import pandas as pd                                                       # Reading, creating and writing dataframes
from nltk.tokenize import sent_tokenize                                   # tokenization (not so used at the moment)
from vaderSentiment.vaderSentiment import sentiment as vaderSentiment     # Sentiment analysis
from random import choice                                                 # For taking samples
import numpy as np
import csv

# Initialization
with open("wheat_articles.txt", "r") as fp:
    wheat_articles = cPickle.load(fp)

wheat_keywords = []    
with open('wheat_keywords.csv','rb') as csvfile:
     wheat_keywords = csv.reader(csvfile, delimiter=';')
     wheat_keywords = list(wheat_keywords)
     
wheat_keywords = list([j for i in wheat_keywords for j in i])
    
#test_sample_size = 1000
    
## SENTIMENT EXTRACTION ##

# VADER
def VADER_analysis(test):
    VADER = list()
    df = pd.DataFrame()
    test['article'] = test['article'].replace(',', '.')   # Article cleaning
    test['article'] = test['article'].replace('\r', ' ')
    test['article'] = test['article'].replace(';', '.')
    test['article'] = test['article'].replace('-', '.')
    highlights = wheat_keywords                                
    sentencesWithHighlights = []                          
    for sentence in sent_tokenize(test['article']):       # Sentence selection (using wheat_keywords)
       for highlight in highlights:
           if highlight in sentence:
              sentencesWithHighlights.append(sentence)
              break
    df_sentences = pd.DataFrame(sentencesWithHighlights)       
    for sentence in sentencesWithHighlights:                   # VADER
		    vs = vaderSentiment(sentence)
		    results = "\n\t" + str(vs)
		    VADER.append(vs)           
    df_sentiment = pd.DataFrame(VADER)                                                              
    df_sentiment['Date'] = test['date']                                 # Article date
    df_sentiment['article_id'] = test['article_id']                     # Article ID
    df = pd.concat([df_sentiment['article_id'],df_sentences, df_sentiment['compound'], df_sentiment['Date']], axis=1)          # Panda output, add sentences if possible
    return df
    
# Data Refinement
test1 = wheat_articles#[:test_sample_size]                        # Insert here articles interval to be analyzed
test = []
for i in range(len(test1)): 
  for word in wheat_keywords:  
    if word in test1[i]['article']: 
          test.append(test1[i])                                   # test is bigger than wheat_articles because article selection duplicates them 
                                                                  # (they may contain more than one wheat keyword being appended once per each keyword), 
                                                                  # but duplicated sentences will be removed in line 67.

# Sentiment Extraction		
sentiment = pd.DataFrame()
for i in range(len(test)):
    sentiment = sentiment.append([VADER_analysis(test[i])])
    
#sentiment['compound'].replace(r'\s+', np.nan, regex=True)
sentiment.columns = ['Article_ID','Sentence', 'Compound', 'Date']

sentiment = sentiment.drop_duplicates(['Sentence'])                # duplicated sentences removal (a lot of sentences removed due to duplicated articles in
                                                                   # original corpus as duplicated by this script articles selection method)

## OUTPUT ##
sentiment.to_csv('df.csv', sep=';',index=False)
