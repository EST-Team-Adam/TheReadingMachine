from __future__ import division
import os
import pandas as pd
from sqlalchemy import create_engine


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
    topic_modelled_article = pd.read_sql(
        'SELECT * FROM NoposTopicModel', engine)
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


def harmonise_article(sentiment_col, id_col='id', date_col='date'):

    sentiment_scored_article = get_sentiment_scored_article()
    topic_modelled_article = get_topic_modelled_article()

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
    return harmonised_article
