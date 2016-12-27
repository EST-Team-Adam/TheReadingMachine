from __future__ import division
from thereadingmachine.keyword import get_amis_topic_keywords
from thereadingmachine.process import extract_geo
from thereadingmachine.process import extract_commodity
from thereadingmachine.process import extract_date

# Initialisation
file_prefix = "data/amis_articles"
version = '27_11_2016'
geo_input_file_name = '{0}_{1}_geotagged_from_indexed.jsonl'.format(
    file_prefix, version)
geo_output_file_name = '{0}_{1}_geo_tag.jsonl'.format(
    file_prefix, version)
commodity_input_file_name = '{0}_{1}_processed.jsonl'.format(
    file_prefix, version)
commodity_output_file_name = '{0}_{1}_commodity_tag.jsonl'.format(
    file_prefix, version)
date_input_file_name = '{0}_{1}_indexed.jsonl'.format(
    file_prefix, version)
date_output_file_name = '{0}_{1}_article_date.jsonl'.format(
    file_prefix, version)


wheat_keywords, rice_keywords, maize_keywords, barley_keywords, soybean_keywords, grains_keywords = get_amis_topic_keywords()

extract_geo(geo_input_file_name, geo_output_file_name)
extract_commodity(commodity_input_file_name,
                  commodity_output_file_name,
                  wheat_keywords=wheat_keywords,
                  rice_keywords=rice_keywords,
                  maize_keywords=maize_keywords,
                  soybean_keywords=soybean_keywords,
                  grain_keywords=grains_keywords)
extract_date(date_input_file_name, date_output_file_name)
