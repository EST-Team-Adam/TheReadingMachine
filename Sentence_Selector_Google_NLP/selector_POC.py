from thereadingmachine.process import read_jsonl
from thereadingmachine.keyword import get_amis_topic_keywords                # Checkwords (from Michael)
from thereadingmachine.sentence_selector import sentences_analyzer
from thereadingmachine.sentence_selector import all_sentences_analyzer
from thereadingmachine.sentence_selector import wordslist
from thereadingmachine.sentence_selector import articles_sentiment
from thereadingmachine.sentence_selector import whole_articles
from thereadingmachine.textcleaner import articles_cleaner
from thereadingmachine.textcleaner import articles_duplicates
from json import dump

#import random     # for random sample


# Initiate file names and parameters
file_prefix = "data/amis_articles"
version = '27_11_2016'
input_file_name = '{0}_{1}_indexed.jsonl'.format(file_prefix, version)
wheat_output_file_name = '{0}_{1}_sentences_wheat.jsonl'.format(file_prefix, version)
rice_output_file_name = '{0}_{1}_sentences_rice.jsonl'.format(file_prefix, version)
soybeans_output_file_name = '{0}_{1}_sentences_soybeans.jsonl'.format(file_prefix, version)
maize_output_file_name = '{0}_{1}_sentences_maize.jsonl'.format(file_prefix, version)
barley_output_file_name = '{0}_{1}_sentences_barley.jsonl'.format(file_prefix, version)
grains_output_file_name = '{0}_{1}_sentences_grains.jsonl'.format(file_prefix, version)
all_sentences_output_file_name = '{0}_{1}_all_sentences.jsonl'.format(file_prefix, version)
articles_scores_output_file_name = '{0}_{1}_articles_scores.jsonl'.format(file_prefix, version)
whole_articles_output_file_name = '{0}_{1}_whole_articles.jsonl'.format(file_prefix, version)
test_sample_size = 1


# Read the data
articles = read_jsonl(input_file_name)



# Test Article

#strings = ['Green Plains EU grains output to revive','best crop bets', 'big bearish wheat bet','wheat futures dodge bullet'] 
#tests = articles_cleaner(articles, strings)

tests = articles      # Full analysis


# Keywords extraction
wheat_keywords, rice_keywords, maize_keywords, barley_keywords, soybean_keywords, grains_keywords = get_amis_topic_keywords()




# Sentences & Sentiment Extraction

articles_analysis = whole_articles(tests)      # performs an analysis on the whole article
#articles_analysis = [x for x in articles_analysis if x is not None]      # clear from None



all_sentences = all_sentences_analyzer(tests, counter)     # performs an analysis on all the sentences
articles_scores = articles_sentiment(all_sentences)        # collapses all sentences results into article scores
#articles_scores1 = [x for x in articles_scores if x is not None]      # clear from None




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



elapsed_time = time.time() - start_time

print elapsed_time


# Save the processed file  # WIP write output file for all the scores

with open(whole_articles_output_file_name, 'w') as f:
     dump(articles_analysis, f)
     f.write('\n')



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
#checkwords = commodity + wordslist(rice_keywords)                                 # It happens that a few people are called Rice
#rice_sentences = sentences_analyzer(tests[0:2], checkwords)
     
