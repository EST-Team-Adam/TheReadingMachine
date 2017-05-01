#!/bin/bash

source set_env_var.sh

# install virtualenv
pip install virtualenv

# Create virtual environment
virtualenv --verbose venv

# Start virtual environment
source venv/bin/activate

# Install Python packages
pip install -r requirements.txt

# Download the required nltk datasets
python $DATA_DIR/nltk_data_downloader.py

# Initialise Airflow
airflow initdb

