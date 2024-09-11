from airflow.decorators import dag
from cosmos import DbtTaskGroup, ProjectConfig, RenderConfig

from include.profiles import redshift_db
from include.constants import jaffle_shop_path, venv_execution_config


@dag(
    dag_id="dbt_trigger",
    catchup=False,
    tags=["dbt_trigger"],
)
def dbt_trigger() -> None:
    """
    The simplest example of using Cosmos to render a dbt project as a TaskGroup.
    """

    dbt_task = DbtTaskGroup(
        group_id="dbt_project",
        project_config=ProjectConfig(jaffle_shop_path),
        profile_config=redshift_db,
        operator_args={"install_deps": True},
        execution_config=venv_execution_config,
        render_config=RenderConfig(emit_datasets=False),
    )

    dbt_task


dbt_trigger()
