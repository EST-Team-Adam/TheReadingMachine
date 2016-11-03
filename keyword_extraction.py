import json
from thereadingmachine.keyword import get_topic_keywords
from thereadingmachine.keyword import extract_text_keywords

# Initialisation
file_prefix = "data/amis_articles"
version = '27_07_2016'
input_file_name = '{0}_{1}_processed.jsonl'.format(file_prefix, version)
test_sample_size = 1000

# Read the data
print "Reading data from '{0}' ...".format(input_file_name)
articles = []
with open(input_file_name) as f:
    for line in f:
        articles.append(json.loads(line))

# Take a sample for testing
test_sample = articles[:test_sample_size]


# Keyword Extraction
# --------------------------------------------------

# Pre define the topics
topics = ['wheat', 'rice', 'maize', 'soybean',
          'produce', 'trade', 'government', 'finance']

# Extract keywords
for article in test_sample:
    for topic in topics:
        article["{0}_keyword".format(topic).decode('UTF-8')] = \
            extract_text_keywords(article['processed_article'], topic)

# Subset articles that are related to wheat
wheat_articles = [article
                  for article in test_sample
                  if len(article['wheat_keyword']) > 0]
