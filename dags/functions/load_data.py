import ast
import pandas as pd
from airflow.models import Variable
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError


def connect_to_redshift_engine():
    """
    Establish a connection to the Redshift database using SQLAlchemy.

    Returns:
        sqlalchemy.engine.Engine: SQLAlchemy engine for Redshift connection.
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

        engine = create_engine(connection_string)
        return engine

    except OperationalError as e:
        raise RuntimeError(f"An error occurred while connecting to Redshift: {str(e)}")


def load_data_to_redshift(df_json, table_name):
    """
    Load data from a JSON string into the specified Redshift table.

    Args:
        df_json (str): Data in JSON format to be inserted.
        table_name (str): Name of the table to insert the data into.
    """
    df_dict = ast.literal_eval(df_json)
    df = pd.DataFrame.from_dict(df_dict)

    engine = connect_to_redshift_engine()

    try:
        df.to_sql(
            table_name,
            engine,
            schema="2024_diego_rojas_schema",
            if_exists="append",
            index=False,
        )
    except Exception as e:
        raise RuntimeError(
            f"An error occurred while loading data to Redshift: {str(e)}"
        )
