import httplib2                         # Google NLP Authetication
from googleapiclient import discovery
from oauth2client.client import GoogleCredentials
from json import dump


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
    

# Google NLP
def GoogleNLP(article_sentences):
    sentiment_Google = list()
    for sentence in article_sentences:
       sentiment_Google.append(retrieve_sentiment(sentence))
    return sentiment_Google
