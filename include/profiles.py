"Contains profile mappings used in the project"

from cosmos import ProfileConfig
from cosmos.profiles import (
    # PostgresUserPasswordProfileMapping,
    RedshiftUserPasswordProfileMapping,
)


# airflow_db = ProfileConfig(
#     profile_name="airflow_db",
#     target_name="dev",
#     profile_mapping=PostgresUserPasswordProfileMapping(
#         conn_id="airflow_metadata_db",
#         profile_args={"schema": "dbt"},
#     ),
# )

redshift_db = ProfileConfig(
    profile_name="redshift_db",
    target_name="dev",
    profile_mapping=RedshiftUserPasswordProfileMapping(
        conn_id="redshift_conn",
        profile_args={"schema": "2024_diego_rojas_schema"},
    ),
)
