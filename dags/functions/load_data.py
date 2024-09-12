import ast
import pandas as pd
from airflow.models import Variable
from sqlalchemy import create_engine


def connect_to_redshift_engine():
    """
    Establish a connection to the Redshift database using SQLAlchemy.

    Returns:
        sqlalchemy.engine.Engine: SQLAlchemy engine for Redshift connection.
    """
    user = "2024_diego_rojas"
    password = Variable.get("redshift_password")
    host = "redshift-pda-cluster.cnuimntownzt.us-east-2.redshift.amazonaws.com"
    port = 5439
    dbname = "pda"

    connection_string = (
        f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}"
    )
    return create_engine(connection_string)


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

    df.to_sql(
        table_name,
        engine,
        schema="2024_diego_rojas_schema",
        if_exists="append",
        index=False,
    )
