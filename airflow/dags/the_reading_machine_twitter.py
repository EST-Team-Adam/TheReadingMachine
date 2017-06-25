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

# Twitter scraping
# -------------------
twitter_scraper_script_path = os.path.join(
    process_directory, 'twitter_scraper/processor.py')
twitter_scraper_command = 'python {}'.format(
    twitter_scraper_script_path)
twitter_scraper = BashOperator(bash_command=twitter_scraper_command,
                               task_id='twitter_scraper',
                               params=default_args,
                               dag=dag)
db_raw_twitter = DummyOperator(task_id='db_raw_twitter', dag=dag)

# Sentiment scoring
# --------------------
sentiment_scoring_script_path = os.path.join(
    process_directory, 'sentiment_scoring/sentiment_scoring.py')
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
price_model = DummyOperator(task_id='price_model', dag=dag)
db_price_model = DummyOperator(task_id='db_price_model', dag=dag)

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

db_raw_twitter_article.set_upstream(twitter_scraper)

sentiment_scoring.set_upstream(db_raw_twitter_article)
topic_modelling.set_upstream(db_raw_twitter_article)
geo_tagging.set_upstream(db_raw_twitter_article)
commodity_tagging.set_upstream(db_raw_twitter_article)

db_sentiment_scoring.set_upstream(sentiment_scoring)
db_topic_modelling.set_upstream(topic_modelling)
db_geo_tagging.set_upstream(geo_tagging)
db_commodity_tagging.set_upstream(commodity_tagging)

data_harmonisation.set_upstream(db_sentiment_scoring)
data_harmonisation.set_upstream(db_topic_modelling)
data_harmonisation.set_upstream(db_geo_tagging)
data_harmonisation.set_upstream(db_commodity_tagging)

db_data_harmonisation.set_upstream(data_harmonisation)

price_model.set_upstream(db_data_harmonisation)
db_price_model.set_upstream(price_model)

# send_success_email.set_upstream(db_price_model)
