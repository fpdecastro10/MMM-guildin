import streamlit as st
from src.update_db.update_local_db import update_db_local_guilding
from src.update_db.update_local_db import delete_table_importador_sales_all
from src.update_db.update_local_db import update_sales_all, create_sub_tables
from src.update_db.update_local_db import write_query_to_dataset
from src.update_db.update_local_db import TABLES, TABLES_SALES
from src.update_db.dict_queries import DATASET_DATE
import time


def update_db_local_with_each_table():
    placeholder = st.container().empty()
    index_progress = 0
    progress_bar = st.progress(index_progress)

    with placeholder:
        for table in TABLES:
            result = update_db_local_guilding(table)
            st.write(result)
            index_progress += 1
            progress_bar.progress(index_progress / len(TABLES))
            time.sleep(0.3)


def update_importador_sales_all():
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


def update_datasets():
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


def main():
    # Lógica de la primera aplicación
    imagen_local = './assets/img/logo2x.png'
    st.sidebar.image(imagen_local, use_column_width=True)
    st.markdown(
        '<h1 style="font-size: 34px;">Actualizacion Base de datos </h1>',
        unsafe_allow_html=True
    )

    if st.sidebar.button("Actualizar Base de Datos local"):
        update_db_local_with_each_table()

    if st.sidebar.button("Actualizar tabla de ventas"):
        update_importador_sales_all()

    if st.sidebar.button("Actualizar datasets"):
        update_datasets()


if __name__ == "__main__":
    main()
