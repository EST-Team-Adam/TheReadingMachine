import json
from googleapiclient import discovery
from oauth2client.client import GoogleCredentials

# Define the function to retrieve sentiments from Google NLP API.


def retrieve_sentiment(string):
    ''' Use the google nlp api to calculate the sentiments.
    '''

    try:
        credentials = GoogleCredentials.get_application_default()
        service = discovery.build(
            'language', 'v1beta1', credentials=credentials)
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
    except:
        polarity = 0
        magnitude = 0
    return {'polarity': polarity, 'magnitude': magnitude}

# Initialisation
file_prefix = "data/amis_articles"
version = '27_11_2016'
input_file_name = '{0}_{1}_processed.jsonl'.format(file_prefix, version)
output_file_name = '{0}_{1}_sentiment.jsonl'.format(file_prefix, version)

# Append sentiments to the articles
#
# NOTE (Michael): It seems that the computational cost of the
#                 sentiment using the Google NLP API is quite high and
#                 may take a great amount of time to compute the
#                 sentiments of all articles. Further, there may be
#                 limits to the request or charges.

with open(input_file_name) as fi, open(output_file_name, 'w') as fo:
    for line in fi:
        article = json.loads(line)
        sentiment = retrieve_sentiment(article['article'])
        sentiment.update({'id': article['id']})
        print(sentiment)
        json.dump(sentiment, fo)
        fo.write('\n')
