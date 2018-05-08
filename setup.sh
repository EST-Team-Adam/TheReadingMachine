#!/bin/bash

# Load environment variable
source set_env_var.sh

# Use virtual env if not in Docker
if ! [[ "$(cat /proc/1/cgroup | grep docker)" ]]
then
    # install virtualenv
    pip install virtualenv

    # Create virtual environment
    virtualenv --verbose venv

    # Start virtual environment
    # Load virtualenv
    if [[ "$VIRTUAL_ENV" == "" ]]
    then
        source venv/bin/activate
    fi
fi

# Install or update pip
pip install --upgrade pip

# Install Python packages
pip install -r requirements.txt

# Download the required nltk datasets
python $DATA_DIR/nltk_data_downloader.py

# Create data base
touch $DATA_DIR/the_reading_machine.db

# Initialise Airflow
airflow initdb

