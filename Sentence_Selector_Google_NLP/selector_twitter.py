from thereadingmachine.process import read_jsonl
from thereadingmachine.keyword import get_amis_topic_keywords                   # Checkwords (from Michael)
from thereadingmachine.sentence_selector import sentences_analyzer_twitter
from thereadingmachine.sentence_selector import wordslist
from thereadingmachine.twitter import twitter_reader
from thereadingmachine.twitter import twitter_formatter                  # formats and selects english language tweets
from thereadingmachine.twitter import tweets_unicode                     # special characters removal
from thereadingmachine.sentence_selector import all_sentences_analyzer
from thereadingmachine.sentence_selector import articles_sentiment
from json import dump


for tweet in all_tweets:
    print len(tweet['sentences'][0][1]['compound'])

# Initiate file names and parameters
file_prefix = "data/twitter"
input_file_name = '{0}_timelines.csv'.format(file_prefix)
all_tweets_output_file_name = '{0}_all_tweets.jsonl'.format(file_prefix)
wheat_output_file_name = '{0}_tweets_wheat.jsonl'.format(file_prefix)
rice_output_file_name = '{0}_tweets_rice.jsonl'.format(file_prefix)
soybeans_output_file_name = '{0}_tweets_soybeans.jsonl'.format(file_prefix)
maize_output_file_name = '{0}_tweets_maize.jsonl'.format(file_prefix)
barley_output_file_name = '{0}_tweets_barley.jsonl'.format(file_prefix)
grains_output_file_name = '{0}_tweets_grains.jsonl'.format(file_prefix)
test_sample_size = 1000



# Reading the data
twitter = twitter_reader(input_file_name)
twitter_data = twitter#[1240:1342]


# Format the data
tests = twitter_formatter(twitter_data)


# Get the commodity keywords
wheat_keywords, rice_keywords, maize_keywords, barley_keywords, soybean_keywords, grains_keywords = get_amis_topic_keywords()

          

# Extract relevant tweets and relative sentiment

tests = tweets_unicode(tests)
    

all_tweets = all_sentences_analyzer(tests)                  # 88582 tweets analyzed on 203774 tweets
all_tweets_sentiment = articles_sentiment(all_tweets)      # at the moment it seems not necessary, since tweets are usually one-sentence statements


commodity = ['wheat']
checkwords = commodity + wordslist(wheat_keywords)       
wheat_tweets = sentences_analyzer_twitter(tests, checkwords)



commodity = ['rice']
checkwords = commodity + wordslist(rice_keywords)                                
rice_tweets = sentences_analyzer_twitter(tests, checkwords)



commodity = ['soybeans']
checkwords = commodity + wordslist(soybean_keywords)       
soybeans_tweets = sentences_analyzer_twitter(tests, checkwords)



commodity = ['maize']
checkwords = commodity + wordslist(maize_keywords)          
maize_tweets = sentences_analyzer_twitter(tests, checkwords)



commodity = ['barley']
checkwords = commodity + wordslist(barley_keywords)          
barley_tweets = sentences_analyzer_twitter(tests, checkwords)



commodity = ['grains']
checkwords = commodity + wordslist(grains_keywords)          
grains_tweets = sentences_analyzer_twitter(tests, checkwords)



# Save the processed file
with open(all_tweets_output_file_name, 'w') as f:
     dump(all_tweets, f)
     f.write('\n')


with open(wheat_output_file_name, 'w') as f:
     dump(wheat_tweets, f)
     f.write('\n')
        

        
with open(rice_output_file_name, 'w') as f:
     dump(rice_tweets, f)
     f.write('\n')
        

       
with open(soybeans_output_file_name, 'w') as f:
     dump(soybeans_tweets, f)
     f.write('\n')
        

        
with open(maize_output_file_name, 'w') as f:
     dump(maize_tweets, f)
     f.write('\n')
     


with open(barley_output_file_name, 'w') as f:
     dump(barley_tweets, f)
     f.write('\n')
     


with open(grains_output_file_name, 'w') as f:
     dump(grains_tweets, f)
     f.write('\n')