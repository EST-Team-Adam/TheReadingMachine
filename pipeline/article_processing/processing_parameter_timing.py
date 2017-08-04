import os
import time
import pandas as pd
import controller as ctr
from sqlalchemy import create_engine


# Configuration
n = 100
min_length = 30
data_dir = os.environ['DATA_DIR']
source_data_table = 'RawArticle'
target_data_table = 'ProcessedArticle'
summary_data_table = 'ProcessedArticleSummary'
engine = create_engine('sqlite:///{0}/the_reading_machine.db'.format(data_dir))
sql_query = 'SELECT * FROM {}'.format(source_data_table)
articles = pd.read_sql(sql_query, engine, parse_dates=['date'])
processed_articles = ctr.scraper_post_processing(articles)
processed_articles = processed_articles[processed_articles['source'].isin(
    ['agrimoney', 'euractiv'])]


def print_result(setting, duration):
    print('{} [Time in sec]: {:.2f} (sample), {:.2f} (total estimate)'.format(
        setting, duration, duration / n * processed_articles.shape[0]))


# Benchmark: no stemming and noun preserved
test_data = processed_articles[:n]
start = time.time()
ctr.text_preprocessing(article_df=test_data,
                       article_col='article',
                       min_length=min_length)
end = time.time()
duration = end - start
print_result('benchmark', duration)

# Stemming
start = time.time()
ctr.text_preprocessing(article_df=test_data,
                       article_col='article',
                       min_length=min_length, stem=True)
end = time.time()
duration = end - start
print_result('stem', duration)

# Noun removed
start = time.time()
ctr.text_preprocessing(article_df=test_data,
                       article_col='article',
                       min_length=min_length, stem=False,
                       remove_noun=True)
end = time.time()
duration = end - start
print_result('remove noun', duration)

# Stemming and noum removed
start = time.time()
ctr.text_preprocessing(article_df=test_data,
                       article_col='article',
                       min_length=min_length, stem=True,
                       remove_noun=True)
end = time.time()
duration = end - start
print_result('stem and remove noun', duration)
