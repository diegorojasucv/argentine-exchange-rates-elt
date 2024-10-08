"""DAG that triggers a dbt task group for executing dbt commands"""

from functools import partial
from types import NoneType

from airflow.decorators import dag
from airflow.operators.python import PythonOperator
from cosmos import DbtTaskGroup, ProjectConfig, RenderConfig

from dags.functions.alert_email import on_failure_callback, send_status_email
from include.constants import jaffle_shop_path, venv_execution_config
from include.profiles import redshift_db

ETL_NAME = "dbt trigger"

default_args = {
    "email_on_failure": False,
    "on_failure_callback": partial(on_failure_callback, ETL_NAME),
}


@dag(
    dag_id="dbt_trigger",
    description="dbt trigger",
    catchup=False,
    tags=["dbt_trigger"],
)
def dbt_trigger() -> NoneType:
    """
    This function sets up and runs a dbt task group using the provided
    configurations for the dbt project, profile, and virtual environment execution.
    It is designed to be scheduled and managed by Airflow.

    Task Details:
        - dbt_task: Trigger a build run. This means that a run job and a test job are executed.
        - alerting_email: Sends a email notification if all previous tasks are successful or if any task failed.

    Returns:
        None: This DAG doesn't return any values.
    """
    dbt_task = DbtTaskGroup(
        group_id="dbt_project",
        project_config=ProjectConfig(jaffle_shop_path),
        profile_config=redshift_db,
        operator_args={"install_deps": True},
        execution_config=venv_execution_config,
        render_config=RenderConfig(emit_datasets=False),
    )

    alerting_email: PythonOperator = PythonOperator(
        task_id="alerting_email",
        python_callable=send_status_email,
        op_kwargs={
            "etl_name": ETL_NAME,
            "success": True,
        },
        trigger_rule="all_success",
    )

    dbt_task >> alerting_email


dbt_trigger()
