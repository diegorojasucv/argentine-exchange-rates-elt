"""ETL for other exchange rates"""

from types import NoneType

from airflow.decorators import dag
from airflow.models import Variable
from airflow.operators.python import PythonOperator

from dags.functions.alert_email import on_failure_callback, send_status_email
from dags.functions.extract_data import extract_data_from_api
from dags.functions.load_data import load_data_to_redshift
from dags.functions.transform_data import transform_other_usd_from_criptoya_api

ALERT_EMAIL = Variable.get("email_to_send_alert")
ETL_NAME = "CriptoYa Other"


@dag(
    dag_id="elt_criptoya_other",
    catchup=False,
    tags=["criptoya"],
    default_args={
        "email_on_failure": False,  # Desactivar el email de error automático para usar el personalizado
        "on_failure_callback": on_failure_callback,  # Callback en caso de fallo
    },
)
def elt_criptoya_other() -> NoneType:
    """
    ETL pipeline for extracting, transforming, and loading Other USD prices (e.g Saving, Card and Blue) from CriptoYa API.

    This DAG orchestrates an ETL process to retrieve data for other USD prices (e.g Saving, Card and Blue)
    using the CriptoYa API, transforms it, and loads it into a PostgreSQL or Redshift table.

    Tasks:
        - extract_data_from_api: Fetches USD prices from other sources via the CriptoYa API.
        - transform_other_usd_from_criptoya_api: Transforms the raw USD data for further use.
        - load_other_prices_to_postgres: Loads the transformed data into the 'raw_other_ars_prices' table.

    Returns:
        None: This DAG doesn't return any values.
    """

    extract_task = PythonOperator(
        task_id="extract_data_from_api",
        python_callable=extract_data_from_api,
        op_kwargs={"api_name": "usd"},
    )

    transform_task = PythonOperator(
        task_id="transform_other_usd_from_criptoya_api",
        python_callable=transform_other_usd_from_criptoya_api,
        op_kwargs={"data": "{{ ti.xcom_pull(task_ids='extract_data_from_api') }}"},
    )

    load_task = PythonOperator(
        task_id="load_other_prices_to_postgres",
        python_callable=load_data_to_redshift,
        op_kwargs={
            "df_json": "{{ ti.xcom_pull(task_ids='transform_other_usd_from_criptoya_api') }}",
            "table_name": "raw_other_ars_prices",
        },
    )

    # Email task for success notification
    alerting_email = PythonOperator(
        task_id="alerting_email",
        python_callable=send_status_email,
        op_kwargs={"etl_name": ETL_NAME, "success": True},
        trigger_rule="all_success",
    )

    extract_task >> transform_task >> load_task >> alerting_email


elt_criptoya_other()
