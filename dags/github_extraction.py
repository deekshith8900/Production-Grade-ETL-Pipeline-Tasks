from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'github_extraction',
    default_args=default_args,
    description='Extract GitHub issues daily to S3',
    schedule_interval='@daily',
    start_date=datetime(2023, 1, 1),
    catchup=False,
    tags=['etl', 'github'],
) as dag:

    # Task to extract issues using the python script
    # We pass the execution date {{ ds }} (YYYY-MM-DD) to the script
    extract_task = BashOperator(
        task_id='extract_github_issues',
        bash_command='python /opt/airflow/scripts/extract_github.py --date {{ ds }}',
    )
    
    load_task = BashOperator(
        task_id='load_github_issues',
        bash_command='python /opt/airflow/scripts/load_raw.py --date {{ ds }}',
    )
    
    transform_task = BashOperator(
        task_id='transform_github_issues',
        bash_command='python /opt/airflow/scripts/transform.py --date {{ ds }}',
    )
    
    extract_task >> load_task >> transform_task
