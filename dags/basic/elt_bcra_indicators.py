from airflow.decorators import dag
from airflow.operators.python import PythonOperator
from airflow.models import Variable

from functions.extract_data import *
from functions.transform_data import *
from functions.load_data import *

db_config = {
    "host": Variable.get("postgres_host"),
    "port": 5432,
    "dbname": Variable.get("postgres_dbname"),
    "user": Variable.get("postgres_user"),
    "password": Variable.get("postgres_password"),
    "schema": "raw",
}


@dag(
    dag_id="elt_bcra_indicators",
    catchup=False,
    tags=["bcra"],
)
def elt_bcra_indicators() -> None:
    """
    ETL for BCRA indicators.
    """

    extract_task = PythonOperator(
        task_id="extract_bcra_from_api",
        python_callable=extract_bcra_from_api,
    )

    transform_task = PythonOperator(
        task_id="transform_bcra_from_api",
        python_callable=transform_bcra_from_api,
        op_kwargs={"data": "{{ ti.xcom_pull(task_ids='extract_bcra_from_api') }}"},
    )

    load_task = PythonOperator(
        task_id="load_bcra_prices_to_postgres",
        python_callable=load_bcra_prices_to_postgres,
        op_kwargs={
            "df_json": "{{ ti.xcom_pull(task_ids='transform_bcra_from_api') }}",
            "db_config": db_config,
        },
    )

    extract_task >> transform_task >> load_task


elt_bcra_indicators()
