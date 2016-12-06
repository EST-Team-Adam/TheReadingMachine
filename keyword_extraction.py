from __future__ import division
import re
from thereadingmachine.process import read_jsonl
from thereadingmachine.keyword import extract_text_keywords
from thereadingmachine.keyword import get_topic_keywords

# Initialisation
file_prefix = "data/amis_articles"
version = '27_11_2016'
input_file_name = '{0}_{1}_processed.jsonl'.format(file_prefix, version)
test_sample_size = 1000

# Read the data
# articles = read_jsonl(input_file_name, size=test_sample_size)
articles = read_jsonl(input_file_name, size=test_sample_size)


# Keyword Extraction
# --------------------------------------------------

# Pre define the topics
topics = ['wheat', 'rice', 'maize', 'soybean']
wheat_keywords, rice_keywords, maize_keywords, soybean_keywords = [
    get_topic_keywords(topic) for topic in topics]
grains_keywords = list(set(get_topic_keywords('grains')) -
                       set(wheat_keywords) -
                       set(rice_keywords) -
                       set(maize_keywords) -
                       set(soybean_keywords))
# Manually remove keywords
#
# Probably should use pop to move the word
for index, grain in enumerate(grains_keywords):
    for topic, topic_keyword in zip(topics,
                                    [wheat_keywords, rice_keywords,
                                     maize_keywords, soybean_keywords]):
        search_string = r'\b' + re.escape(topic) + r'\b'
        if bool(re.search(search_string, grain)):
            print('popping out ' + (grain))
            topic_keyword.append(grains_keywords.pop(index))

# Extract keywords
for article in articles:
    matched_topic = {}
    for topic in topics:
        matched_topic.update(extract_text_keywords(
            article['processed_article'], topic))
    article['keywords'] = matched_topic

    # article["{0}_keyword".format(topic).decode('UTF-8')] = \
    #     extract_text_keywords(article['processed_article'], topic)

check = [(k, v) for article in articles for k,
         v in article['keywords'].items() if len(v) != 0]
print(len(check))

# Subset articles that are related to wheat
# wheat_articles = [article
#                   for article in articles
#                   if len(article['wheat_keyword']) > 0]
