import os
import sqlalchemy
import pandas as pd
from sqlalchemy import create_engine
from geotagging import read_countries
from geotagging import country_list_to_dict
from geotagging import geotag_article
from geotagging import flatten_geotagged_article

# Reading data
# --------------------------------------------------

data_dir = os.environ['DATA_DIR']
source_data_table = 'RawArticle'
engine = create_engine('sqlite:///{0}/the_reading_machine.db'.format(data_dir))
sql_query = 'SELECT * FROM {}'.format(source_data_table)
articles = pd.read_sql(sql_query, engine, parse_dates=['date'])
articles_dict = articles.to_dict(orient='records')


# Getting file of list of countries
file_countries = '{0}/list_of_countries.csv'.format(data_dir)
list_countries = read_countries(file_countries)
country_dict = country_list_to_dict(list_countries)

# Append country information to articles
geotagged_articles = geotag_article(
    articles=articles_dict, country_dict=country_dict)
flattened_article = flatten_geotagged_article(geotagged_articles)

# Save output file
target_data_table = 'GeoTaggedArticle'
field_type = {'id': sqlalchemy.types.Integer(),
              'geo_tag': sqlalchemy.types.NVARCHAR(length=255)}

flattened_article_df = pd.DataFrame(flattened_article)
flattened_article_df.to_sql(con=engine, name=target_data_table, index=False,
                            if_exists='replace',
                            dtype=field_type)
