import os
import pandas as pd
from sqlalchemy import create_engine


# def read_data_inputs(source_data_table, engine, id_field):
#     table_list = list()
#     for current_table in source_data_table:
#         sql_query = 'SELECT * FROM {}'.format(current_table)
#         table_list.append(pd.read_sql(sql_query, engine))
#     table_list.append(get_raw_article_with_dates())
#     merged_table = reduce(lambda x, y: pd.merge(x, y, on=id_field), table_list)
#     return merged_table


# def get_raw_article_with_dates():
#     data_dir = os.environ['DATA_DIR']
#     engine = create_engine(
#         'sqlite:///{0}/the_reading_machine.db'.format(data_dir))
#     dated_article = pd.read_sql('SELECT id, date FROM RawArticle', engine)
#     return dated_article


def get_sentiment_scored_article():
    data_dir = os.environ['DATA_DIR']
    engine = create_engine(
        'sqlite:///{0}/the_reading_machine.db'.format(data_dir))
    sentiment_scored_article = pd.read_sql(
        'SELECT * FROM SentimentScoredArticle', engine)
    return sentiment_scored_article


def get_topic_modelled_article():
    data_dir = os.environ['DATA_DIR']
    engine = create_engine(
        'sqlite:///{0}/the_reading_machine.db'.format(data_dir))
    topic_modelled_article = pd.read_sql('SELECT * FROM TopicModel', engine)
    return topic_modelled_article


def get_commodity_tagged_article():
    data_dir = os.environ['DATA_DIR']
    engine = create_engine(
        'sqlite:///{0}/the_reading_machine.db'.format(data_dir))
    commodity_tagged_article = pd.read_sql(
        'SELECT * FROM CommodityTaggedArticle', engine)
    return commodity_tagged_article


def harmonise_article():

    sentiment_scored_article = get_sentiment_scored_article()
    topic_modelled_article = get_topic_modelled_article()
    commodity_tagged_article = get_commodity_tagged_article()

    processed_article_list = [sentiment_scored_article, topic_modelled_article,
                              commodity_tagged_article]

    harmonised_article = reduce(lambda dfx, dfy: pd.merge(dfx, dfy, on='id', how='inner'),
                                processed_article_list)
    return harmonised_article
