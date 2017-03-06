from thereadingmachine.process import read_jsonl
from thereadingmachine.keyword import get_amis_topic_keywords                # Checkwords (from Michael)
from thereadingmachine.sentence_selector import sentences_analyzer
from json import dump

import random     # for random sample


# Initiate file names and parameters
file_prefix = "data/amis_articles"
version = '27_11_2016'
input_file_name = '{0}_{1}_indexed.jsonl'.format(file_prefix, version)
wheat_output_file_name = '{0}_{1}_sentences_wheat.jsonl'.format(file_prefix, version)
rice_output_file_name = '{0}_{1}_sentences_rice.jsonl'.format(file_prefix, version)
soybeans_output_file_name = '{0}_{1}_sentences_soybeans.jsonl'.format(file_prefix, version)
maize_output_file_name = '{0}_{1}_sentences_maize.jsonl'.format(file_prefix, version)
test_sample_size = 1000


# Read the data
articles = read_jsonl(input_file_name)


# Test Article
tests = random.sample(articles,test_sample_size) # put articles here for full analysis


# WIP
#wheat_keywords, rice_keywords, maize_keywords, barley_keywords, soybean_keywords, grains_keywords = get_amis_topic_keywords()
#checkwords = wheat_keywords


# Sentences Extraction

checkwords =['Wheat']
wheat = sentences_analyzer(tests, checkwords)


#checkwords =['Rice']                                # It happens that a few people are called Rice
#rice = sentences_analyzer(tests, checkwords)


checkwords =['Soybeans']
soybeans = sentences_analyzer(tests, checkwords)


checkwords =['Maize']
maize = sentences_analyzer(tests, checkwords)


# Save the processed file
with open(wheat_output_file_name, 'w') as f:
     dump(wheat, f)
     f.write('\n')
        
        
#with open(rice_output_file_name, 'w') as f:
#     dump(rice, f)
#     f.write('\n')
        
        
with open(soybeans_output_file_name, 'w') as f:
     dump(soybeans, f)
     f.write('\n')
        
        
with open(maize_output_file_name, 'w') as f:
     dump(maize, f)
     f.write('\n')
     
     
