import streamlit as st
import time
import os
from src.update_db.update_rds_db import (
    copy_table_to_rds,
    drop_importador_sales_all_rds,
    copy_sales_table_to_sales_all,
    create_isa_table_rds,
    TABLES_RDS,
    TABLES_SALES_RDS
)


def run_full_update():
    # --- Step 1: Copy all tables from source to RDS ---
    st.markdown("#### Paso 1 de 3: Copiando tablas a AWS...")
    progress_bar_1 = st.progress(0)

    for i, table in enumerate(TABLES_RDS):
        st.write(copy_table_to_rds(table))
        progress_bar_1.progress((i + 1) / len(TABLES_RDS))
        time.sleep(0.1)

    # --- Step 2: Rebuild importador_sales_all ---
    st.markdown("#### Paso 2 de 3: Creando tabla importador_sales_all en AWS...")
    drop_importador_sales_all_rds()
    progress_bar_2 = st.progress(0)

    for i, table in enumerate(TABLES_SALES_RDS):
        st.write(copy_sales_table_to_sales_all(table))
        progress_bar_2.progress((i + 1) / len(TABLES_SALES_RDS))
        time.sleep(0.1)

    # --- Step 3: Create isa_table for Tableau ---
    st.markdown("#### Paso 3 de 3: Creando tabla isa_table en AWS...")
    st.write(create_isa_table_rds())

    st.success("✅ Base de datos de AWS actualizada exitosamente. Proceder a actualizar datos en Tableau: Fuente de datos -> isa_table -> Actualizar y Fuente de datos -> importador_sales_all -> Actualizar.")


def main():
    st.markdown(
        '<h1 style="font-size: 34px;">Actualizar Base de Datos de Tableau</h1>',
        unsafe_allow_html=True
    )

    st.write(
        "Al hacer clic en el botón se actualizará la base de datos en AWS conectada al "
        "dashboard de Tableau con los datos más recientes. Este proceso tarda varios minutos."
    )

    rds_configured = all([
        os.getenv("RDS_HOST"),
        os.getenv("RDS_USER"),
        os.getenv("RDS_PASSWORD"),
        os.getenv("RDS_DATABASE")
    ])

    if not rds_configured:
        st.error("⚠️ Las variables de entorno de RDS no están configuradas. Contacte al administrador.")
        return

    if st.button("🔄 Actualizar Tableau DB", help="Copia todos los datos al servidor AWS y regenera las tablas que usa Tableau."):
        run_full_update()


if __name__ == "__main__":
    main()
