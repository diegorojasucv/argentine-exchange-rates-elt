import ast
import psycopg2
import pandas as pd


def connect_to_db(db_config):
    """
    Establish a connection to the PostgreSQL database.

    Args:
        db_config (dict): Configuration for connecting to the database.

    Returns:
        conn: Connection object.
        cursor: Cursor object for executing queries.
    """
    conn = psycopg2.connect(
        host=db_config["host"],
        port=db_config["port"],
        database=db_config["dbname"],
        user=db_config["user"],
        password=db_config["password"],
    )
    cursor = conn.cursor()
    cursor.execute(f"SET search_path TO {db_config['schema']};")
    return conn, cursor


def create_table_if_not_exists(cursor, table_name, table_schema):
    """
    Create a table if it does not already exist in the database.

    Args:
        cursor: Cursor object for executing the query.
        table_name (str): The name of the table to create.
        table_schema (str): The schema definition for the table.
    """
    create_table_query = f"CREATE TABLE IF NOT EXISTS {table_name} ({table_schema});"
    cursor.execute(create_table_query)


def insert_data_to_table(cursor, insert_query, data):
    """
    Insert data into a PostgreSQL table.

    Args:
        cursor: Cursor object for executing the query.
        insert_query (str): SQL insert query.
        data (list): Data to be inserted in the form of a list of tuples.
    """
    cursor.executemany(insert_query, data)


def load_prices_to_postgres(df_json, db_config, table_name, table_schema, insert_query):
    """
    Insert DataFrame data into a specified PostgreSQL table.

    Args:
        df_json (str): Data in JSON format to be inserted.
        db_config (dict): Configuration for connecting to the database.
        table_name (str): Name of the table to insert the data into.
        table_schema (str): Schema definition of the table.
        insert_query (str): SQL query for inserting the data.
    """

    df_dict = ast.literal_eval(df_json)
    df = pd.DataFrame.from_dict(df_dict)

    # Connect to the database
    conn, cursor = connect_to_db(db_config)

    # Create the table if it does not exist
    create_table_if_not_exists(cursor, table_name, table_schema)
    conn.commit()

    # Insert the data into the table
    data_to_insert = [tuple(row) for row in df.itertuples(index=False, name=None)]
    insert_data_to_table(cursor, insert_query, data_to_insert)
    conn.commit()

    # Close the connection
    cursor.close()
    conn.close()


# Function to load USDT prices
def load_usdt_prices_to_postgres(df_json, db_config):
    """
    Insert USDT-ARS price data into the usdt_ars_prices table in PostgreSQL.

    Args:
        df_json (str): USDT price data in JSON format.
        db_config (dict): Database connection configuration.
    """
    table_name = "usdt_ars_prices"
    table_schema = """
        exchange_name VARCHAR NOT NULL,
        ask_price DECIMAL(18, 8) NOT NULL,
        total_ask_price DECIMAL(18, 8) NOT NULL,
        bid_price DECIMAL(18, 8) NOT NULL,
        total_bid_price DECIMAL(18, 8) NOT NULL,
        updated_at TIMESTAMP NOT NULL,
        extracted_at TIMESTAMP NOT NULL
    """
    insert_query = """
        INSERT INTO usdt_ars_prices (exchange_name, ask_price, total_ask_price, bid_price, total_bid_price, updated_at, extracted_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    load_prices_to_postgres(df_json, db_config, table_name, table_schema, insert_query)


# Function to load MEP prices
def load_mep_prices_to_postgres(df_json, db_config):
    """
    Insert MEP price data into the mep_ars_prices table in PostgreSQL.

    Args:
        df_json (str): MEP price data in JSON format.
        db_config (dict): Database connection configuration.
    """
    table_name = "mep_ars_prices"
    table_schema = """
        mep_name VARCHAR NOT NULL,
        price DECIMAL(18, 8) NOT NULL,
        updated_at TIMESTAMP NOT NULL,
        extracted_at TIMESTAMP NOT NULL
    """
    insert_query = """
        INSERT INTO mep_ars_prices (mep_name, price, updated_at, extracted_at)
        VALUES (%s, %s, %s, %s)
    """
    load_prices_to_postgres(df_json, db_config, table_name, table_schema, insert_query)


# Function to load other dollar prices
def load_other_prices_to_postgres(df_json, db_config):
    """
    Insert other USD prices datas into the other_ars_prices table in PostgreSQL.

    Args:
        df_json (str): Other USD prices data in JSON format.
        db_config (dict): Database connection configuration.
    """
    table_name = "other_ars_prices"
    table_schema = """
        other_name VARCHAR NOT NULL,
        price DECIMAL(18, 8) NOT NULL,
        ask_price DECIMAL(18, 8) NOT NULL,
        bid_price DECIMAL(18, 8) NOT NULL,
        updated_at TIMESTAMP NOT NULL,
        extracted_at TIMESTAMP NOT NULL
    """
    insert_query = """
        INSERT INTO other_ars_prices (other_name, price, ask_price, bid_price, updated_at, extracted_at)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    load_prices_to_postgres(df_json, db_config, table_name, table_schema, insert_query)


# Function to load BCRA indicators
def load_bcra_prices_to_postgres(df_json, db_config):
    """
    Insert BCRA indicators data into the bcra_indicators table in PostgreSQL.

    Args:
        df_json (str): BCRA indicator data in JSON format.
        db_config (dict): Database connection configuration.
    """
    table_name = "bcra_indicators"
    table_schema = """
        id_variable INTEGER NOT NULL,
        cd_serie INTEGER NOT NULL,
        descripcion VARCHAR NOT NULL,
        valor DECIMAL(18, 8) NOT NULL,
        updated_at TIMESTAMP NOT NULL,
        extracted_at TIMESTAMP NOT NULL
    """
    insert_query = """
        INSERT INTO bcra_indicators (id_variable, cd_serie, descripcion, valor, updated_at, extracted_at)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    load_prices_to_postgres(df_json, db_config, table_name, table_schema, insert_query)
