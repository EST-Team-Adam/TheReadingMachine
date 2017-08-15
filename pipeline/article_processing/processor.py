import os
import pandas as pd
import controller as ctr
import sqlalchemy
from sqlalchemy import create_engine
from datetime import datetime

# Configuration
data_dir = os.environ['DATA_DIR']
source_data_table = 'RawArticle'
target_data_table = 'ProcessedArticle'
summary_data_table = 'ProcessedArticleSummary'
engine = create_engine('sqlite:///{0}/the_reading_machine.db'.format(data_dir))
sql_query = 'SELECT * FROM {}'.format(source_data_table)

# Initialise processing parameters
model_start_date = datetime(2010, 1, 1).date()
min_length = 30
remove_captalisation = True
remove_noun = False
remove_numerical = True
remove_punctuation = True
stem = False


# Reading data
articles = pd.read_sql(sql_query, engine, parse_dates=['date'])

# Post processing the data extraction
processed_articles = ctr.scraper_post_processing(
    articles, model_start_date=model_start_date)

# HACK (Michael): To test the model, I have taken only data from
#                 'agrimoney' and 'euractive' as they go beyond
#                 2010. This is required to learn the increase in
#                 price.
processed_articles = processed_articles[processed_articles['source'].isin(
    ['agrimoney', 'euractiv'])]

# Process the texts
preprocessed_text, text_summary = (
    ctr.text_preprocessing(article_df=processed_articles,
                           article_col='article',
                           min_length=min_length,
                           remove_captalisation=remove_captalisation,
                           remove_noun=remove_noun,
                           remove_numerical=remove_numerical,
                           remove_punctuation=remove_punctuation,
                           stem=stem))

# Save the data
data_field_type = {'id': sqlalchemy.types.Integer(),
                   'date': sqlalchemy.types.Date(),
                   'article': sqlalchemy.types.Text(),
                   'title': sqlalchemy.types.NVARCHAR(300),
                   'source': sqlalchemy.types.NVARCHAR(20),
                   'link': sqlalchemy.types.NVARCHAR(255)
                   }

summary_field_type = {'createTime': sqlalchemy.types.DateTime(),
                      'article_count': sqlalchemy.types.Integer(),
                      'average_article_length': sqlalchemy.types.Float(),
                      'average_lexical_diversity': sqlalchemy.types.Float(),
                      'vocab_size': sqlalchemy.types.Integer()
                      }

preprocessed_text.to_sql(con=engine,
                         name=target_data_table,
                         index=False,
                         if_exists='replace',
                         dtype=data_field_type)

text_summary.to_sql(con=engine,
                    name=summary_data_table,
                    index=False,
                    if_exists='append',
                    dtype=summary_field_type)
