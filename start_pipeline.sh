#!/bin/bash

source set_env_var.sh

# Start webserver
if [ -e $AIRFLOW_WEBSERVER_PID ]
then
    cat $AIRFLOW_WEBSERVER_PID | xargs kill
    airflow webserver --pid $AIRFLOW_WEBSERVER_PID&
    echo "Web server restarted"
else
    airflow webserver --pid $AIRFLOW_WEBSERVER_PID&
    echo "Web server starting"
fi

# Start scheduler
airflow scheduler&

# Start web app
python $WEBAPP_DIR/app.py
