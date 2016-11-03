import json
from thereadingmachine.process import process_text


# Reading data
# --------------------------------------------------

# Initiate file names and parameters
file_prefix = "data/amis_articles"
version = '27_07_2016'
input_file_name = '{0}_{1}.jsonl'.format(file_prefix, version)
output_file_name = '{0}_{1}_processed.jsonl'.format(file_prefix, version)
test_sample_size = 1000

# Read the data
print "Reading data from '{0}' ...".format(input_file_name)
articles = []
with open(input_file_name) as f:
    for line in f:
        articles.append(json.loads(line))

# Take a sample for testing
test_sample = articles[:test_sample_size]


# Processing
# --------------------------------------------------

# TODO (Michael): Check why lemmatization resulted in more words.
for article in test_sample:
    article['processed_article'] = process_text(article['article'])

# Save the processed file
# --------------------------------------------------
with open(output_file_name, 'w') as f:
    for article in test_sample:
        json.dump(article, f)
        f.write('\n')
