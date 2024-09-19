from typing import NoneType

from airflow.decorators import dag
from cosmos import DbtTaskGroup, ProjectConfig, RenderConfig

from include.constants import jaffle_shop_path, venv_execution_config
from include.profiles import redshift_db


@dag(
    dag_id="dbt_trigger",
    catchup=False,
    tags=["dbt_trigger"],
)
def dbt_trigger() -> NoneType:
    """
    DAG that triggers a dbt task group for executing dbt commands.

    This function sets up and runs a dbt task group using the provided
    configurations for the dbt project, profile, and virtual environment execution.
    It is designed to be scheduled and managed by Airflow.

    Task Details:
    - dbt_project: Refers to the dbt project configuration, including the project path
      and Redshift profile.
    - Dependencies are automatically installed in a virtual environment specified
      in the execution config.
    - The datasets will not be emitted by default (controlled by RenderConfig).

    Returns:
        None: This DAG doesn't return any values, it just triggers the dbt tasks.
    """
    dbt_task: DbtTaskGroup = DbtTaskGroup(
        group_id="dbt_project",
        project_config=ProjectConfig(jaffle_shop_path),
        profile_config=redshift_db,
        operator_args={"install_deps": True},
        execution_config=venv_execution_config,
        render_config=RenderConfig(emit_datasets=False),
    )

    dbt_task


dbt_trigger()
