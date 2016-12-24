from __future__ import division
import re
import json
from thereadingmachine.process import read_jsonl
from thereadingmachine.keyword import extract_text_keywords
from thereadingmachine.keyword import get_topic_keywords

# Initialisation
file_prefix = "data/amis_articles"
version = '27_11_2016'
input_file_name = '{0}_{1}_processed.jsonl'.format(file_prefix, version)
output_file_name = '{0}_{1}_commodity_tag.jsonl'.format(file_prefix, version)
test_sample_size = 1000

# Read the data
test_articles = read_jsonl(input_file_name, size=test_sample_size)


# Keyword Extraction
# --------------------------------------------------

# Pre define the topics
topics = ['wheat', 'rice', 'maize', 'soybean']
wheat_keywords, rice_keywords, maize_keywords, soybean_keywords = [
    get_topic_keywords(topic) for topic in topics]
grain_keywords = list(set(get_topic_keywords('grains')) -
                      set(wheat_keywords) -
                      set(rice_keywords) -
                      set(maize_keywords) -
                      set(soybean_keywords))
# Manually remove keywords
#
# Probably should use pop to move the word
for index, grain in enumerate(grain_keywords):
    for topic, topic_keyword in zip(topics,
                                    [wheat_keywords, rice_keywords,
                                     maize_keywords, soybean_keywords]):
        search_string = r'\b' + re.escape(topic) + r'\b'
        if bool(re.search(search_string, grain)):
            print('popping out ' + (grain))
            topic_keyword.append(grain_keywords.pop(index))


def tag_commodity(article, wheat_keywords, rice_keywords,
                  maize_keywords, soybean_keywords, grain_keywords):
    keyword = {'hasWheat': 0,
               'hasRice': 0,
               'hasMaize': 0,
               'hasSoybean': 0,
               'hasGrain': 0
               }

    wheat_match = set(wheat_keywords).intersection(
        article['processed_article'])
    rice_match = set(rice_keywords).intersection(
        article['processed_article'])
    maize_match = set(maize_keywords).intersection(
        article['processed_article'])
    soybean_match = set(soybean_keywords).intersection(
        article['processed_article'])
    grain_match = set(grain_keywords).intersection(
        article['processed_article'])

    if len(wheat_match) > 0:
        keyword['hasWheat'] = 1
    if len(rice_match) > 0:
        keyword['hasRice'] = 1
    if len(maize_match) > 0:
        keyword['hasMaize'] = 1
    if len(soybean_match) > 0:
        keyword['hasSoybean'] = 1
    if len(grain_match) > 0:
        keyword['hasGrain'] = 1
    return keyword

with open(input_file_name) as fi, open(output_file_name, 'w') as fo:
    for line in fi:
        article = json.loads(line)
        tagged_article = tag_commodity(article,
                                       wheat_keywords=wheat_keywords,
                                       rice_keywords=rice_keywords,
                                       maize_keywords=maize_keywords,
                                       soybean_keywords=soybean_keywords,
                                       grain_keywords=grain_keywords)
        tagged_article.update({'id': article['id']})
        json.dump(tagged_article, fo)
        fo.write('\n')

# outputCheck = read_jsonl(output_file_name)
# import pandas as pd
# pd.DataFrame(outputCheck).describe()
