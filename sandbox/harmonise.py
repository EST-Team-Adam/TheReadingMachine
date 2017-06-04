import pandas as pd
import feather
from thereadingmachine.process import read_jsonl

# Initialisation
file_prefix = "data/amis_articles"
version = '27_11_2016'
geo_tag_file_name = '{0}_{1}_geotagged_from_indexed.jsonl'.format(
    file_prefix, version)
commodity_tag_file_name = '{0}_{1}_commodity_tag.jsonl'.format(
    file_prefix, version)
topic_tag_file_name = '{0}_{1}_topic_clustered.csv'.format(
    file_prefix, version)
sentiment_file_name = '{0}_{1}_sentiment.jsonl'.format(
    file_prefix, version)
article_date_file_name = '{0}_{1}_article_date.jsonl'.format(
    file_prefix, version)
output_file_name = 'harmonised_data.feather'

geo_tag_json = read_jsonl(geo_tag_file_name)
normalised = [{'id': entry.get('id'), 'geo_tag': tag}
              for entry in geo_tag_json
              for tag in entry['geo_tag']]
geo_tag_data = pd.DataFrame(normalised)
commodity_tag_json = read_jsonl(commodity_tag_file_name)
commodity_tag_data = pd.DataFrame(commodity_tag_json)
topic_tag_data = pd.read_csv(topic_tag_file_name, index_col=False)
article_date_json = read_jsonl(article_date_file_name)
article_date_data = pd.DataFrame(article_date_json)
sentiment_data = pd.DataFrame(read_jsonl(sentiment_file_name))

input_data_list = [commodity_tag_data,
                   topic_tag_data, article_date_data, sentiment_data]
harmonised_data = reduce(lambda left, right: pd.merge(
    left, right, on='id'), input_data_list)


feather.write_dataframe(harmonised_data, output_file_name)
