#!/bin/bash

# Load environment variable
export PROJECT_HOME=`pwd`
export PROCESS_DIR=$PROJECT_HOME/data_pipeline
export PACKAGE_DIR=$PROJECT_HOME/thereadingmachine
export AIRFLOW_HOME=$PROJECT_HOME/airflow
export DATA_DIR=$PROJECT_HOME/data
export NLTK_DATA=$DATA_DIR
export AIRFLOW_WEBSERVER_PID=$PROJECT_HOME/airflow-webserver.pid
export SCRAPER_FILE_PREFIX=blog_articles
