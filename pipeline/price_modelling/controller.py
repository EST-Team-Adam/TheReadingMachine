from __future__ import division
import os
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from datetime import timedelta
from sklearn.linear_model import ElasticNetCV
from statsmodels.nonparametric.smoothers_lowess import lowess


data_dir = os.environ['DATA_DIR']
engine = create_engine(
    'sqlite:///{0}/the_reading_machine.db'.format(data_dir))
harmonised_table = 'HarmonisedData'


def get_igc_price(response=None):
    ''' Function to load the IGC price data.
    '''

    sentiment_scored_article = pd.read_sql(
        'SELECT * FROM PriceIGC', engine, parse_dates=['date'])
    if response:
        sentiment_scored_article = sentiment_scored_article[['date', response]]
    return sentiment_scored_article


def get_harmonised_data():
    ''' Function to load the harmonised data.
    '''

    harmonised_data = pd.read_sql(
        'SELECT * FROM {}'.format(harmonised_table), engine,
        parse_dates=['date'])
    return harmonised_data


def get_topic_variables():
    ''' Function to get all the names of the topic model.
    '''

    topic_variables = (
        pd.read_sql('PRAGMA table_info(TopicModel)', engine)['name']
        .where(lambda x: x != 'id')
        .dropna()
        .tolist())
    cmoplete_topic_variable = [v + suffix
                               for v in topic_variables
                               for suffix in ['_pos', '_neg']]
    return cmoplete_topic_variable


def transform_harmonised_data(data, forecast_period, topic_variables,
                              response_variable, filter_coef):
    '''Function to transform the harmonised data for modeling.

    The following transformation are performed:

    1. Remove commodity tag (this is a temporary hack)
    2. Create the response by shifting the price time serie.
    3. Perform filtering.

    '''
    non_commodity_tag_columns = [i
                                 for i in data.columns
                                 if 'contain' not in i]
    transformed_data = data.copy()[non_commodity_tag_columns]
    transformed_data[response_variable] = (
        transformed_data['GOI'].shift(-forecast_period))

    # Perform cumsum, the implementation in R is more flexible where a
    # filter cefficient can be applied.

    for v in topic_variables:
        transformed_data[v] = transformed_data[v].cumsum()

    return transformed_data


def build_datasets(complete_data, forecast_period, holdout_period,
                   response_variable):
    ''' Function to split the complete data into train, test, and prediction data.
    '''

    prediction_data = complete_data[complete_data[response_variable].isnull()]
    model_data = complete_data[~complete_data[response_variable].isnull()]
    train_data = model_data.iloc[1:-(holdout_period - 1)]
    test_data = model_data.iloc[-(holdout_period):]
    cutoff_date = train_data['date'].max() + timedelta(days=forecast_period)
    return prediction_data, train_data, test_data, cutoff_date


def train_bag_elasticnet(complete_data, forecast_period, holdout_period,
                         bootstrapIteration, topic_variables,
                         response_variable, date_col='date'):
    '''Function to bag and train the Elastic net iwth cross-validation
    error as weight.

    '''

    prediction_data, train_data, test_data, cutoff_date = (
        build_datasets(complete_data=complete_data,
                       forecast_period=forecast_period,
                       holdout_period=holdout_period,
                       response_variable=response_variable))

    observation_length = complete_data.shape[0]
    total_variable_count = len(topic_variables)
    predictions = np.zeros(shape=(observation_length, bootstrapIteration))
    cv_min = np.zeros(bootstrapIteration)
    # This is the of the implementation in R due to the specification of Python
    sample_rate = 1 / (10 / total_variable_count)

    for i in range(bootstrapIteration):
        bagging_size = min([total_variable_count,
                            int(np.random.exponential(sample_rate) + 2)])
        bagging_variables = np.random.choice(topic_variables, bagging_size)
        model = ElasticNetCV(n_alphas=100, l1_ratio=1,
                             tol=1e-7, max_iter=100000, cv=10,
                             n_jobs=-1)

        model.fit(train_data[bagging_variables],
                  train_data[response_variable])

        predictions[:, i] = model.predict(complete_data[bagging_variables])
        cv_min[i] = model.alpha_

    bagging_weights = (1 / cv_min) / (1 / cv_min).sum()
    weighted_prediction = np.matmul(predictions, bagging_weights)

    smoothed_prediction = lowess(weighted_prediction,
                                 range(observation_length),
                                 return_sorted=False,
                                 frac=forecast_period / observation_length)
    prediction_df = pd.DataFrame(
        {'date': complete_data[date_col] + timedelta(days=forecast_period),
         'prediction': smoothed_prediction,
         'forecastPeriod': forecast_period})

    return prediction_df


# TODO (Michael):
#
# 1. Check the lowess implementation
#
# 2. Add weighted coefficients as in the R implementation.
