from airflow.decorators import dag
from airflow.operators.python import PythonOperator

from functions.extract_data import extract_usdt_from_criptoya_api
from functions.transform_data import transform_data
from functions.load_data import load_data_to_postgres

db_config = {
    "host": "postgres",
    "port": 5432,
    "dbname": "postgres",
    "user": "postgres",
    "password": "postgres",
    "schema": "raw",
}


@dag(
    dag_id="elt_criptoya_usdt",
    catchup=False,
    tags=["elt_criptoya_usdt"],
)
def elt_criptoya_usdt() -> None:
    """
    The simplest example of using Cosmos to render a dbt project as a TaskGroup.
    """

    extract_task = PythonOperator(
        task_id="extract_usdt_from_criptoya_api",
        python_callable=extract_usdt_from_criptoya_api,
    )

    transform_task = PythonOperator(
        task_id="transform_data",
        python_callable=transform_data,
        op_kwargs={
            "data": "{{ ti.xcom_pull(task_ids='extract_usdt_from_criptoya_api') }}"
        },
    )

    load_task = PythonOperator(
        task_id="load_data_to_postgres",
        python_callable=load_data_to_postgres,
        op_kwargs={
            "df_json": "{{ ti.xcom_pull(task_ids='transform_data') }}",
            "db_config": db_config,
        },
    )

    extract_task >> transform_task >> load_task


elt_criptoya_usdt()
