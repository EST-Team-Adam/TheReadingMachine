from thereadingmachine.process import read_jsonl
from thereadingmachine.SBD import SBD
from thereadingmachine.sentence_tagger import Topic_Extractor  # to be eliminated from here
from json import dump


# Initiate file names and parameters
file_prefix = "data/amis_articles"
version = '27_11_2016'
input_file_name = '{0}_{1}_indexed.jsonl'.format(file_prefix, version)
output_file_name = '{0}_{1}_sentences_from_indexed.jsonl'.format(file_prefix, version)

# Functions
def main(sentence):
    topic_extractor = Topic_Extractor(sentence)
    result = topic_extractor.extract()
    results.append(result)
    return results
    

def sentence_by_sentence(article_sentences):
    for sentence in article_sentences:
        if __name__ == '__main__':
            result_article = main(sentence)
            results_article.append(result_article)
    return results_article



# Introduction (for paper purposes only)
#sentence = "Wheat market is showing a positive trend: trained by last year good American production, wheat price arose more than prices of rice and soybeans."
#results = list()
#results = main(sentence) 

# Read the data
articles = read_jsonl(input_file_name)

# Test Article
tests = articles

# Extract Topics
for test in tests:
  article_sentences = SBD(test)
  result_article = list()
  results_article = list()
  results = list()
  results_article = sentence_by_sentence(article_sentences)
  dict = {}
  for i in range(len(article_sentences)):
     dict[article_sentences[i]] = results[i]
     #dict[results[i]] = article_sentences[i]     # maybe it's better to switch keys and values
     test['sentences'] = dict


# Save the processed file
with open(output_file_name, 'w') as f:
    for test in tests:
        dump(test, f)
        f.write('\n')