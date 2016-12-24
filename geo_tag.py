import json
from thereadingmachine.process import read_jsonl

# Initialisation
file_prefix = "data/amis_articles"
version = '27_11_2016'
input_file_name = '{0}_{1}_geotagged_from_indexed.jsonl'.format(
    file_prefix, version)
output_file_name = '{0}_{1}_geo_tag.jsonl'.format(file_prefix, version)

test = read_jsonl(input_file_name, size=100)

with open(input_file_name) as fi, open(output_file_name, 'w') as fo:
    for line in fi:
        geo_tagged = json.loads(line)
        geo_dict = {'id': geo_tagged['id'],
                    'geo_tag': geo_tagged['geo_tag']}
        json.dump(geo_dict, fo)
        fo.write('\n')


# import pandas as pd
# check = read_jsonl(output_file_name)
# normalised = [{'id': entry.get('id'), 'geo_tag': tag}
#               for entry in check
#               for tag in entry['geo_tag']]

# geo_tag_data = pd.DataFrame(normalised)
