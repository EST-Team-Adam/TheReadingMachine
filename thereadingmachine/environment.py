import os
import sqlalchemy
from sqlalchemy import create_engine

# Spiders for scraper
# MG: agrimoney now is not anymore freely available, such as bloomberg
spiders = ['worldgrain', 'euractiv']

# Data directory and engine
data_dir = os.environ['DATA_DIR']
plot_output_dir = os.environ['WEBAPP_PLOT_DIR']
engine = create_engine('sqlite:///{0}/the_reading_machine.db'.format(data_dir))
country_file = '{0}/list_of_countries.csv'.format(data_dir)
twitter_file = '{0}/Free_Twitter_Followers_Report_on_amis.csv'.format(data_dir)

# Table names
raw_article_table = 'RawArticle'
raw_tweet_table = 'RawTweets'
processed_article_table = 'ProcessedArticle'
processed_article_summary_table = 'ProcessedArticleSummary'
commodity_tagged_table = 'CommodityTaggedArticle'
geo_tagged_table = 'GeoTaggedArticle'
harmonised_table = 'HarmonisedData'
topic_model_table = 'TopicModel'
sentiment_scored_table = 'SentimentScoredArticle'
price_table = 'PriceIGC'
market_force_table = 'MarketForce'

# Table field type
processed_article_field_type = {
    'id': sqlalchemy.types.Integer(),
    'date': sqlalchemy.types.Date(),
    'article': sqlalchemy.types.Text(),
    'title': sqlalchemy.types.NVARCHAR(300),
    'source': sqlalchemy.types.NVARCHAR(20),
    'link': sqlalchemy.types.NVARCHAR(255)
}
processed_article_summary_field_type = {
    'createTime': sqlalchemy.types.DateTime(),
    'article_count': sqlalchemy.types.Integer(),
    'average_article_length': sqlalchemy.types.Float(),
    'average_lexical_diversity': sqlalchemy.types.Float(),
    'vocab_size': sqlalchemy.types.Integer()
}
commodity_tagged_field_type = {
    'id': sqlalchemy.types.Integer(),
    'containGrain': sqlalchemy.types.Boolean(),
    'containMaize': sqlalchemy.types.Boolean(),
    'containRice': sqlalchemy.types.Boolean(),
    'containSoybean': sqlalchemy.types.Boolean(),
    'containWheat': sqlalchemy.types.Boolean()
}

geo_tagged_field_type = {
    'id': sqlalchemy.types.Integer(),
    'geo_tag': sqlalchemy.types.NVARCHAR(length=255)
}
price_field_type = {
    'date': sqlalchemy.types.Date(),
    'GOI': sqlalchemy.types.Integer(),
    'Wheat': sqlalchemy.types.Integer(),
    'Maize': sqlalchemy.types.Integer(),
    'Rice': sqlalchemy.types.Integer(),
    'Barley': sqlalchemy.types.Integer(),
    'Soyabeans': sqlalchemy.types.Integer()
}
sentiment_scored_field_type = {
    'id': sqlalchemy.types.Integer(),
    'date': sqlalchemy.types.Date(),
    'compound_sentiment': sqlalchemy.types.Float(),
    'negative_sentiment': sqlalchemy.types.Float(),
    'neutral_sentiment': sqlalchemy.types.Float(),
    'positive_sentiment': sqlalchemy.types.Float()
}
raw_tweet_field_type = {
    'source': sqlalchemy.types.Unicode(length=255),
    'title': sqlalchemy.types.Unicode(length=255),
    'date': sqlalchemy.types.Date(),
    'link': sqlalchemy.types.Unicode(length=255),
    'article': sqlalchemy.types.UnicodeText
}
