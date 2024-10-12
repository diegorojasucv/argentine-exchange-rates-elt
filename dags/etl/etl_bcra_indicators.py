"""ETL for bcra exchange rates"""

from types import NoneType

from airflow.decorators import dag
from airflow.operators.python import PythonOperator

from include.functions.alert_email import (on_failure_callback,
                                           send_status_email)
from include.functions.extract_data import extract_data_from_api
from include.functions.load_data import load_data_to_redshift
from include.functions.transform_data import transform_bcra_from_api

default_args = {
    "email_on_failure": False,
    "on_failure_callback": on_failure_callback,
}


@dag(
    dag_id="etl_bcra_indicators",
    description="ETL for BCRA indicators",
    catchup=False,
    default_args=default_args,
    schedule_interval=None,
    tags=["bcra-indicators"],
)
def etl_bcra_indicators() -> NoneType:
    """
    Defines the dynamic ETL DAG structure.

    Tasks:
        - extract_task: Fetches exchange rates from the CriptoYa and BCRA APIs.
        - transform_task: Transforms the raw data into the required format.
        - load_task: Loads the transformed data into a Redshift table.
        - alerting_email: Sends a email notification if all previous tasks are successful or if any task failed.

    Returns:
        NoneType: The DAG definition.
    """

    extract_task: PythonOperator = PythonOperator(
        task_id="extract_data_from_api",
        python_callable=extract_data_from_api,
        op_kwargs={"api_name": "bcra"},
    )

    transform_task: PythonOperator = PythonOperator(
        task_id="transform_bcra_data",
        python_callable=transform_bcra_from_api,
        op_kwargs={"data": "{{ ti.xcom_pull(task_ids='extract_data_from_api') }}"},
    )

    load_task: PythonOperator = PythonOperator(
        task_id="load_bcra_data_to_redshift",
        python_callable=load_data_to_redshift,
        op_kwargs={
            "df_json": "{{ ti.xcom_pull(task_ids='transform_bcra_data') }}",
            "table_name": "raw_bcra_indicators_test",
        },
    )

    alerting_email: PythonOperator = PythonOperator(
        task_id="alerting_email",
        python_callable=send_status_email,
        op_kwargs={
            "etl_name": "bcra",
            "success": True,
        },
        trigger_rule="all_success",
    )

    extract_task >> transform_task >> load_task >> alerting_email


etl_bcra_indicators()