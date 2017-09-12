import os
import pandas as pd
import controller as ctr
import sqlalchemy
from sqlalchemy import create_engine

# Configuration
data_dir = os.environ['DATA_DIR']
source_data_table = 'ProcessedArticle'
target_data_table = 'CommodityTaggedArticle'
engine = create_engine('sqlite:///{0}/the_reading_machine.db'.format(data_dir))
sql_query = 'SELECT * FROM {}'.format(source_data_table)

# Reading data
articles = pd.read_sql(sql_query, engine, parse_dates=['date'])
articles_list = articles.to_dict(orient='record')


# Tag commodity
commodity_tagged_articles = ctr.commodity_tag_article(articles=articles_list,
                                                      article_field='article',
                                                      id_field='id')

# Save back to database
field_type = {'id': sqlalchemy.types.Integer(),
              'containGrain': sqlalchemy.types.Boolean(),
              'containMaize': sqlalchemy.types.Boolean(),
              'containRice': sqlalchemy.types.Boolean(),
              'containSoybean': sqlalchemy.types.Boolean(),
              'containWheat': sqlalchemy.types.Boolean()
              }
commodity_tagged_articles_df = pd.DataFrame(commodity_tagged_articles)
commodity_tagged_articles_df.to_sql(con=engine,
                                    name=target_data_table,
                                    index=False,
                                    if_exists='replace',
                                    dtype=field_type)
