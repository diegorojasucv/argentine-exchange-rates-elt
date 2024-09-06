from datetime import datetime, timedelta

from airflow.decorators import dag
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator

from cosmos import DbtTaskGroup, ProjectConfig, RenderConfig

from include.profiles import airflow_db
from include.constants import jaffle_shop_path, venv_execution_config

from functions.extract_data import fetch_data_from_api
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
    schedule_interval="@daily",
    start_date=datetime(2023, 1, 1),
    catchup=False,
    tags=["etl_criptoya"],
)
def elt_argentina_exchange_rates() -> None:
    """
    The simplest example of using Cosmos to render a dbt project as a TaskGroup.
    """
    extract_task = PythonOperator(
        task_id="extrack_data_from_api",
        python_callable=fetch_data_from_api,
    )

    transform_task = PythonOperator(
        task_id="transform_data",
        python_callable=transform_data,
        op_kwargs={"data": "{{ ti.xcom_pull(task_ids='extrack_data_from_api') }}"},
    )

    load_task = PythonOperator(
        task_id="load_data_to_postgres",
        python_callable=load_data_to_postgres,
        op_kwargs={
            "df_json": "{{ ti.xcom_pull(task_ids='transform_data') }}",
            "db_config": db_config,
        },
    )

    dbt_task = DbtTaskGroup(
        group_id="dbt_project",
        project_config=ProjectConfig(jaffle_shop_path),
        profile_config=airflow_db,
        operator_args={ 
            "install_deps": True
        },
        execution_config=venv_execution_config,
        render_config=RenderConfig(emit_datasets=False),
    )

    extract_task >> transform_task >> load_task >> dbt_task


elt_argentina_exchange_rates()
