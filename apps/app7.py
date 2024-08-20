import streamlit as st
from src.update_db.update_local_db import update_db_local_guilding
from src.update_db.update_local_db import delete_table_importador_sales_all
from src.update_db.update_local_db import update_sales_all, create_sub_tables
from src.update_db.update_local_db import write_query_to_dataset
from src.update_db.update_local_db import TABLES, TABLES_SALES
from src.update_db.dict_queries import DATASET_DATE
import time
import requests
import os

def get_public_ip():
    try:
        response = requests.get('https://api.ipify.org?format=json')
        response.raise_for_status()  # Verifica que la solicitud fue exitosa
        ip_info = response.json()
        return ip_info['ip']
    except requests.RequestException as e:
        print(f"Error obteniendo la IP pública: {e}")
        return None


def update_db_local_with_each_table():
    placeholder = st.container().empty()
    index_progress = 0
    progress_bar = st.progress(index_progress)
    try:
        with placeholder:
            for table in TABLES:
                result = update_db_local_guilding(table)
                st.write(result)
                index_progress += 1
                progress_bar.progress(index_progress / len(TABLES))
                time.sleep(0.3)
    except Exception as e:
        st.write(f"Error: agregue el ip {get_public_ip()} a la lista de permitidos en el servidor")


def update_importador_sales_all():
    try:
        delete_table_importador_sales_all()

        placeholder = st.container().empty()
        index_progress = 0
        progress_bar = st.progress(index_progress)

        with placeholder:
            for table in TABLES_SALES:
                result = update_sales_all(table)
                st.write(result)
                index_progress += 1
                progress_bar.progress(index_progress / len(TABLES_SALES))
                time.sleep(0.3)
    except Exception as e:
        st.write(f"Error: No se pudo actualizar la tabla de ventas, debe actualizar la base de datos primero")


def update_datasets():
    try:
        create_sub_tables()
        placeholder = st.container().empty()
        index_progress = 0
        progress_bar = st.progress(index_progress)

        with placeholder:
            for table in DATASET_DATE:
                name = table["name"]
                st.write(f"Actualizando dataset {name}")
                result = write_query_to_dataset(table)
                st.write(f"Actualizando dataset {result}")
                index_progress += 1
                progress_bar.progress(index_progress / len(DATASET_DATE))
                time.sleep(0.3)
    except Exception as e:
        st.write(f"Error: No se pudo actualizar la tabla de ventas, debe actualizar la base de datos primero")

def main():
    # Lógica de la primera aplicación
    st.write("----------")
    st.write(os.getenv("HOSTS"))
    st.write(os.getenv("USERS"))
    st.write(os.getenv("PWDS"))
    st.write(os.getenv("NAME_DATABASES"))
    st.write(os.getenv("PORTS"))
    st.write("----------")
    st.markdown(
        '''
        <h1 style="font-size: 34px;">Actualización base de datos y datasets para reflejar nuevos cambios</h1>
        ''',
        unsafe_allow_html=True
    )

    if st.button(
        "Actualizar Base de Datos local",
        help="Añade los registros nuevos en la base de datos para reflejar cambios recientes o corregir errores."
    ):
        update_db_local_with_each_table()

    if st.button(
        "Actualizar tabla de ventas",
        help="Impacta los nuevos registros nuevos de tabla de ventas offline agregado por clientes."
    ):
        update_importador_sales_all()

    if st.button(
        "Actualizar datasets",
        help="Añade los registros nuevos del Dataset configurado para entrenar el modelo."
    ):
        update_datasets()


if __name__ == "__main__":
    main()
