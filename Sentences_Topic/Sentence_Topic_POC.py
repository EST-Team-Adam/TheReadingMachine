from thereadingmachine.process import read_jsonl
from thereadingmachine.SBD import SBD
from thereadingmachine.article_keywords import article_keywords
from thereadingmachine.sentiment_VADER import VADER
from thereadingmachine.sentiment_GoogleNLP import GoogleNLP
from json import dump


# Initiate file names and parameters
file_prefix = "data/amis_articles"
version = '27_11_2016'
input_file_name = '{0}_{1}_indexed.jsonl'.format(file_prefix, version)
output_file_name = '{0}_{1}_sentences_from_indexed.jsonl'.format(file_prefix, version)


# Read the data
articles = read_jsonl(input_file_name)


# Test Article
tests = articles#[0:100]#[98345:98347]


# Extract Topics and Sentiment
for test in tests:
  article_sentences = SBD(test)
  results_article = article_keywords(article_sentences)
  sentiment_VADER = VADER(article_sentences)
  #sentiment_Google = GoogleNLP(article_sentences)
  dict = {}
  for i in range(len(article_sentences)):
     #dict[article_sentences[i]] = [results_article[i], sentiment_VADER[i], sentiment_Google[i]]
     dict[repr(results_article[i])] = [article_sentences[i], sentiment_VADER[i]]#, sentiment_Google[i]]
     test['sentences'] = dict


# Save the processed file
with open(output_file_name, 'w') as f:
    for test in tests:
        dump(test, f)
        f.write('\n')
