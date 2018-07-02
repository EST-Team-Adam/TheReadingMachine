from airflow import DAG
from airflow.utils.dates import days_ago
from datetime import timedelta
from airflow.operators.bash_operator import BashOperator

# Set configure
default_args = {
    'owner': 'michael',
    'depends_on_past': False,
    'start_date': days_ago(1),
    'email': ['michael.kao@fao.org'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=1),
    'catchup_by_default': False
}

# Create dag, the frequency is at '00:00 on Sunday'.
dag = DAG('docker_clean_up',
          default_args=default_args,
          schedule_interval='0 0 * * 0')

# Create the clean up DAG
BashOperator(bash_command='docker system prune -a -f',
             task_id='docker_clean_up',
             params=default_args,
             dag=dag)
