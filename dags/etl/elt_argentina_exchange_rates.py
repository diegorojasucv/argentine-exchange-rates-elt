"""DAG for orchestrating the ELT process of exchange rates in Argentina"""

from datetime import datetime

import pendulum
from airflow.models.dag import DAG
from airflow.operators.trigger_dagrun import TriggerDagRunOperator

local_tz = pendulum.timezone("America/Argentina/Buenos_Aires")

with DAG(
    dag_id="elt_argentina_exchange_rates",
    schedule_interval="0 12 * * *",
    start_date=datetime(2024, 9, 23, tzinfo=local_tz),
    catchup=False,
    tags=["main_elt"],
) as dag:
    """
    This DAG is scheduled to run daily and triggers multiple dependent DAGs
    responsible for fetching exchange rate data from various sources, including
    CriptoYa (USD, MEP, and other exchange rates) and BCRA indicators.
    After fetching the data, a dbt DAG is triggered to process the data.

    Tasks:
        - elt_criptoya_usdt: Triggers the DAG for fetching USD/USDT rates from CriptoYa.
        - elt_criptoya_mep: Triggers the DAG for fetching MEP rates from CriptoYa.
        - elt_criptoya_other: Triggers the DAG for fetching other exchange rates from CriptoYa.
        - elt_bcra_indicators: Triggers the DAG for fetching BCRA indicators.
        - dbt_trigger: Triggers the DAG responsible for running dbt transformations.

    Returns:
        None: This DAG does not return any values.
    """

    elt_criptoya_usd_trigger: TriggerDagRunOperator = TriggerDagRunOperator(
        task_id="elt_criptoya_usdt",
        trigger_dag_id="elt_criptoya_usdt",
    )

    elt_criptoya_mep_trigger: TriggerDagRunOperator = TriggerDagRunOperator(
        task_id="elt_criptoya_mep",
        trigger_dag_id="elt_criptoya_mep",
    )

    elt_criptoya_other_trigger: TriggerDagRunOperator = TriggerDagRunOperator(
        task_id="elt_criptoya_other",
        trigger_dag_id="elt_criptoya_other",
    )

    elt_bcra_indicators_trigger: TriggerDagRunOperator = TriggerDagRunOperator(
        task_id="elt_bcra_indicators",
        trigger_dag_id="elt_bcra_indicators",
    )

    dbt_trigger: TriggerDagRunOperator = TriggerDagRunOperator(
        task_id="dbt_trigger",
        trigger_dag_id="dbt_trigger",
    )

    (
        elt_criptoya_usd_trigger
        >> elt_criptoya_mep_trigger
        >> elt_criptoya_other_trigger
        >> elt_bcra_indicators_trigger
        >> dbt_trigger
    )
