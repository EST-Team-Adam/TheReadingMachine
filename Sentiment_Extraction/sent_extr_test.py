import cPickle
import pandas as pd
from nltk.tokenize import sent_tokenize
from vaderSentiment.vaderSentiment import sentiment as vaderSentiment
from random import choice
import httplib2
from googleapiclient import discovery
from oauth2client.client import GoogleCredentials
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
    for sentence in sentencesWithHighlights:                # Google NLP
            print sentence
            print retrieve_sentiment(sentence)
            Google_NLP.append(retrieve_sentiment(sentence))
    for sentence in sentencesWithHighlights:                # VADER
		    print sentence,
		    vs = vaderSentiment(sentence)
		    results = "\n\t" + str(vs)
		    print "\n\t" + str(vs)
		    VADER.append(vs)
    df = pd.DataFrame(VADER,Google_NLP)                     # Panda dataframe
    return df
	    #results[test['date']] = VADER
    #return VADER

# Sentiment Extraction Test		
test = choice(articles)
df = []
df = test_VADER_GoogleNLP(test)

## OUTPUT ##

df.to_csv('df_test.csv', sep=';')                           # Panda csv output
