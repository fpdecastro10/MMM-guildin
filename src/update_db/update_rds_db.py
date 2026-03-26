import pandas as pd
from sqlalchemy import create_engine, text
import os


# Source database (existing env vars — same remote MySQL as always)
HOSTS = os.getenv("HOSTS")
USERS = os.getenv("USERS")
PWDS = os.getenv("PWDS")
NAME_DATABASES = os.getenv("NAME_DATABASES")
PORTS = os.getenv("PORTS", "3306")

# RDS destination database (new env vars from .env.rds)
RDS_HOST = os.getenv("RDS_HOST")
RDS_USER = os.getenv("RDS_USER")
RDS_PASSWORD = os.getenv("RDS_PASSWORD")
RDS_DATABASE = os.getenv("RDS_DATABASE")
RDS_PORT = os.getenv("RDS_PORT", "3306")


TABLES_RDS = [
    'asignador_store_groups',
    'asignador_store_groups_productos',
    'asignador_store_groups_productos_campaign',
    'asignador_store_groups_productos_stores',
    'importador_monedas',
    'importador_paises',
    'importador_productos',
    'importador_retailers',
    'importador_sales',
    'importador_sales_broncolin_sell_out',
    'importador_sales_cicloferon_sell_out',
    'importador_sales_colageina_sell_out',
    'importador_sales_emulsion_sell_out',
    'importador_sales_jaloma_sell_out',
    'importador_sales_jalomaarnica_sell_out',
    'importador_sales_leonflax_sell_out',
    'importador_sales_manzanillasophia_sell_out',
    'importador_sales_picot_sell_out',
    'importador_sales_redoxon_sell_out',
    'importador_sales_santanaturaglucontrol_sell_out',
    'importador_sales_santanaturayovitalmujer_sell_out',
    'importador_sales_splash_sell_out',
    'importador_sales_subway_sell_out',
    'importador_sales_suerooral_sell_out',
    'importador_sales_shampoocrec_sell_out',
    'importador_stores'
]

TABLES_SALES_RDS = [
    'importador_sales_broncolin_sell_out',
    'importador_sales_cicloferon_sell_out',
    'importador_sales_colageina_sell_out',
    'importador_sales_emulsion_sell_out',
    'importador_sales_jaloma_sell_out',
    'importador_sales_jalomaarnica_sell_out',
    'importador_sales_leonflax_sell_out',
    'importador_sales_manzanillasophia_sell_out',
    'importador_sales_picot_sell_out',
    'importador_sales_redoxon_sell_out',
    'importador_sales_santanaturaglucontrol_sell_out',
    'importador_sales_santanaturayovitalmujer_sell_out',
    'importador_sales_splash_sell_out',
    'importador_sales_subway_sell_out',
    'importador_sales_suerooral_sell_out',
    'importador_sales_shampoocrec_sell_out'
]


def get_source_engine():
    return create_engine(
        f'mysql+pymysql://{USERS}:{PWDS}@{HOSTS}:{PORTS}/{NAME_DATABASES}'
    )


def get_rds_engine():
    return create_engine(
        f'mysql+pymysql://{RDS_USER}:{RDS_PASSWORD}@{RDS_HOST}:{RDS_PORT}/{RDS_DATABASE}'
    )


def _map_error(table_name: str, e: Exception) -> str:
    msg = str(e).lower()
    if "packet sequence number" in msg or "lost connection" in msg or "connection" in msg:
        return (
            f"{table_name}: No se pudo conectar a la base de datos fuente. "
            "La conexión fue interrumpida — esto suele pasar cuando el servidor está ocupado "
            "o la red es inestable. Intentá de nuevo en unos minutos."
        )
    if "access denied" in msg:
        return f"{table_name}: Acceso denegado. Verificá las credenciales de la base de datos."
    if "timeout" in msg:
        return f"{table_name}: Tiempo de conexión agotado. El servidor tardó demasiado en responder."
    return f"{table_name}: Ocurrió un error inesperado. Detalle técnico: {e}"


def copy_table_to_rds(table_name) -> str:
    """Step 1 — copies a single table from source MySQL to RDS MySQL."""
    try:
        source_engine = get_source_engine()
        rds_engine = get_rds_engine()
        if table_name == 'importador_stores':
            df = pd.read_sql("""
                SELECT
                    CAST(id AS SIGNED) as id,
                    CAST(retailer_id AS SIGNED) as retailer_id,
                    CAST(store_id AS SIGNED) as store_id,
                    address, city, state, zip,
                    CAST(country AS SIGNED) as country,
                    customer_class, latitud, longitud,
                    status_latitud_longitud, time_stamp
                FROM importador_stores
            """, source_engine)
        else:
            df = pd.read_sql(f"SELECT * FROM {table_name}", source_engine)
        df.to_sql(name=table_name, con=rds_engine, if_exists='replace', index=False)
        return f"Tabla {table_name} copiada con éxito."
    except Exception as e:
        return _map_error(table_name, e)


def drop_importador_sales_all_rds():
    """Step 2a — drops importador_sales_all before rebuilding it."""
    try:
        rds_engine = get_rds_engine()
        with rds_engine.connect() as conn:
            conn.execute(text("DROP TABLE IF EXISTS importador_sales_all"))
            conn.commit()
        return 1
    except Exception as e:
        return 0


def copy_sales_table_to_sales_all(table_name):
    """Step 2b — appends one sales table into importador_sales_all.
    Note: jaloma is filtered to exclude sku_id=7, matching the original script logic."""
    try:
        rds_engine = get_rds_engine()

        if table_name == 'importador_sales_jaloma_sell_out':
            query = f"""
                SELECT id, store_id, retailer_id, country_id, sku_id, ISOweek,
                       sales, revenue, currency_id, pos_qty, id_store_id, time_stamp
                FROM {table_name} WHERE sku_id != 7
            """
        else:
            query = f"""
                SELECT id, store_id, retailer_id, country_id, sku_id, ISOweek,
                       sales, revenue, currency_id, pos_qty, id_store_id, time_stamp
                FROM {table_name}
            """

        df = pd.read_sql(query, rds_engine)
        df.to_sql(name='importador_sales_all', con=rds_engine, if_exists='append', index=False)
        return f"Datos de {table_name} añadidos a importador_sales_all."
    except Exception as e:
        return _map_error(table_name, e)


def create_isa_table_rds():
    """Step 3 — creates isa_table, the aggregated table that Tableau reads."""
    try:
        rds_engine = get_rds_engine()
        with rds_engine.connect() as conn:
            conn.execute(text("DROP TABLE IF EXISTS isa_table"))
            conn.execute(text("""
                CREATE TABLE isa_table AS
                SELECT
                    ISOweek,
                    id_store_id,
                    retailer_id,
                    sku_id,
                    SUM(sales) AS weekly_sales
                FROM importador_sales_all
                GROUP BY ISOweek, id_store_id, retailer_id, sku_id
            """))
            conn.commit()
        return "Tabla isa_table creada con éxito. El dashboard de Tableau ya refleja los datos actualizados."
    except Exception as e:
        return _map_error("isa_table", e)
