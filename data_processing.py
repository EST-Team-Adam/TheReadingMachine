from thereadingmachine.process import read_jsonl
from thereadingmachine.process import process_text
from json import dump

# Reading data
# --------------------------------------------------

# Initiate file names and parameters
file_prefix = "data/amis_articles"
version = '27_11_2016'
input_file_name = '{0}_{1}_indexed.jsonl'.format(file_prefix, version)
output_file_name = '{0}_{1}_processed.jsonl'.format(file_prefix, version)
test_sample_size = 1000

# Read the data
articles = read_jsonl(input_file_name)

# Processing
# --------------------------------------------------

# TODO (Michael): Check why lemmatization resulted in more words.
for article in articles:
    article['processed_article'] = process_text(article['article'])

# Save the processed file
# --------------------------------------------------
with open(output_file_name, 'w') as f:
    for article in articles:
        dump(article, f)
        f.write('\n')
