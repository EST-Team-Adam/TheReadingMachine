import os
from airflow import DAG
from airflow import configuration as conf
from airflow.operators.dummy_operator import DummyOperator
from datetime import datetime, timedelta
from thereadingmachine.utils.airflow_extra import BashWrapperOperator

# Load configuration
process_directory = os.path.join(conf.get('core', 'process_folder'))


# Set configure
default_args = {
    'owner': 'michael',
    'depends_on_past': False,
    'start_date': datetime(2018, 4, 20),
    'email': ['michael.kao@fao.org'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=1),
    'catchup_by_default': False
}

# Create dag
dag = DAG('the_reading_machine',
          default_args=default_args,
          schedule_interval='@daily')

########################################################################
# Create nodes
########################################################################

# Article scrapping
# --------------------
article_scraper = BashWrapperOperator(pipeline_dir=process_directory,
                                      script_dir='article_scraper',
                                      dag=dag,
                                      dag_args=default_args)
db_raw_article = DummyOperator(task_id='db_raw_article', dag=dag)

# Article processing
# --------------------
article_processing = BashWrapperOperator(pipeline_dir=process_directory,
                                         script_dir='article_processing',
                                         dag=dag,
                                         dag_args=default_args)
db_processed_article = DummyOperator(task_id='db_processed_article', dag=dag)


# Price Extraction
# --------------------
price_scraper = BashWrapperOperator(pipeline_dir=process_directory,
                                    script_dir='price_scraper',
                                    dag=dag,
                                    dag_args=default_args)
db_raw_price = DummyOperator(task_id='db_raw_price', dag=dag)


# Sentiment scoring
# --------------------
sentiment_scoring = BashWrapperOperator(pipeline_dir=process_directory,
                                        script_dir='sentiment_scoring',
                                        dag=dag,
                                        dag_args=default_args)
db_sentiment_scoring = DummyOperator(task_id='db_sentiment_scoring', dag=dag)

# Topic Modelling
# --------------------
topic_modelling = BashWrapperOperator(pipeline_dir=process_directory,
                                      script_dir='topic_modelling',
                                      dag=dag,
                                      dag_args=default_args)
db_topic_modelling = DummyOperator(task_id='db_topic_modelling', dag=dag)


# Data harmonisation
# --------------------
data_harmonisation = BashWrapperOperator(pipeline_dir=process_directory,
                                         script_dir='data_harmonisation',
                                         dag=dag,
                                         dag_args=default_args)
db_data_harmonisation = DummyOperator(task_id='db_data_harmonisation', dag=dag)

# Compute the market force
# --------------------
compute_market_force = BashWrapperOperator(pipeline_dir=process_directory,
                                           script_dir='compute_market_force',
                                           dag=dag,
                                           dag_args=default_args)


########################################################################
# Create dependency
########################################################################

db_raw_article.set_upstream(article_scraper)
db_raw_price.set_upstream(price_scraper)

article_processing.set_upstream(db_raw_article)
db_processed_article.set_upstream(article_processing)

sentiment_scoring.set_upstream(db_processed_article)
topic_modelling.set_upstream(db_processed_article)

db_sentiment_scoring.set_upstream(sentiment_scoring)
db_topic_modelling.set_upstream(topic_modelling)

data_harmonisation.set_upstream(db_sentiment_scoring)
data_harmonisation.set_upstream(db_topic_modelling)

db_data_harmonisation.set_upstream(data_harmonisation)
compute_market_force.set_upstream(db_data_harmonisation)
