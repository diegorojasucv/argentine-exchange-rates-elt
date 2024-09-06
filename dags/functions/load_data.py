import ast
import psycopg2
import pandas as pd


def load_data_to_postgres(df_json, db_config):
    """
    Inserta los datos de un DataFrame en la tabla usdt_ars_prices de PostgreSQL.
    Si la tabla no existe, la crea.

    Args:
        dataframe (pd.DataFrame): Datos que se insertarán en la tabla.
        db_config (dict): Configuración para conectarse a la base de datos.
    """

    df_dict = ast.literal_eval(df_json)
    df = pd.DataFrame.from_dict(df_dict)

    # Conexión a la base de datos
    conn = psycopg2.connect(
        host=db_config["host"],
        port=db_config["port"],
        database=db_config["dbname"],
        user=db_config["user"],
        password=db_config["password"],
    )
    cursor = conn.cursor()

    cursor.execute(f"SET search_path TO {db_config['schema']};")

    # Crear la tabla si no existe
    create_table_query = """
    CREATE TABLE IF NOT EXISTS usdt_ars_prices (
        exchange_name VARCHAR NOT NULL,
        ask_price DECIMAL(18, 8) NOT NULL,
        total_ask_price DECIMAL(18, 8) NOT NULL,
        bid_price DECIMAL(18, 8) NOT NULL,
        total_bid_price DECIMAL(18, 8) NOT NULL,
        updated_at TIMESTAMP NOT NULL,
        extracted_at TIMESTAMP NOT NULL
    );
    """

    cursor.execute(create_table_query)
    conn.commit()

    # Insertar los datos en la tabla
    insert_query = """
    INSERT INTO usdt_ars_prices (exchange_name, ask_price, total_ask_price, bid_price, total_bid_price, updated_at, extracted_at)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """

    # Convertir el DataFrame a una lista de tuplas
    data_to_insert = [tuple(row) for row in df.itertuples(index=False, name=None)]

    cursor.executemany(insert_query, data_to_insert)
    conn.commit()

    # Cerrar la conexión
    cursor.close()
    conn.close()
