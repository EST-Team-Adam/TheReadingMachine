import os
from airflow import DAG
from airflow import configuration as conf
from airflow.operators.bash_operator import BashOperator
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.email_operator import EmailOperator
from datetime import datetime, timedelta


# Load configuration
process_directory = os.path.join(conf.get('core', 'process_folder'))


# Set configure
default_args = {
    'owner': 'michael',
    'depends_on_past': False,
    'start_date': datetime(2017, 4, 24),
    'email': ['mkao006@gmail.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=1),
    'catchup_by_default': False
}

# Create dag
dag = DAG('the_reading_machine',
          default_args=default_args,
          schedule_interval=None)

########################################################################
# Create nodes
########################################################################

# Article scrapping
# --------------------
article_scraper_script_path = os.path.join(
    process_directory, 'article_scraper/processor.py')
article_scraper_command = 'python {}'.format(
    article_scraper_script_path)
article_scraper = BashOperator(bash_command=article_scraper_command,
                               task_id='article_scraper',
                               params=default_args,
                               dag=dag)
db_raw_article = DummyOperator(task_id='db_raw_article', dag=dag)

# Article processing
# --------------------
article_processing_script_path = os.path.join(
    process_directory, 'article_processing/processor.py')
article_processing_command = 'python {}'.format(
    article_processing_script_path)
article_processing = BashOperator(bash_command=article_processing_command,
                                  task_id='article_processing',
                                  params=default_args,
                                  dag=dag)
db_processed_article = DummyOperator(task_id='db_processed_article', dag=dag)


# Price Extraction
# --------------------
price_scraper_script_path = os.path.join(
    process_directory, 'price_extraction/processor.py')
price_scraper_command = 'python {}'.format(
    price_scraper_script_path)
price_scraper = BashOperator(bash_command=price_scraper_command,
                             task_id='price_extraction',
                             params=default_args,
                             dag=dag)
db_raw_price = DummyOperator(task_id='db_raw_price', dag=dag)


# Sentiment scoring
# --------------------
sentiment_scoring_script_path = os.path.join(
    process_directory, 'sentiment_scoring/processor.py')
sentiment_scoring_command = 'python {}'.format(
    sentiment_scoring_script_path)
sentiment_scoring = BashOperator(bash_command=sentiment_scoring_command,
                                 task_id='sentiment_scoring',
                                 params=default_args,
                                 dag=dag)
db_sentiment_scoring = DummyOperator(task_id='db_sentiment_scoring', dag=dag)

# Topic Modelling
# --------------------
topic_modelling_script_path = os.path.join(
    process_directory, 'topic_modelling/processor.py')
topic_modelling_command = 'python {}'.format(
    topic_modelling_script_path)
topic_modelling = BashOperator(bash_command=topic_modelling_command,
                               task_id='topic_modelling',
                               params=default_args,
                               dag=dag)
db_topic_modelling = DummyOperator(task_id='db_topic_modelling', dag=dag)

# Geo_Tagging
# --------------------
geo_tagging_script_path = os.path.join(
    process_directory, 'geo_tagging/processor.py')
geo_tagging_command = 'python {}'.format(
    geo_tagging_script_path)
geo_tagging = BashOperator(bash_command=geo_tagging_command,
                           task_id='geo_tagging',
                           params=default_args,
                           dag=dag)
db_geo_tagging = DummyOperator(task_id='db_geo_tagging', dag=dag)

# Commodity tagging
# --------------------
commodity_tagging_script_path = os.path.join(
    process_directory, 'commodity_tagging/processor.py')
commodity_tagging_command = 'python {}'.format(
    commodity_tagging_script_path)
commodity_tagging = BashOperator(bash_command=commodity_tagging_command,
                                 task_id='commodity_tagging',
                                 params=default_args,
                                 dag=dag)
db_commodity_tagging = DummyOperator(task_id='db_commodity_tagging', dag=dag)

# Data harmonisation
# --------------------
data_harmonisation_script_path = os.path.join(
    process_directory, 'data_harmonisation/processor.py')
data_harmonisation_command = 'python {}'.format(
    data_harmonisation_script_path)
data_harmonisation = BashOperator(bash_command=data_harmonisation_command,
                                  task_id='data_harmonisation',
                                  params=default_args,
                                  dag=dag)
db_data_harmonisation = DummyOperator(task_id='db_data_harmonisation', dag=dag)


# Build price model
# --------------------
price_modelling_script_path = os.path.join(
    process_directory, 'price_modelling/processor.py')
price_modelling_command = 'python {}'.format(
    price_modelling_script_path)
price_modelling = BashOperator(bash_command=price_modelling_command,
                               task_id='price_modelling',
                               params=default_args,
                               dag=dag)
db_price_forecast = DummyOperator(task_id='db_price_forecast', dag=dag)

# Sent email
# --------------------
# send_success_email = EmailOperator(
#     task_id='send_success_email',
#     to=default_args['email'],
#     subject='The Reading Machine executed successfully',
#     html_content='',
#     dag=dag)

########################################################################
# Create dependency
########################################################################

db_raw_article.set_upstream(article_scraper)
db_raw_price.set_upstream(price_scraper)

article_processing.set_upstream(db_raw_article)
db_processed_article.set_upstream(article_processing)

sentiment_scoring.set_upstream(db_processed_article)
topic_modelling.set_upstream(db_processed_article)
geo_tagging.set_upstream(db_processed_article)
commodity_tagging.set_upstream(db_processed_article)

db_sentiment_scoring.set_upstream(sentiment_scoring)
db_topic_modelling.set_upstream(topic_modelling)
db_geo_tagging.set_upstream(geo_tagging)
db_commodity_tagging.set_upstream(commodity_tagging)

data_harmonisation.set_upstream(db_sentiment_scoring)
data_harmonisation.set_upstream(db_topic_modelling)
data_harmonisation.set_upstream(db_geo_tagging)
data_harmonisation.set_upstream(db_commodity_tagging)

db_data_harmonisation.set_upstream(data_harmonisation)

price_modelling.set_upstream(db_raw_price)
price_modelling.set_upstream(db_data_harmonisation)
db_price_forecast.set_upstream(price_modelling)

# send_success_email.set_upstream(db_price_model)
