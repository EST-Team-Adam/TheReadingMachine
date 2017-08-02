import os
import pandas as pd
import controller as ctr
import sqlalchemy
from sqlalchemy import create_engine


# Configuration
data_dir = os.environ['DATA_DIR']
source_data_table = 'RawArticle'
target_data_table = 'ProcessedArticle'
engine = create_engine('sqlite:///{0}/the_reading_machine.db'.format(data_dir))
sql_query = 'SELECT * FROM {}'.format(source_data_table)

# Reading data
articles = pd.read_sql(sql_query, engine, parse_dates=['date'])

# Process the articles
processed_articles = ctr.process_articles(articles)


# Save back to database
field_type = {'id': sqlalchemy.types.Integer(),
              'date': sqlalchemy.types.Date(),
              'article': sqlalchemy.types.Text(),
              'title': sqlalchemy.types.NVARCHAR(300),
              'source': sqlalchemy.types.NVARCHAR(20),
              'link': sqlalchemy.types.NVARCHAR(255)
              }


# Save the data
processed_articles.to_sql(con=engine,
                          name=target_data_table,
                          index=False,
                          if_exists='replace',
                          dtype=field_type)
