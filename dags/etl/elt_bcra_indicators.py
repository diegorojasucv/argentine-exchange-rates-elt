from airflow.decorators import dag
from airflow.operators.python import PythonOperator
from airflow.models import Variable

from functions.extract_data import *
from functions.transform_data import *
from functions.load_data import *


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
        task_id="extract_data_from_api",
        python_callable=extract_data_from_api,
        op_kwargs={"api_name": "bcra"},
    )

    transform_task = PythonOperator(
        task_id="transform_bcra_from_api",
        python_callable=transform_bcra_from_api,
        op_kwargs={"data": "{{ ti.xcom_pull(task_ids='extract_data_from_api') }}"},
    )

    load_task = PythonOperator(
        task_id="load_bcra_prices_to_postgres",
        python_callable=load_data_to_redshift,
        op_kwargs={
            "df_json": "{{ ti.xcom_pull(task_ids='transform_bcra_from_api') }}",
            "table_name": "raw_bcra_indicators",
        },
    )

    extract_task >> transform_task >> load_task


elt_bcra_indicators()
