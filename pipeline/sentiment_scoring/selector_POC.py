import os
from thereadingmachine.process import read_jsonl
from thereadingmachine.keyword import get_amis_topic_keywords
from thereadingmachine.sentence_selector import sentences_analyzer
from thereadingmachine.sentence_selector import all_sentences_analyzer
from thereadingmachine.sentence_selector import wordslist
from thereadingmachine.sentence_selector import articles_sentiment
from json import dump

# import random     # for random sample


# Load environment variable for dataset
data_dir = os.environ['DATA_DIR']
dataset_version = os.environ['DATASET_VERSION']

input_file_name = '{0}/amis_articles_{1}.jsonl'.format(
    data_dir, dataset_version)


# Initiate file names and parameters
wheat_output_file_name = '{0}/amis_articles_{1}_sentences_wheat.jsonl'.format(
    data_dir, dataset_version)
rice_output_file_name = '{0}/amis_articles_{1}_sentences_rice.jsonl'.format(
    data_dir, dataset_version)
soybeans_output_file_name = '{0}/amis_articles_{1}_sentences_soybeans.jsonl'.format(
    data_dir, dataset_version)
maize_output_file_name = '{0}/amis_articles_{1}_sentences_maize.jsonl'.format(
    data_dir, dataset_version)
barley_output_file_name = '{0}/amis_articles_{1}_sentences_barley.jsonl'.format(
    data_dir, dataset_version)
grains_output_file_name = '{0}/amis_articles_{1}_sentences_grains.jsonl'.format(
    data_dir, dataset_version)
all_sentences_output_file_name = '{0}/amis_articles_{1}_all_sentences_grains.jsonl'.format(
    data_dir, dataset_version)
articles_scores_output_file_name = '{0}/amis_articles_{1}_all_sentences_grains.jsonl'.format(
    data_dir, dataset_version)
test_sample_size = 1000


# Read the data
articles = read_jsonl(input_file_name)


# Test Article
# tests = random.sample(articles,test_sample_size) # Test analysis
tests = articles

# Keywords extraction
wheat_keywords, rice_keywords, maize_keywords, barley_keywords, soybean_keywords, grains_keywords = get_amis_topic_keywords()


# Test

#all_sentences = all_sentences_analyzer(tests)
#analyzed_sentences = all_sentences

#articles_scores = articles_sentiment(analyzed_sentences)


# Sentences Extraction

all_sentences = all_sentences_analyzer(tests)
articles_scores = articles_sentiment(all_sentences)

commodity = ['wheat']
checkwords = commodity + wordslist(wheat_keywords)
wheat_sentences = sentences_analyzer(tests, checkwords)
wheat_articles_scores = articles_sentiment(wheat_sentences)


commodity = ['rice']
checkwords = commodity + wordslist(rice_keywords)
rice_sentences = sentences_analyzer(tests, checkwords)
rice_articles_scores = articles_sentiment(rice_sentences)


commodity = ['soybeans']
checkwords = commodity + wordslist(soybean_keywords)
soybeans_sentences = sentences_analyzer(tests, checkwords)
soybeans_articles_scores = articles_sentiment(soybeans_sentences)


commodity = ['maize']
checkwords = commodity + wordslist(maize_keywords)
maize_sentences = sentences_analyzer(tests, checkwords)
maize_articles_scores = articles_sentiment(maize_sentences)


commodity = ['barley']
checkwords = commodity + wordslist(barley_keywords)
barley_sentences = sentences_analyzer(tests, checkwords)
barley_articles_scores = articles_sentiment(barley_sentences)


commodity = ['grains']
checkwords = commodity + wordslist(grains_keywords)
grains_sentences = sentences_analyzer(tests, checkwords)
grains_articles_scores = articles_sentiment(grains_sentences)


# Save the processed file  # WIP write output file for all the scores

with open(all_sentences_output_file_name, 'w') as f:
    dump(all_sentences, f)
    f.write('\n')


with open(articles_scores_output_file_name, 'w') as f:
    dump(articles_scores, f)
    f.write('\n')


with open(wheat_output_file_name, 'w') as f:
    dump(wheat_sentences, f)
    f.write('\n')


with open(rice_output_file_name, 'w') as f:
    dump(rice_sentences, f)
    f.write('\n')


with open(soybeans_output_file_name, 'w') as f:
    dump(soybeans_sentences, f)
    f.write('\n')


with open(maize_output_file_name, 'w') as f:
    dump(maize_sentences, f)
    f.write('\n')


with open(barley_output_file_name, 'w') as f:
    dump(barley_sentences, f)
    f.write('\n')


with open(grains_output_file_name, 'w') as f:
    dump(grains_sentences, f)
    f.write('\n')

###############     TESTING     #####################


#tests[0]['article'] = "Miss Rice went to South Africa last week. Condoleeza Rice said good stuff about american government. I can also talk about Mr Rice who actually won a competition."
#tests[1]['article'] = "Kenya rice production is getting better and better. Paddy is increasing for 2$ and that's enough for being accounted. In US rice price is increased by 20$. Brown rice imports are getting lower as brown rice is still present in the list."
#commodity = ['rice']
# checkwords = commodity + wordslist(rice_keywords)                                 # It happens that a few people are called Rice
#rice_sentences = sentences_analyzer(tests[0:2], checkwords)
