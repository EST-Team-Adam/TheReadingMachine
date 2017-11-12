import os
import pandas as pd
from sqlalchemy import create_engine
from datetime import datetime
from datetime import timedelta
from sklearn import preprocessing
from nltk.tokenize import RegexpTokenizer
import string
from nltk import pos_tag
from nltk.stem import SnowballStemmer
from nltk.corpus import stopwords


# Configurations
topicModelTable = 'TopicModel'
model_start_date = datetime(2010, 1, 1).date()
data_dir = os.environ['DATA_DIR']
engine = create_engine(
    'sqlite:///{0}/the_reading_machine.db'.format(data_dir))

# Global parameters
forecast_period = 90
holdout_period = 180
response_variable = 'response'


# Model parameters
feature_size = 100
timestep_size = 90
batch_size = 90
num_layer = 2
cell_size = 128
learning_rate = 0.0001
epochs = 300
keep_prob = 0.75
clipping_cap = 1.0

# This is because the model needs timestep and forecast period ahead
# data to make the first forecast.
rnn_start_date = model_start_date - \
    timedelta(days=timestep_size + forecast_period)


def get_igc_price(response=None):
    ''' Function to load the IGC price data.
    '''

    igc_price = pd.read_sql(
        'SELECT * FROM PriceIGC', engine, parse_dates=['date'])
    if response:
        igc_price = igc_price[['date', response]]
    return igc_price


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
    sclae_input = topic_modelled_article.drop('id', axis=1)
    scaled_topic = pd.DataFrame(preprocessing.scale(sclae_input),
                                columns=sclae_input.columns)
    scaled_topic['id'] = topic_modelled_article['id']

    return scaled_topic


def get_commodity_tagged_article():
    data_dir = os.environ['DATA_DIR']
    engine = create_engine(
        'sqlite:///{0}/the_reading_machine.db'.format(data_dir))
    commodity_tagged_article = pd.read_sql(
        'SELECT * FROM CommodityTaggedArticle', engine)
    return commodity_tagged_article


def compute_topic_score(pos_sentiment_col, neg_sentiment_col, topic,
                        id_col='id'):
    original_id = topic[id_col]
    compound_sentiment = preprocessing.scale(
        pos_sentiment_col - neg_sentiment_col)
    scored_topic = topic.drop(id_col, axis=1).apply(
        lambda x: x * compound_sentiment)

    scored_topic[id_col] = original_id
    return scored_topic


def harmonise_article(pos_sentiment_col='positive_sentiment',
                      neg_sentiment_col='negative_sentiment',
                      id_col='id', date_col='date'):
    '''The function harmonised the various data sources and return a
    hamonised dataset for modeling.

    '''
    sentiment_scored_article = get_sentiment_scored_article()
    topic_modelled_article = get_topic_modelled_article()
    igc_price = get_igc_price(response='GOI')

    article_max_date = sentiment_scored_article[date_col].max()
    model_price = igc_price[(igc_price[date_col] >= rnn_start_date) &
                            (igc_price[date_col] <= article_max_date)]

    # commodity_tagged_article = get_commodity_tagged_article()
    scored_topic = compute_topic_score(
        pos_sentiment_col=sentiment_scored_article[pos_sentiment_col],
        neg_sentiment_col=sentiment_scored_article[neg_sentiment_col],
        topic=topic_modelled_article, id_col=id_col)
    scored_topic[date_col] = sentiment_scored_article[date_col]

    # Perform aggregation
    aggregated_article = (scored_topic
                          .drop('id', axis=1)
                          .groupby(date_col)
                          .mean()
                          .apply(lambda x: x / x.abs().max(), axis=0)
                          )
    aggregated_article[date_col] = aggregated_article.index

    # NOTE (Michael): dates without sentiments and topic are filled
    #                 with 0 assuming there are no information
    #                 available.
    harmonised_data = (pd.merge(model_price, aggregated_article,
                                on=date_col, how='left')
                       .fillna(0))

    return harmonised_data


def text_processor(text, remove_captalisation=True, remove_noun=False,
                   remove_numerical=True, remove_punctuation=True,
                   stem=False, tokenizer=None):
    '''The function process the texts with the intention for topic
    modelling.

    The following steps are performed:
    1. Tokenise
    2. Prune words
    3. Removal of stopwords

    Details:

    The regular expression tokeniser is used as we are interested just
    on the key words, punctuation is irrelevant. Numerical and
    captalisation removal can be specified as a parameter. Stop words
    and certain manually coded phrases are also removed.

    NOTE(Michael): The remove_noun is currently inactive. Further
                    investigation is required for the implementation.

    '''

    # Tokenize
    if tokenizer is None:
        tokenizer = RegexpTokenizer(r'\w+')
        tokenized_text = tokenizer.tokenize(text)
    else:
        tokenized_text = tokenizer(text)

    if remove_punctuation:
        punct = string.punctuation
        tokenized_text = [t for t in tokenized_text if t not in punct]

    # This step is extremely computational expensive. The benchmark
    # shows it would increase the total time by 12 times.
    if remove_noun:
        noun_set = set(['NNP', 'NNPS'])
        tokenized_text = [w for w, t in pos_tag(tokenized_text)
                          if t not in noun_set]
    # Stemming
    if stem:
        stemmer = SnowballStemmer('english')
        tokenized_text = [stemmer.stem(word) for word in tokenized_text]

    # This option is available as certain capital word has intrinsic
    # meaning. e.g. Apple vs apple.
    if remove_captalisation:
        tokenized_text = [word.lower() for word in tokenized_text]

    if remove_numerical:
        tokenized_text = [word for word in tokenized_text
                          if not word.isdigit()]

    # Remove stopwords and manual exlusion set
    meaningless_words = ['euractiv', 'com',
                         'bloomberg', 'reuters', 'jpg', 'png']
    exclusion_words = stopwords.words('english') + meaningless_words

    nonstopword_text = [word
                        for word in tokenized_text
                        if word.lower() not in exclusion_words]
    return nonstopword_text


def get_top_topic(text, k, model):
    tfidf = model.tf_vectorizer.transform(text)
    nmf = model.nmf[100].transform(tfidf)
    topic_series = pd.Series(nmf[0], index=model.nmf_labels)
    return topic_series.sort_values().tail(k).index.tolist()
