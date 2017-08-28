import os
import sqlalchemy
import pandas as pd
from sqlalchemy import create_engine
import controller as ctr

# Configuration
data_dir = os.environ['DATA_DIR']
source_data_table = 'ProcessedArticle'
target_data_table = 'SentimentScoredArticle'
engine = create_engine('sqlite:///{0}/the_reading_machine.db'.format(data_dir))
sql_query = 'SELECT * FROM {}'.format(source_data_table)


# Read the data
articles = pd.read_sql(sql_query, engine, parse_dates=['date'])
articles_list = articles.to_dict(orient='records')

# Score the articles
scored_articles = ctr.article_sentiment_scoring(
    articles=articles_list, article_col='article', id_col='id',
    date_col='date', method=['VADER', 'GOOGLE_NLP'], to_df=True)

# Save output file
field_type = {'id': sqlalchemy.types.Integer(),
              'date': sqlalchemy.types.Date(),
              'compound_sentiment': sqlalchemy.types.Float(),
              'negative_sentiment': sqlalchemy.types.Float(),
              'neutral_sentiment': sqlalchemy.types.Float(),
              'positive_sentiment': sqlalchemy.types.Float()
              }

scored_articles.to_sql(con=engine, name=target_data_table, index=False,
                       if_exists='replace', dtype=field_type)
