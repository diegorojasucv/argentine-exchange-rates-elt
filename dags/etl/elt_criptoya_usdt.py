"""ETL for usdt-ars pair"""

from functools import partial
from types import NoneType

from airflow.decorators import dag
from airflow.operators.python import PythonOperator

from dags.functions.alert_email import on_failure_callback, send_status_email
from dags.functions.extract_data import extract_data_from_api
from dags.functions.load_data import load_data_to_redshift
from dags.functions.transform_data import transform_usdt_from_criptoya_api

ETL_NAME = "CriptoYa USDT-ARS"

default_args = {
    "email_on_failure": False,
    "on_failure_callback": partial(on_failure_callback, ETL_NAME),
}


@dag(
    dag_id="elt_criptoya_usdt",
    catchup=False,
    tags=["criptoya"],
)
def elt_criptoya_usdt() -> NoneType:
    """
    ETL pipeline for extracting, transforming, and loading USDT prices from CriptoYa API.

    This DAG orchestrates an ETL process that extracts USDT data from the CriptoYa API,
    transforms the data, and loads it into a PostgreSQL or Redshift table.

    Tasks:
        - extract_data_from_api: Fetches USDT prices from the CriptoYa API.
        - transform_usdt_from_criptoya_api: Transforms the raw USDT data for further processing.
        - load_usdt_prices_to_postgres: Loads the transformed USDT prices into the 'raw_usdt_ars_prices' table.
        - alerting_email: Sends a email notification if all previous tasks are successful or if any task failed.

    Returns:
        NoneType: This function returns nothing as it's meant to define a DAG.
    """

    extract_task: PythonOperator = PythonOperator(
        task_id="extract_data_from_api",
        python_callable=extract_data_from_api,
        op_kwargs={"api_name": "usdt"},
    )

    transform_task: PythonOperator = PythonOperator(
        task_id="transform_usdt_from_criptoya_api",
        python_callable=transform_usdt_from_criptoya_api,
        op_kwargs={"data": "{{ ti.xcom_pull(task_ids='extract_data_from_api') }}"},
    )

    load_task: PythonOperator = PythonOperator(
        task_id="load_usdt_prices_to_postgres",
        python_callable=load_data_to_redshift,
        op_kwargs={
            "df_json": "{{ ti.xcom_pull(task_ids='transform_usdt_from_criptoya_api') }}",
            "table_name": "raw_usdt_ars_prices",
        },
    )

    alerting_email: PythonOperator = PythonOperator(
        task_id="alerting_email",
        python_callable=send_status_email,
        op_kwargs={
            "etl_name": ETL_NAME,
            "success": True,
        },
        trigger_rule="all_success",
    )

    extract_task >> transform_task >> load_task >> alerting_email


elt_criptoya_usdt()
