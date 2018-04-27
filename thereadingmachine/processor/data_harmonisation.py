from __future__ import division
import pandas as pd
import thereadingmachine.environment as env
import thereadingmachine.parameter as param
import thereadingmachine.utils.io as io


def compute_topic_score(pos_sentiment_col, neg_sentiment_col, topic,
                        id_col='id'):
    original_id = topic[id_col]
    pos_scored_topic = topic.drop(id_col, axis=1).apply(
        lambda x: x * pos_sentiment_col)
    new_pos_names = {n: n + '_pos'
                     for n in topic.columns}
    pos_scored_topic.rename(columns=new_pos_names, inplace=True)
    neg_scored_topic = topic.drop(id_col, axis=1).apply(
        lambda x: x * -neg_sentiment_col)
    new_neg_names = {n: n + '_neg'
                     for n in topic.columns}
    neg_scored_topic.rename(columns=new_neg_names, inplace=True)
    scored_topic = pd.concat([pos_scored_topic, neg_scored_topic], axis=1)

    # TODO (Michael): Need to think how to normalise.
    scored_topic[id_col] = original_id
    return scored_topic


def harmonise_article(pos_sentiment_col='positive_sentiment',
                      neg_sentiment_col='negative_sentiment',
                      id_col='id', date_col='date'):

    sentiment_scored_article = io.read_table(env.sentiment_scored_table)
    topic_modelled_article = io.read_table(env.topic_model_table, dates=False)
    igc_price = io.read_table(env.price_table)

    article_max_date = sentiment_scored_article[date_col].max()
    model_price = igc_price[(igc_price[date_col] >= param.model_start_date) &
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

    scored_topic = compute_topic_score(
        pos_sentiment_col=sentiment_scored_article[pos_sentiment_col],
        neg_sentiment_col=sentiment_scored_article[neg_sentiment_col],
        topic=topic_modelled_article, id_col=id_col)

    processed_article_list = [scored_topic]

    harmonised_article = reduce(lambda dfx, dfy:
                                pd.merge(dfx, dfy, on='id', how='inner'),
                                processed_article_list)
    harmonised_article[date_col] = sentiment_scored_article[date_col]

    # Perform aggregation
    aggregated_article = (harmonised_article
                          .drop('id', axis=1)
                          .groupby('date')
                          .mean()
                          .apply(lambda x: (x - x.mean()) / x.std(), axis=0)
                          .reset_index())

    # NOTE (Michael): dates without sentiments and topic are filled
    #                 with NA assuming there are no information
    #                 available.
    harmonised_data = (pd.merge(model_price, aggregated_article,
                                on='date', how='left')
                       .fillna(0))

    return harmonised_data
