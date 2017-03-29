import json
from thereadingmachine.process import read_jsonl
from thereadingmachine.process import index_article

# Initiate file names and parameters
file_prefix = "data/amis_articles"
version = '27_11_2016'
input_file_name = '{0}_{1}.jsonl'.format(file_prefix, version)
output_file_name = '{0}_{1}_indexed.jsonl'.format(file_prefix, version)


raw_data = read_jsonl(input_file_name)
indexed_data = index_article(raw_data)


# Save indexed file
with open(output_file_name, 'w') as f:
    for entry in indexed_data:
        json.dump(entry, f)
        f.write('\n')
