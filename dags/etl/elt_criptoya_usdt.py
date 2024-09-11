from airflow.decorators import dag
from airflow.operators.python import PythonOperator
from airflow.models import Variable

from functions.extract_data import *
from functions.transform_data import *
from functions.load_data import *


@dag(
    dag_id="elt_criptoya_usdt",
    catchup=False,
    tags=["criptoya"],
)
def elt_criptoya_usdt() -> None:
    """
    ETL for usdt-ars prices for cripto exchanges.
    """

    extract_task = PythonOperator(
        task_id="extract_usdt_from_criptoya_api",
        python_callable=extract_usdt_from_criptoya_api,
        provide_context=True,
    )

    transform_task = PythonOperator(
        task_id="transform_usdt_from_criptoya_api",
        python_callable=transform_usdt_from_criptoya_api,
        provide_context=True,
        op_kwargs={
            "data": "{{ ti.xcom_pull(task_ids='extract_usdt_from_criptoya_api') }}"
        },
    )

    load_task = PythonOperator(
        task_id="load_usdt_prices_to_postgres",
        python_callable=load_data_to_redshift,
        provide_context=True,
        op_kwargs={
            "df_json": "{{ ti.xcom_pull(task_ids='transform_usdt_from_criptoya_api') }}",
            "table_name": "raw_usdt_ars_prices",
        },
    )

    extract_task >> transform_task >> load_task


elt_criptoya_usdt()
