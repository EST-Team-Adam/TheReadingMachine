from thereadingmachine.process import read_jsonl
from thereadingmachine.process import process_text
from json import dump
from time import strptime

# Reading data
# --------------------------------------------------

# Initiate file names and parameters
file_prefix = "data/amis_articles"
version = '27_07_2016'
input_file_name = '{0}_{1}.jsonl'.format(file_prefix, version)
output_file_name = '{0}_{1}_processed.jsonl'.format(file_prefix, version)
test_sample_size = 1000

# Read the data
articles = read_jsonl(input_file_name)

# Take a sample for testing
test_sample = articles[:test_sample_size]


# Processing
# --------------------------------------------------

# TODO (Michael): Check why lemmatization resulted in more words.
for article in test_sample:
    article['processed_article'] = process_text(article['article'])

# Sort the list and assign article ID.
#
# NOTE (Michael): The article is sorted from the oldest to the newest.
sorted_articles = sorted(articles, key=lambda k: strptime(
    k['date'], '%Y-%m-%d %H:%M:%S'))

# Assign article ID.
[article.update({'article_id': i})
 for i, article in enumerate(sorted_articles)]

# Save the processed file
# --------------------------------------------------
with open(output_file_name, 'w') as f:
    for article in sorted_articles:
        dump(article, f)
        f.write('\n')
