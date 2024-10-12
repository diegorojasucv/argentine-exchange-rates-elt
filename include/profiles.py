"Contains profile mappings used in the project"

from cosmos import ProfileConfig
from cosmos.profiles import RedshiftUserPasswordProfileMapping

redshift_db = ProfileConfig(
    profile_name="redshift_db",
    target_name="dev",
    profile_mapping=RedshiftUserPasswordProfileMapping(
        conn_id="redshift_conn",
        profile_args={"schema": "2024_diego_rojas_schema"},
    ),
)
