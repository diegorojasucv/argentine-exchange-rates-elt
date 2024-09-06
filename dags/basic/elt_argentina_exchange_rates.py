from datetime import datetime, timedelta

from airflow.models.dag import DAG
from airflow.operators.trigger_dagrun import TriggerDagRunOperator

with DAG(
    dag_id="elt_argentina_exchange_rates",
    schedule_interval="@daily",
    start_date=datetime(2024, 9, 5),
    catchup=False,
    tags=["main_elt"],
) as dag:

    extract_load_trigger = TriggerDagRunOperator(
        task_id="elt_criptoya",
        trigger_dag_id="elt_criptoya",
        conf={"message": "Hello World"},
    )

    dbt_trigger = TriggerDagRunOperator(
        task_id="dbt_trigger",
        trigger_dag_id="dbt_trigger",
        conf={"message": "Hello World"},
    )

    extract_load_trigger >> dbt_trigger
