import os
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from sklearn.linear_model import ElasticNetCV
import plotly.graph_objs as go
from plotly.offline import plot


data_dir = os.environ['DATA_DIR']
plot_output_dir = os.environ['WEBAPP_PLOT_DIR']
target_data_table = 'PriceForecast'
engine = create_engine('sqlite:///{0}/the_reading_machine.db'.format(data_dir))
harmonised_table = 'HarmonisedData'

# Model parameters
filter_coef = 1
sentiment_scale = 50
bootstrapIteration = 75
forecast_period = 180


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
    complete_topic_variable = [v + suffix
                               for v in topic_variables
                               for suffix in ['_pos', '_neg']]
    return complete_topic_variable


def transform_harmonised_data(data, forecast_period, topic_variables,
                              response_variable, all_price_variables,
                              filter_coef):
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
    transformed_data['response'] = (
        transformed_data[response_variable].shift(-forecast_period))
    other_price_variables = [v for v in all_price_variables
                             if v != response_variable]
    transformed_data.drop(other_price_variables, axis=1, inplace=True)

    # Perform cumsum, the implementation in R is more flexible where a
    # filter cefficient can be applied.

    for v in topic_variables:
        transformed_data[v] = transformed_data[v].cumsum()

    return transformed_data


def sum_sentiments(sentiments):
    ''' Sum up the sentiments according to the sign.
    '''
    pos_sentiment = sentiments[sentiments > 0].sum()
    neg_sentiment = sentiments[sentiments < 0].sum()
    return pos_sentiment, neg_sentiment


def create_model_data(response_variable, all_price_variables):
    # Get the input data
    topic_variables = get_topic_variables()
    harmonised_data = get_harmonised_data()
    model_data = (
        transform_harmonised_data(data=harmonised_data,
                                  forecast_period=forecast_period,
                                  topic_variables=topic_variables,
                                  filter_coef=filter_coef,
                                  response_variable=response_variable,
                                  all_price_variables=all_price_variables))
    return model_data


def estimate_sentiment_weights(model_data, response_variable):

    # Drop the dates, original price and NA's
    model_data = model_data.drop(['date', response_variable], axis=1).dropna()
    topic_variables = [v for v in model_data.columns if v != 'response']

    # Use bagged elasticnet to estimate the coefficients
    total_variable_count = len(topic_variables)
    sample_rate = 1 / (10.0 / total_variable_count)
    bagged_coefs = np.zeros((bootstrapIteration, total_variable_count))

    for i in range(bootstrapIteration):
        bagging_size = min([total_variable_count,
                            int(np.random.exponential(sample_rate) + 2)])
        bagging_variables = np.random.choice(topic_variables, bagging_size)
        model = ElasticNetCV(n_alphas=100, l1_ratio=1,
                             tol=1e-7, max_iter=100000, cv=10,
                             n_jobs=-1, normalize=True)

        model.fit(model_data[bagging_variables],
                  model_data['response'])
        coef_index = [topic_variables.index(bv) for bv in bagging_variables]
        bagged_coefs[i, coef_index] = model.coef_

    # Aggregate the bootstraped weights
    coefs = np.mean(bagged_coefs, axis=0)
    return coefs


def scale(x, scale):
    scaled_x = (x - min(x)) / (max(x) - min(x))
    return scaled_x * scale


def compute_market_sentiments(model_data, weights, date_col,
                              original_price_variable):
    topic_variables = get_topic_variables()
    inputs = np.array(model_data[topic_variables])
    outputs = (inputs * weights)
    p, n = zip(*[sum_sentiments(s) for s in outputs])
    # HACK (Michael): The negation makes the graph look reasonable,
    #                 but this is a major HACK that doesn't make
    #                 sense.
    scaled_p = scale(-pd.Series(p), sentiment_scale)
    scaled_n = -scale(-pd.Series(n), sentiment_scale)
    return pd.DataFrame(
        {'date': model_data[date_col],
         'price': model_data[original_price_variable],
         'positive_market_sentiment': scaled_p,
         'negative_market_sentiment': scaled_n,
         'commodity': original_price_variable.lower()})


def create_polygon(dates, price, sentiment):
    ''' Calculate the sequence of points for the polygon.
    '''
    x = pd.concat([dates, dates[::-1]])
    deviance = price + sentiment
    y = pd.concat([price, deviance[::-1]])
    return x, y


def create_sentiment_plot(sentiment_df, response_variable):
    ''' Creates a plotly html plot.
    '''

    pos_x, pos_y = create_polygon(sentiment_df['date'],
                                  sentiment_df['price'],
                                  sentiment_df['positive_market_sentiment'])

    neg_x, neg_y = create_polygon(sentiment_df['date'],
                                  sentiment_df['price'],
                                  sentiment_df['negative_market_sentiment'])
    price_series = go.Scatter(
        x=sentiment_df['date'],
        y=sentiment_df['price'],
        mode='lines',
        line=dict(
            color=('rgb(91, 146, 229)'),
            width=5),
        name='price'
    )

    positive_polygon = go.Scatter(
        x=pos_x,
        y=pos_y,
        mode='lines',
        line=dict(
            color=('rgb(0, 152, 0)'),
            width=0),
        fill='tozeroy',
        name='positive force'
    )

    negative_polygon = go.Scatter(
        x=neg_x,
        y=neg_y,
        mode='lines',
        line=dict(
            color=('rgb(152, 0, 0)'),
            width=0),
        fill='tozeroy',
        name='negative force'
    )

    plot_output = [positive_polygon, negative_polygon, price_series]
    out_file_name = '{}_market_sentiments.html'.format(
        response_variable.lower())
    plot(plot_output,
         filename=os.path.join(plot_output_dir, out_file_name),
         auto_open=True)
