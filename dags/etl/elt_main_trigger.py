"""DAG for orchestrating the ELT process of exchange rates in Argentina"""

from datetime import datetime

from airflow.models.dag import DAG
from airflow.operators.trigger_dagrun import TriggerDagRunOperator

with DAG(
    dag_id="elt_main_trigger",
    description="Main ETL",
    schedule_interval="@daily",
    start_date=datetime(2024, 9, 23),
    catchup=False,
    tags=["main_elt"],
) as dag:
    """
    This DAG is scheduled to run daily and triggers multiple dependent DAGs
    responsible for fetching exchange rate data from various sources, including
    CriptoYa (USD, MEP, and other exchange rates) and BCRA indicators.
    After fetching the data, a dbt DAG is triggered to process the data.

    Tasks:
        - elt_usdt: Triggers the DAG for fetching USD/USDT rates from CriptoYa.
        - elt_mep: Triggers the DAG for fetching MEP rates from CriptoYa.
        - elt_other: Triggers the DAG for fetching other exchange rates from CriptoYa.
        - elt_bcra: Triggers the DAG for fetching BCRA indicators.
        - dbt_trigger: Triggers the DAG responsible for running dbt transformations.

    Returns:
        None: This DAG does not return any values.
    """

    dags_to_trigger = ["elt_usdt", "elt_mep", "elt_other", "elt_bcra"]

    trigger_tasks = []
    for dag_info in dags_to_trigger:
        trigger_task = TriggerDagRunOperator(
            task_id=dag_info,
            trigger_dag_id=dag_info,
            wait_for_completion=True,
        )
        trigger_tasks.append(trigger_task)

    dbt_trigger: TriggerDagRunOperator = TriggerDagRunOperator(
        task_id="dbt_trigger",
        trigger_dag_id="dbt_trigger",
        wait_for_completion=True,
    )

    trigger_tasks >> dbt_trigger
