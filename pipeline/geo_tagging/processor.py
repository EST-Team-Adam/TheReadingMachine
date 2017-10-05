import os
import sqlalchemy
import pandas as pd
from sqlalchemy import create_engine
import controller as ctr

# Configuration
data_dir = os.environ['DATA_DIR']
source_data_table = 'ProcessedArticle'
target_data_table = 'GeoTaggedArticle'
engine = create_engine('sqlite:///{0}/the_reading_machine.db'.format(data_dir))
sql_query = 'SELECT * FROM {}'.format(source_data_table)
country_file = '{0}/list_of_countries.csv'.format(data_dir)

# Read the data
articles = pd.read_sql(sql_query, engine, parse_dates=['date'])
articles_dict = articles.to_dict(orient='records')


# Read country list
country_list = ctr.read_countries(country_file)
country_dict = ctr.country_list_to_dict(country_list)

# Geotag articles
geotagged_articles = ctr.geotag_article(
    articles=articles_dict, country_dict=country_dict)


# Save output file
field_type = {'id': sqlalchemy.types.Integer(),
              'geo_tag': sqlalchemy.types.NVARCHAR(length=255)}
flattened_article_df = pd.DataFrame(geotagged_articles)
flattened_article_df.to_sql(con=engine, name=target_data_table, index=False,
                            if_exists='replace',
                            dtype=field_type)
