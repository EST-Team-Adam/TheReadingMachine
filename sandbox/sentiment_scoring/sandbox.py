
# GOOGLE NLP ENGINE

# @retry  # (stop_max_attempt_number=10, wait_random_min=1000, wait_random_max=10000)
# def retrieve_sentiment(string):
#     credentials = GoogleCredentials.get_application_default()
#     service = discovery.build('language', 'v1beta1', credentials=credentials)
#     service_request = service.documents().analyzeSentiment(
#         body={
#             'document': {
#                 'type': 'PLAIN_TEXT',
#                 'content': string,
#             }
#         }
#     )
#     try:
#         response = service_request.execute()
#         polarity = response['documentSentiment']['polarity']
#         magnitude = response['documentSentiment']['magnitude']
#         return {'polarity': polarity, 'magnitude': magnitude}
#     except KeyboardInterrupt:
#         raise
#     except:
#         print 'Block of text not accepted by Google NLP'


# def GoogleNLP2(sentence):
#     sentiment_Google = retrieve_sentiment(sentence)
#     return sentiment_Google


# SENTIMENT EXTRACTION FUNCTION
# def whole_articles(tests):     # whole articles analysis
#     counter = 0
#     results = list()
#     for test in tests:
#         dict = {'article': [], 'date': [], 'id': [],
#                 'Google_NLP_detail': [], 'VADER': [], 'Google_NLP': []}
#         counter = counter + 1
#         dict['date'] = test['date']
#         dict['article'] = test['article']
#         dict['id'] = test['id']
#         dict['Google_NLP_detail'] = GoogleNLP2(test['article'])
#         dict['VADER'] = VADER2(test['article'])
#         try:
#             dict['Google_NLP'] = dict['Google_NLP_detail']['polarity'] * \
#                 dict['Google_NLP_detail']['magnitude']
#         except KeyboardInterrupt:
#             raise
#         except:
#             print 'No Google NLP Sentiment'
#         # print dict
#         print counter
#         results.append(dict)
#         # print results
#     return results
