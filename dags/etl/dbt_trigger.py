"""DAG that triggers a dbt task group for executing dbt commands"""

from datetime import timedelta
from types import NoneType

from airflow.decorators import dag
from cosmos import DbtTaskGroup, ProjectConfig, RenderConfig

from include.constants import jaffle_shop_path, venv_execution_config
from include.profiles import redshift_db


@dag(
    dag_id="dbt_trigger",
    catchup=False,
    default_args={"retries": 5, "retry_delay": timedelta(minutes=1)},
    tags=["dbt_trigger"],
)
def dbt_trigger() -> NoneType:
    """
    This function sets up and runs a dbt task group using the provided
    configurations for the dbt project, profile, and virtual environment execution.
    It is designed to be scheduled and managed by Airflow.

    Task Details:
        - dbt_task: Trigger a build run. This means that a run job and a test job are executed.

    Returns:
        None: This DAG doesn't return any values.
    """
    dbt_task = DbtTaskGroup(
        group_id="dbt_project",
        project_config=ProjectConfig(jaffle_shop_path),
        profile_config=redshift_db,
        operator_args={
            "install_deps": True,
        },
        execution_config=venv_execution_config,
        render_config=RenderConfig(
            select=["1+int_exchange_rates_unioned+"], emit_datasets=False
        ),
    )

    dbt_task


dbt_trigger()
