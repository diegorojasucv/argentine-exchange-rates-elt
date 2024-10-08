"""Load functions"""

import json
from typing import Dict

import pandas as pd
from airflow.models import Variable
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError


def connect_to_redshift_engine():
    """
    Establish a connection to the Redshift database using SQLAlchemy.

    Returns:
        Connection: SQLAlchemy connection for Redshift.
    """
    try:
        redshift_user = "2024_diego_rojas"
        redshift_password = Variable.get("redshift_password")
        redshift_host = (
            "redshift-pda-cluster.cnuimntownzt.us-east-2.redshift.amazonaws.com"
        )
        redshift_port = 5439
        redshift_db = "pda"

        connection_string = f"redshift+psycopg2://{redshift_user}:{redshift_password}@{redshift_host}:{redshift_port}/{redshift_db}"

        # Create an engine and immediately connect to Redshift
        engine = create_engine(connection_string)
        return engine

    except OperationalError as e:
        raise RuntimeError(f"An error occurred while connecting to Redshift: {str(e)}")


def load_data_to_redshift(df_json: str, table_name: str) -> None:
    """
    Load data from a JSON string into the specified Redshift table.

    Args:
        df_json (str): Data in JSON format to be inserted.
        table_name (str): Name of the table to insert the data into.
    """
    df_dict: Dict = json.loads(df_json)
    df: pd.DataFrame = pd.DataFrame.from_dict(df_dict)

    connection = connect_to_redshift_engine()

    try:
        df.to_sql(
            table_name,
            connection,
            schema="2024_diego_rojas_schema",
            if_exists="append",
            index=False,
        )
    except Exception as e:
        raise RuntimeError(
            f"An error occurred while loading data to Redshift: {str(e)}"
        )
