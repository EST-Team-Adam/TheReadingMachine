import httplib2                         # Google NLP Authetication
from googleapiclient import discovery
from oauth2client.client import GoogleCredentials
from json import dump
import time
from retrying import retry


@retry#(stop_max_attempt_number=10, wait_random_min=1000, wait_random_max=10000)
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
    try:
        response = service_request.execute()
        polarity = response['documentSentiment']['polarity']
        magnitude = response['documentSentiment']['magnitude']
        return {'polarity': polarity, 'magnitude': magnitude}
    except KeyboardInterrupt:
        raise
    except:
        print 'Block of text not accepted by Google NLP'



# Google NLP
def GoogleNLP(article_sentences):
    sentiment_Google = list()
    for sentence in article_sentences:
        sent = retrieve_sentiment(sentence)
        sentiment_Google.append(sent)  
    return sentiment_Google
    

def GoogleNLP2(sentence):                       
    sentiment_Google = retrieve_sentiment(sentence)
    return sentiment_Google
