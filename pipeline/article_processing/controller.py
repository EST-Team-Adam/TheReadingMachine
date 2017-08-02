import os
from datetime import datetime

# Load and set some manipulation parameters
model_start_date = datetime.strptime(
    os.environ['MODEL_START_DATE'], '%Y-%m-%d').date()

maintenance_title = ['Reduced service at Agrimoney.com',
                     'Apology to Agrimoney.com subscribers']

irrelevant_link = ['https://www.euractiv.com/topics/news/?type_filter=video',
                   'http://www.euractiv.com/topics/news/?type_filter=video',
                   'http://www.euractiv.com/topics/news/?type_filter=news',
                   'http://www.euractiv.com/topics/news/?type_filter=all',
                   'https://www.euractiv.com/topics/news/?type_filter=all',
                   'https://www.euractiv.com/topics/news/',
                   'https://www.euractiv.com/topics/news/?type_filter=news',
                   'http://www.euractiv.com/topics/news/',
                   'https://www.euractiv.com/news/',
                   'http://www.euractiv.com/news/']


def process_articles(raw_articles):

    # Remove the original id and drop duplciates
    processed_articles = (raw_articles
                          .drop('id', 1)
                          .drop_duplicates(subset='article'))

    # Remvoe entries that are associated with maintenance or service.
    processed_articles = processed_articles[~processed_articles['title'].isin(
        maintenance_title)]

    # Remoe links that are not associated with news articles.
    processed_articles = processed_articles[~processed_articles['link'].isin(
        irrelevant_link)]

    # Subset the data only after the model_start_date
    processed_articles = processed_articles[processed_articles['date']
                                            > model_start_date]

    # Recreate the index
    processed_articles.sort_values(['date'], ascending=[1], inplace=True)
    processed_articles['id'] = range(1, processed_articles.shape[0] + 1)

    return processed_articles
