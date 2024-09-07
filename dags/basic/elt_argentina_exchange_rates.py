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

    elt_criptoya_usd_trigger = TriggerDagRunOperator(
        task_id="elt_criptoya_usdt",
        trigger_dag_id="elt_criptoya_usdt",
    )

    elt_criptoya_mep_trigger = TriggerDagRunOperator(
        task_id="elt_criptoya_mep",
        trigger_dag_id="elt_criptoya_mep",
    )

    elt_criptoya_other_trigger = TriggerDagRunOperator(
        task_id="elt_criptoya_other",
        trigger_dag_id="elt_criptoya_other",
    )

    elt_bcra_indicators_trigger = TriggerDagRunOperator(
        task_id="elt_bcra_indicators",
        trigger_dag_id="elt_bcra_indicators",
    )

    dbt_trigger = TriggerDagRunOperator(
        task_id="dbt_trigger",
        trigger_dag_id="dbt_trigger",
    )

    elt_criptoya_usd_trigger >> dbt_trigger
