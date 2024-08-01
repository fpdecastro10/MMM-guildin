# Importamos la librerias que hacen falta
import pandas as pd
import mysql.connector
from sqlalchemy import create_engine
import sqlite3
import csv
import os


HOSTS = os.getenv("HOSTS")
USERS = os.getenv("USERS")
PWDS = os.getenv("PWDS")
NAME_DATABASES = os.getenv("NAME_DATABASES")
PORTS = os.getenv("PORTS")


TABLES = [
    "importador_sales_tables",
    "asignador_store_groups",
    "asignador_store_groups_productos",
    "asignador_store_groups_productos_campaign",
    "asignador_store_groups_productos_stores",
    "importador_monedas",
    "importador_paises",
    "importador_productos",
    "importador_retailers",
    "importador_sales",
    "importador_sales_broncolin_sell_out",
    "importador_sales_cicloferon_sell_out",
    "importador_sales_colageina_sell_out",
    "importador_sales_emulsion_sell_out",
    "importador_sales_jaloma_sell_out",
    "importador_sales_jalomaarnica_sell_out",
    "importador_sales_leonflax_sell_out",
    "importador_sales_manzanillasophia_sell_out",
    "importador_sales_picot_sell_out",
    "importador_sales_redoxon_sell_out",
    "importador_sales_santanaturaglucontrol_sell_out",
    "importador_sales_santanaturayovitalmujer_sell_out",
    "importador_sales_splash_sell_out",
    "importador_sales_subway_sell_out",
    "importador_sales_suerooral_sell_out",
    "importador_sales_shampoocrec_sell_out",
    "importador_stores",
    "supermetrics_data_facebook_weekly",
    "supermetrics_data_google_weekly"
]
TABLES_SALES = [
    "importador_sales_broncolin_sell_out",
    "importador_sales_cicloferon_sell_out",
    "importador_sales_colageina_sell_out",
    "importador_sales_emulsion_sell_out",
    "importador_sales_jaloma_sell_out",
    "importador_sales_jalomaarnica_sell_out",
    "importador_sales_leonflax_sell_out",
    "importador_sales_manzanillasophia_sell_out",
    "importador_sales_picot_sell_out",
    "importador_sales_redoxon_sell_out",
    "importador_sales_santanaturaglucontrol_sell_out",
    "importador_sales_santanaturayovitalmujer_sell_out",
    "importador_sales_splash_sell_out",
    "importador_sales_subway_sell_out",
    "importador_sales_shampoocrec_sell_out",
    "importador_sales_suerooral_sell_out"
]


def update_db_local_guilding(table_name):
    # Configuración de la conexión a la base de datos de destino

    source_config = {
        "host": HOSTS,
        "user": USERS,
        "password": PWDS,
        "database": NAME_DATABASES,
        "port":PORTS,
        
    }

    source_connector = mysql.connector.connect(**source_config)
    source_cursor = source_connector.cursor()

    # Tables to update
    # Create a local sqlite3 database
    sink_connection = sqlite3.connect('database_guilding_local.db')
    sink_cursor = sink_connection.cursor()
    sink_engine = create_engine(
        'sqlite:///database_guilding_local.db',
        echo=False
    )

    try:
        exist_table = f'''
            SELECT *
            FROM sqlite_master
            WHERE type = 'table' AND name = '{table_name}';
        '''
        sink_cursor.execute(exist_table)
        bool_is_none = sink_cursor.fetchone()

        if bool_is_none is not None:
            query_count = f"SELECT COUNT(*) FROM {table_name}"

            sink_cursor.execute(query_count)
            count_sink = sink_cursor.fetchone()[0]

            source_cursor.execute(query_count)
            count_source = source_cursor.fetchone()[0]

            if count_sink != count_source:
                query = f'''
                    SELECT *
                    FROM {table_name}
                '''
                df = pd.read_sql(query, source_connector)
                df.to_sql(
                    name=table_name,
                    con=sink_engine,
                    if_exists='replace',
                    index=False
                )
        else:
            query = f'''
                SELECT *
                FROM {table_name}
            '''
            df = pd.read_sql(query, source_connector)
            df.to_sql(
                name=table_name,
                con=sink_engine,
                if_exists='replace',
                index=False
            )

        return f"Datos de {table_name} transferidos con éxito."

    except Exception as e:
        return e


def delete_table_importador_sales_all():

    sink_connection = sqlite3.connect('database_guilding_local.db')
    sink_cursor = sink_connection.cursor()
    try:
        query_drop_sales_all = "DROP TABLE importador_sales_All"
        sink_cursor.execute(query_drop_sales_all)
        return 1
    except Exception as e:
        print(f"Error: {e}")
        return 0


def update_sales_all(table_name):

    sink_connection = sqlite3.connect('database_guilding_local.db')
    sink_engine = create_engine(
        'sqlite:///database_guilding_local.db',
        echo=False
    )

    query = f"""
        SELECT
            id,
            store_id,
            retailer_id,
            country_id,
            sku_id,
            ISOweek,
            sales,
            revenue,
            currency_id,
            pos_qty,
            id_store_id,
            time_stamp
        FROM {table_name}
    """
    df = pd.read_sql(query, sink_connection)

    df.to_sql(
        name='importador_sales_All',
        con=sink_engine,
        if_exists='append',
        index=False
    )
    sink_connection.close()
    return f"Datos transmitidos con éxitos de la tabla {table_name}"


def create_sub_tables():

    sink_connection = sqlite3.connect('database_guilding_local.db')
    sink_engine = create_engine(
        'sqlite:///database_guilding_local.db',
        echo=False
    )

    list_sub_tables = [
        [
            'campaignUnionsView',
            '''
            select
                id,
                yearweek,
                account,
                account_id,
                campaign_name,
                campaign_id,
                currency,
                impressions,
                ctr,
                cpc,
                cpm,
                cost,
                media,
                time_stamp,
                link_clicks as clicks,
                cost_website_convertions as cost_convertion
            from supermetrics_data_facebook_weekly
            union
            select
                id,
                yearweek,
                account,
                account_id,
                campaign_name,
                campaign_id,
                currency,
                impressions,
                ctr,
                cpc,
                cpm,
                cost,
                media,
                time_stamp,
                 clicks,
                cost_per_convertion
            from supermetrics_data_google_weekly
            '''
        ]
    ]

    for sub_table in list_sub_tables:
        df = pd.read_sql(sub_table[1], sink_connection)
        df.to_sql(
            name=sub_table[0],
            con=sink_engine,
            if_exists='replace',
            index=False
        )

    sink_connection.close()


def write_query_to_dataset(data_dataset):

    csv_file_name = data_dataset["name"]
    path_to_dataset = "datasets/"+csv_file_name

    with open(path_to_dataset, "w", newline="", encoding="utf-8") as f:
        f.write(data_dataset["header"])

    with sqlite3.connect('database_guilding_local.db') as sink_connection:
        sink_cursor = sink_connection.cursor()

        # Ejecutar la consulta y obtener los resultados
        sink_cursor.execute(data_dataset["query"])
        result = sink_cursor.fetchall()

    with open(path_to_dataset, "a", newline="", encoding="utf-8") as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerows(result)
        # Write the query data
        return f"Data has been successfully written to {csv_file_name}."
