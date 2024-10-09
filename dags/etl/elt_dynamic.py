"""ETL for dynamic CriptoYa processes"""

from types import NoneType

from airflow.decorators import dag
from airflow.operators.python import PythonOperator
from functions.alert_email import on_failure_callback, send_status_email
from functions.extract_data import extract_data_from_api
from functions.load_data import load_data_to_redshift

from include.config import TRANSFORM_FUNCTIONS

default_args = {
    "email_on_failure": False,
    "on_failure_callback": on_failure_callback,
}


def create_dynamic_elt_dag(process_type: str):
    """
    Dynamically creates an ETL DAG based on the provided process type.

    This function retrieves the appropriate transformation function from the
    TRANSFORM_FUNCTIONS configuration and sets up the tasks for extracting data from an API,
    transforming it, loading it into Redshift, and sending a status email upon completion.

    Args:
        process_type (str): The type of the ETL process, used to fetch the corresponding
                            API name, transformation function, and target Redshift table.

    Returns:
        NoneType: Returns a function that defines the DAG.
    """

    config = TRANSFORM_FUNCTIONS.get(process_type)

    @dag(
        dag_id=f"elt_{process_type}",
        description=f"ETL for {process_type}",
        catchup=False,
        default_args=default_args,
        schedule_interval=None,
        tags=[process_type],
    )
    def dynamic_elt() -> NoneType:
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
            op_kwargs={"api_name": config["api_name"]},
        )

        transform_task: PythonOperator = PythonOperator(
            task_id=f"transform_{process_type}_data",
            python_callable=config["transform_func"],
            op_kwargs={"data": "{{ ti.xcom_pull(task_ids='extract_data_from_api') }}"},
        )

        load_task: PythonOperator = PythonOperator(
            task_id=f"load_{process_type}_data_to_redshift",
            python_callable=load_data_to_redshift,
            op_kwargs={
                "df_json": f"{{{{ ti.xcom_pull(task_ids='transform_{process_type}_data') }}}}",
                "table_name": config["table_name"],
            },
        )

        alerting_email: PythonOperator = PythonOperator(
            task_id="alerting_email",
            python_callable=send_status_email,
            op_kwargs={
                "etl_name": f"{process_type}",
                "success": True,
            },
            trigger_rule="all_success",
        )

        extract_task >> transform_task >> load_task >> alerting_email

    return dynamic_elt()


for process in TRANSFORM_FUNCTIONS.keys():
    globals()[f"elt_{process}"] = create_dynamic_elt_dag(process_type=process)
