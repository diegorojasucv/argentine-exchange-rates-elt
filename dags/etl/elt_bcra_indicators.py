from airflow.decorators import dag
from airflow.operators.python import PythonOperator
from dags.functions.extract_data import extract_data_from_api
from dags.functions.transform_data import transform_bcra_from_api
from dags.functions.load_data import load_data_to_redshift


@dag(
    dag_id="elt_bcra_indicators",
    catchup=False,
    tags=["bcra"],
)
def elt_bcra_indicators() -> None:
    """
    ETL pipeline for extracting, transforming, and loading BCRA indicators data.

    This DAG orchestrates an ETL process that retrieves data from the BCRA API,
    transforms it, and loads the processed data into a PostgreSQL (or Redshift) database.

    Tasks:
        - extract_data_from_api: Fetches BCRA data from the API.
        - transform_bcra_from_api: Transforms the fetched BCRA data for further use.
        - load_bcra_prices_to_postgres: Loads the transformed data into a PostgreSQL or Redshift table.

    Returns:
        None: This DAG doesn't return any values.
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

    # Define task dependencies
    extract_task >> transform_task >> load_task


elt_bcra_indicators()
