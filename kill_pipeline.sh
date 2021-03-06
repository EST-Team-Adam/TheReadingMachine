#/bin/bash

# Kill webserver
cat $AIRFLOW_WEBSERVER_PID | xargs kill

# Kill scheduler
ps -f | grep airflow | awk '{print $2}' | xargs kill
