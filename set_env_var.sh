#!/bin/bash

# Load environment variable
export PROJECT_HOME=`pwd`
export PROCESS_DIR=$PROJECT_HOME/data_pipeline
export PACKAGE_DIR=$PROJECT_HOME/thereadingmachine
export AIRFLOW_HOME=$PROJECT_HOME/airflow
export DATA_DIR=$PROJECT_HOME/data
export NLTK_DATA=$DATA_DIR
export AIRFLOW_WEBSERVER_PID=$HOME/airflow-webserver.pid

# Set current dataset version
export DATASET_PREFIX=amis_articles
export DATASET_VERSION=27_11_2016

# Set the start date of the model
export MODEL_START_DATE=2012-01-01
