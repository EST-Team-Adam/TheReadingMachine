from __future__ import division
import os
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from datetime import datetime
from datetime import timedelta

# NOTE (Michael): We will use the no pos table for now.
topicModelTable = 'NoposTopicModel'
model_start_date = datetime(2010, 1, 1).date()


def get_igc_price(response=None):
    data_dir = os.environ['DATA_DIR']
    engine = create_engine(
        'sqlite:///{0}/the_reading_machine.db'.format(data_dir))
    sentiment_scored_article = pd.read_sql(
        'SELECT * FROM PriceIGC', engine, parse_dates=['date'])
    if response:
        sentiment_scored_article = sentiment_scored_article[['date', response]]
    return sentiment_scored_article


def get_sentiment_scored_article():
    data_dir = os.environ['DATA_DIR']
    engine = create_engine(
        'sqlite:///{0}/the_reading_machine.db'.format(data_dir))
    sentiment_scored_article = pd.read_sql(
        'SELECT * FROM SentimentScoredArticle', engine,
        parse_dates=['date'])
    return sentiment_scored_article


def get_topic_modelled_article():
    data_dir = os.environ['DATA_DIR']
    engine = create_engine(
        'sqlite:///{0}/the_reading_machine.db'.format(data_dir))
    topic_modelled_article = pd.read_sql(
        'SELECT * FROM {}'.format(topicModelTable), engine)

    # Rename the columns
    #
    # NOTE (Michael): This step should be performed in TopicModel.
    new_names = {n: n.replace(' ', '_')
                 for n in topic_modelled_article.columns}
    topic_modelled_article.rename(columns=new_names, inplace=True)

    return topic_modelled_article


def get_commodity_tagged_article():
    data_dir = os.environ['DATA_DIR']
    engine = create_engine(
        'sqlite:///{0}/the_reading_machine.db'.format(data_dir))
    commodity_tagged_article = pd.read_sql(
        'SELECT * FROM CommodityTaggedArticle', engine)
    return commodity_tagged_article


def compute_topic_score(sentiment, topic, id_col='id'):
    original_id = topic[id_col]
    scored_topic = topic.drop(id_col, axis=1).apply(lambda x: x * sentiment)
    # TODO (Michael): Need to think how to normalise.
    scored_topic[id_col] = original_id
    return scored_topic


def harmonise_article(sentiment_col='compound_sentiment',
                      id_col='id', date_col='date'):

    sentiment_scored_article = get_sentiment_scored_article()
    topic_modelled_article = get_topic_modelled_article()
    igc_price = get_igc_price(response='GOI')

    article_max_date = sentiment_scored_article[date_col].max()
    model_price = igc_price[(igc_price[date_col] >= model_start_date) &
                            (igc_price[date_col] <= article_max_date)]

    # HACK (Michael): There is an increase trend in the size of the
    #                 value in the topic. In order to eliminate this
    #                 effect, we will scale the topic by row. That is,
    #                 the topic are now in relative importance to each
    #                 topic.
    #
    #                 This is a hack mainly because the increasing
    #                 trend is an artifact of the increased data
    #                 sample.
    #
    #                 The na is filled with 0. The reason why there
    #                 are missing value is because there may be a
    #                 single day without any relevant article and thus
    #                 the sum is 0. Since the division of 0 is NaN we
    #                 replace it with 0.

    scaled_topic = (topic_modelled_article.drop(id_col, axis=1)
                    .apply(lambda x: x / sum(x), axis=1)
                    .fillna(0))
    scaled_topic[id_col] = topic_modelled_article[id_col]
    commodity_tagged_article = get_commodity_tagged_article()
    scored_topic = compute_topic_score(
        sentiment_scored_article[sentiment_col], scaled_topic,
        id_col)

    processed_article_list = [scored_topic, commodity_tagged_article]

    harmonised_article = reduce(lambda dfx, dfy:
                                pd.merge(dfx, dfy, on='id', how='inner'),
                                processed_article_list)
    harmonised_article[date_col] = sentiment_scored_article[date_col]

    # Perform aggregation
    aggregated_article = (harmonised_article
                          .drop('id', axis=1)
                          .groupby('date')
                          .mean()
                          .reset_index())

    # NOTE (Michael): dates without sentiments and topic are filled
    #                 with NA assuming there are no information
    #                 available.
    harmonised_data = (pd.merge(model_price, aggregated_article,
                                on='date', how='left')
                       .fillna(0))

    return harmonised_data
