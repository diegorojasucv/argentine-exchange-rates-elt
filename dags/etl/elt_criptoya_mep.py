from airflow.decorators import dag
from airflow.operators.python import PythonOperator
from airflow.models import Variable

from functions.extract_data import *
from functions.transform_data import *
from functions.load_data import *


@dag(
    dag_id="elt_criptoya_mep",
    catchup=False,
    tags=["criptoya"],
)
def elt_criptoya_mep() -> None:
    """
    ETL for the mep-ars prices.
    """

    extract_task = PythonOperator(
        task_id="extract_data_from_api",
        python_callable=extract_data_from_api,
        op_kwargs={"api_name": "usd"},
    )

    transform_task = PythonOperator(
        task_id="transform_mep_usd_from_criptoya_api",
        python_callable=transform_mep_usd_from_criptoya_api,
        op_kwargs={"data": "{{ ti.xcom_pull(task_ids='extract_data_from_api') }}"},
    )

    load_task = PythonOperator(
        task_id="load_mep_prices_to_postgres",
        python_callable=load_data_to_redshift,
        op_kwargs={
            "df_json": "{{ ti.xcom_pull(task_ids='transform_mep_usd_from_criptoya_api') }}",
            "table_name": "raw_mep_ars_prices",
        },
    )

    extract_task >> transform_task >> load_task


elt_criptoya_mep()
