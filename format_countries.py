from thereadingmachine.geotagging import make_dict_countries
from thereadingmachine.geotagging import check_countries
from thereadingmachine.geotagging import read_countries
from thereadingmachine.process import read_jsonl
import sys, re
from json import dump
from collections import defaultdict


# Reading data
# --------------------------------------------------

# Initiate file names and parameters
file_prefix = "data/amis_articles"
version = '27_11_2016'
input_file_name = '{0}_{1}_indexed.jsonl'.format(file_prefix, version)
output_file_name = '{0}_{1}_geotagged_from_indexed.jsonl'.format(file_prefix, version)
## For MK: if you need to run it after your processing run the two commands commented instead
#input_file_name = '{0}_{1}_processed.jsonl'.format(file_prefix, version)
#output_file_name = '{0}_{1}_geotagged_from_processed.jsonl'.format(file_prefix, version)
test_sample_size = 1000
# Getting file of list of countries 
file_countries = "data/list_of_countries.csv"

# Read the data
articles = read_jsonl(input_file_name)
list_countries = read_countries(file_countries)

## Create dictionary of countries
d_countries = defaultdict(list)
[make_dict_countries(l, d_countries) for l in list_countries]

for article in articles:
    article.update({'geo_tag': check_countries(article['article'], d_countries)})

# Save the processed file
# --------------------------------------------------
with open(output_file_name, 'w') as f:
    for article in articles:
        dump(article, f)
        f.write('\n')


