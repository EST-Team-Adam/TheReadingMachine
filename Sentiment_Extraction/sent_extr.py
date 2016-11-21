import cPickle
import pandas as pd
from nltk.tokenize import sent_tokenize
from vaderSentiment.vaderSentiment import sentiment as vaderSentiment
from random import choice
import httplib2
from googleapiclient import discovery
from oauth2client.client import GoogleCredentials
import numpy as np
# select one article by using articles[1]['article']

# Initialization
with open("wheat_articles.txt", "r") as fp:
    articles = cPickle.load(fp)
    

## SENTIMENT EXTRACTION ##

# Google NLP INITIALIZATION
def retrieve_sentiment(string):
    credentials = GoogleCredentials.get_application_default()
    service = discovery.build('language', 'v1beta1', credentials=credentials)
    service_request = service.documents().analyzeSentiment(
        body={
            'document': {
                'type': 'PLAIN_TEXT',
                'content': string,
            }
        }
    )
    response = service_request.execute()
    polarity = response['documentSentiment']['polarity']
    magnitude = response['documentSentiment']['magnitude']
    return {'polarity': polarity, 'magnitude': magnitude}

# VADER & GOOGLE NLP
def test_VADER_GoogleNLP(test):
    VADER = list()
    Google_NLP = list()
    df = pd.DataFrame()
    results = {}
    test['article'] = test['article'].replace(',', '.')   # All the , are replaced with .
    highlights = ["wheat"]                                # Looks in each sentence for the word "wheat"
    sentencesWithHighlights = []                          # Stores all the sentences containing "wheat"
    for sentence in sent_tokenize(test['article']):       # One sentence is contained between two . (or fist article's sentence)
       for highlight in highlights:
           if highlight in sentence:
              sentencesWithHighlights.append(sentence)
              break
    df_sentences = pd.DataFrame(sentencesWithHighlights)       
    #for sentence in sentencesWithHighlights:                  # Google NLP
    #        print sentence
    #        print retrieve_sentiment(sentence)
    #        Google_NLP.append(retrieve_sentiment(sentence))
    for sentence in sentencesWithHighlights:                   # VADER
		    #print sentence,
		    vs = vaderSentiment(sentence)
		    results = "\n\t" + str(vs)
		    #print "\n\t" + str(vs)
		    VADER.append(vs)           
    df_sentiment = pd.DataFrame(VADER)                                                              # Change here Google_NLP or VADER
    df_sentiment['Date'] = test['date']                                                             # Gives article date
    df = pd.concat([df_sentences, df_sentiment['compound'], df_sentiment['Date']], axis=1)          # Panda output, add sentences if possible
    return df


# Data Refinement
test1 = articles                           # Insert here articles interval to be analyzed
test = []
word = "wheat" 
for i in range(len(test1)):   
    if word in test1[i]['article']: 
        test.append(test1[i])


# Sentiment Extraction		
sentiment = pd.DataFrame()
for i in range(len(test)):
    sentiment = sentiment.append([test_VADER_GoogleNLP(test[i])])
    
sentiment['compound'].replace(r'\s+', np.nan, regex=True)

## OUTPUT ##

sentiment.to_csv('df.csv', sep=';',index=False)