import os
import sqlalchemy
import pandas as pd
from sqlalchemy import create_engine
from thereadingmachine.sentence_selector import all_sentences_analyzer
from thereadingmachine.sentence_selector import articles_sentiment

# Configuration
data_dir = os.environ['DATA_DIR']
source_data_table = 'RawArticle'
target_data_table = 'SentimentScoredArticle'
engine = create_engine('sqlite:///{0}/the_reading_machine.db'.format(data_dir))
sql_query = 'SELECT * FROM {}'.format(source_data_table)


# Read the data
articles = pd.read_sql(sql_query, engine, parse_dates=['date'])
articles_dict = articles.to_dict(orient='records')

# Score the articles
scored_sentences = all_sentences_analyzer(articles_dict)
scored_articles = articles_sentiment(scored_sentences)

# Save output file
field_type = {'id': sqlalchemy.types.Integer(),
              'date': sqlalchemy.types.Date(),
              'compound_sentiment': sqlalchemy.types.Float(),
              'negative_sentiment': sqlalchemy.types.Float(),
              'neutral_sentiment': sqlalchemy.types.Float(),
              'positive_sentiment': sqlalchemy.types.Float()
              }

flattened_article_df = pd.DataFrame(scored_articles)
flattened_article_df.to_sql(con=engine, name=target_data_table, index=False,
                            if_exists='replace', dtype=field_type)
