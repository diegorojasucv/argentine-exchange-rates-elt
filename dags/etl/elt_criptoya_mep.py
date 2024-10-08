"""ETL for mep-ars pair"""

from types import NoneType

from airflow.decorators import dag
from airflow.operators.python import PythonOperator

from dags.functions.extract_data import extract_data_from_api
from dags.functions.load_data import load_data_to_redshift
from dags.functions.transform_data import transform_mep_usd_from_criptoya_api


@dag(
    dag_id="elt_criptoya_mep",
    catchup=False,
    tags=["criptoya"],
    schedule_interval=None,
    max_active_tasks=1,
)
def elt_criptoya_mep() -> NoneType:
    """
    ETL pipeline for extracting, transforming, and loading MEP USD prices from CriptoYa API.

    This DAG handles the process of fetching MEP USD data from the CriptoYa API,
    transforming the data, and loading it into a PostgreSQL or Redshift table.

    Tasks:
        - extract_data_from_api: Fetches MEP USD prices from the CriptoYa API.
        - transform_mep_usd_from_criptoya_api: Transforms the raw data into the required format.
        - load_mep_prices_to_postgres: Loads the transformed data into the 'raw_mep_ars_prices' table.

    Returns:
        NoneType: This function returns nothing as it's meant to define a DAG.
    """

    extract_task: PythonOperator = PythonOperator(
        task_id="extract_data_from_api",
        python_callable=extract_data_from_api,
        op_kwargs={"api_name": "usd"},
    )

    transform_task: PythonOperator = PythonOperator(
        task_id="transform_mep_usd_from_criptoya_api",
        python_callable=transform_mep_usd_from_criptoya_api,
        op_kwargs={"data": "{{ ti.xcom_pull(task_ids='extract_data_from_api') }}"},
    )

    load_task: PythonOperator = PythonOperator(
        task_id="load_mep_prices_to_postgres",
        python_callable=load_data_to_redshift,
        op_kwargs={
            "df_json": "{{ ti.xcom_pull(task_ids='transform_mep_usd_from_criptoya_api') }}",
            "table_name": "raw_mep_ars_prices",
        },
    )

    extract_task >> transform_task >> load_task


elt_criptoya_mep()
