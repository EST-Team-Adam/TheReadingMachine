from thereadingmachine.process import read_jsonl
from thereadingmachine.keyword import get_amis_topic_keywords                # Checkwords (from Michael)
from thereadingmachine.sentence_selector import sentences_analyzer
from thereadingmachine.sentence_selector import wordslist
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
wheat_keywords, rice_keywords, maize_keywords, barley_keywords, soybean_keywords, grains_keywords = get_amis_topic_keywords()


# Sentences Extraction

commodity = ['wheat']
checkwords = commodity + wordslist(wheat_keywords)       # I've a 'two', 'wild' and 'grain' here that have to be eliminated from wordslist (sentence selector)
wheat_sentences = sentences_analyzer(tests, checkwords)


commodity = ['rice']
checkwords = commodity + wordslist(rice_keywords)                                
rice_sentences = sentences_analyzer(tests, checkwords)


commodity = ['soybeans']
checkwords = commodity + wordslist(soybean_keywords)        # I should eliminate 'bean' from here because it confuses 
soybeans_sentences = sentences_analyzer(tests, checkwords)


commodity = ['maize']
checkwords = commodity + wordslist(maize_keywords)           # I've to eliminate 'may' from here because it can take the month
maize_sentences = sentences_analyzer(tests, checkwords)


# Save the processed file

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
     
###############     TESTING     #####################


#tests[0]['article'] = "Miss Rice went to South Africa last week. Condoleeza Rice said good stuff about american government. I can also talk about Mr Rice who actually won a competition."
#tests[1]['article'] = "Kenya rice production is getting better and better. Paddy is increasing for 2$ and that's enough for being accounted. In US rice price is increased by 20$. Brown rice imports are getting lower as brown rice is still present in the list."
#commodity = ['rice']
#checkwords = commodity + wordslist(rice_keywords)                                 # It happens that a few people are called Rice
#rice_sentences = sentences_analyzer(tests[0:2], checkwords)


#from thereadingmachine.sentence_selector import keyword_alarm
#from thereadingmachine.SBD import SBD
#from thereadingmachine.sentence_keywords import sentence_keywords

#sentence_keywords(SBD(tests[1],checkwords)[2])
#keyword_alarm(SBD(tests[0][1],checkwords),checkwords)
#sentence_keywords('Price of rice is increased by 20$',checkwords)
     
