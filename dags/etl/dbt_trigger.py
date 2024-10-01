"""DAG that triggers a dbt task group for executing dbt commands"""

from cosmos import DbtDag, ProjectConfig, RenderConfig

from include.constants import jaffle_shop_path, venv_execution_config
from include.profiles import redshift_db

dbt_run_task = DbtDag(
    dag_id="dbt_run",
    project_config=ProjectConfig(jaffle_shop_path),
    profile_config=redshift_db,
    operator_args={"install_deps": True},
    execution_config=venv_execution_config,
    render_config=RenderConfig(select=["path:models"], emit_datasets=False),
    dag_id="dbt_trigger",
    catchup=False,
    tags=["dbt_trigger"],
)
