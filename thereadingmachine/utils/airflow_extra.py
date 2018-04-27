import os
from airflow.operators.bash_operator import BashOperator


def BashWrapperOperator(pipeline_dir, script_dir, dag, dag_args):
    target_dir = os.path.join(pipeline_dir, script_dir)
    command = 'cd {}; python processor.py'.format(target_dir)
    operator = BashOperator(bash_command=command,
                            task_id=script_dir,
                            params=dag_args,
                            dag=dag)
    return operator
