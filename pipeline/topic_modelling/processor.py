import os
import pandas as pd
import controller as ctr
from sqlalchemy import create_engine

# Configuration
data_dir = os.environ['DATA_DIR']
data_source_table = 'RawArticle'
data_target_table = 'TopicModel'
engine = create_engine('sqlite:///{0}/the_reading_machine.db'.format(data_dir))
sql_query = 'SELECT * FROM {}'.format(data_source_table)

# Reading data
articles = pd.read_sql(sql_query, engine, parse_dates=['date'])

# Model article topics
model = ctr.model_article_topic(articles)

# Save the data back to the database
model.nmf_documents_topics.to_sql(con=engine, name=data_target_table,
                                  if_exists='replace',
                                  index=False)
