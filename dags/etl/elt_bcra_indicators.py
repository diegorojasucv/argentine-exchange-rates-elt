"""ETL for bcra indicators"""

from functools import partial
from types import NoneType

from airflow.decorators import dag
from airflow.operators.python import PythonOperator

from functions.alert_email import on_failure_callback, send_status_email
from functions.extract_data import extract_data_from_api
from functions.load_data import load_data_to_redshift
from functions.transform_data import transform_bcra_from_api

ETL_NAME = "BCRA indicators"

default_args = {
    "email_on_failure": False,
    "on_failure_callback": partial(on_failure_callback, ETL_NAME),
}


@dag(
    dag_id="elt_bcra_indicators",
    description="BCRA ETL",
    catchup=False,
    tags=["bcra"],
    schedule_interval=None,
)
def elt_bcra_indicators() -> NoneType:
    """
    ETL pipeline for extracting, transforming, and loading BCRA indicators data.

    This DAG orchestrates an ETL process that retrieves data from the BCRA API,
    transforms it, and loads the processed data into a PostgreSQL (or Redshift) database.

    Tasks:
        - extract_data_from_api: Fetches BCRA data from the API.
        - transform_bcra_from_api: Transforms the fetched BCRA data for further use.
        - load_bcra_prices_to_postgres: Loads the transformed data into a PostgreSQL or Redshift table.
        - alerting_email: Sends a email notification if all previous tasks are successful or if any task failed.

    Returns:
        NoneType: This function returns nothing as it's meant to define a DAG.
    """

    extract_task: PythonOperator = PythonOperator(
        task_id="extract_data_from_api",
        python_callable=extract_data_from_api,
        op_kwargs={"api_name": "bcra"},
    )

    transform_task: PythonOperator = PythonOperator(
        task_id="transform_bcra_from_api",
        python_callable=transform_bcra_from_api,
        op_kwargs={"data": "{{ ti.xcom_pull(task_ids='extract_data_from_api') }}"},
    )

    load_task: PythonOperator = PythonOperator(
        task_id="load_bcra_prices_to_postgres",
        python_callable=load_data_to_redshift,
        op_kwargs={
            "df_json": "{{ ti.xcom_pull(task_ids='transform_bcra_from_api') }}",
            "table_name": "raw_bcra_indicators",
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


elt_bcra_indicators()
