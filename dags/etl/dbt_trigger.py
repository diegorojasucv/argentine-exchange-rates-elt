"""DAG that triggers a dbt task group for executing dbt commands"""

from types import NoneType

from airflow.decorators import dag
from cosmos import DbtDag, ProjectConfig, RenderConfig

from include.constants import jaffle_shop_path, venv_execution_config
from include.profiles import redshift_db


@dag(
    dag_id="dbt_trigger",
    catchup=False,
    tags=["dbt_trigger"],
)
def dbt_trigger() -> NoneType:
    """
    This function sets up and runs two dbt tasks (run and test) using the provided
    configurations for the dbt project, profile, and virtual environment execution.
    It is designed to be scheduled and managed by Airflow.

    Task Details:
        - dbt_run_task: Executes a `dbt run` command.
        - dbt_test_task: Executes a `dbt test` command.

    Returns:
        None: This DAG doesn't return any values.
    """
    # Task 1: Run dbt run on the model and its dependencies
    dbt_run_task = DbtDag(
        dag_id="dbt_run",
        project_config=ProjectConfig(jaffle_shop_path),
        profile_config=redshift_db,
        operator_args={"install_deps": True},
        execution_config=venv_execution_config,
        render_config=RenderConfig(
            select=["+metrics_exchange_rates"], emit_datasets=False
        ),
    )

    # Task 2: Run dbt test on the model and its dependencies
    # dbt_test_task = DbtDag(
    #     dag_id="dbt_test",
    #     project_config=ProjectConfig(jaffle_shop_path),
    #     profile_config=redshift_db,
    #     operator_args={"install_deps": True},
    #     execution_config=venv_execution_config,
    #     render_config=RenderConfig(
    #         select=["+metrics_exchange_rates"], emit_datasets=False
    #     ),
    #     dbt_cmd="test",
    # )

    dbt_run_task


dbt_trigger()
