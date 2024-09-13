import streamlit as st
import os
import zipfile
from dotenv import load_dotenv
import subprocess

command = "cat .env.guilding | base64 --decode > .env"
subprocess.run(command, shell=True, capture_output=True, text=True)

load_dotenv(".env")

file_path = "datasets/dataset_to_detect_performance_of_stores.csv"
if not os.path.isfile(file_path):
    file_path_zip = "datasets/dataset_to_detect_performance_of_stores.csv" + ".zip"
    if os.path.isfile(file_path_zip):
        with zipfile.ZipFile(file_path_zip, 'r') as zip_ref:
            zip_ref.extractall("datasets/")


def main():
    st.title("Seleccione una aplicacion:")
    imagen_local = './assets/img/logo2x.png'
    st.sidebar.image(imagen_local, use_column_width=True)
    app_selection = st.selectbox(
        "",
        [
            "1. Inversión inicial y distribución de budget",
            "2. Predicción de sales + analytics seasonality, trend & media",
            "3. Tendencia de Ventas en Stores",
            "4. Predicción de sales - Regresión polinomial",
            "5. Actualización de la Base de datos, periódos de campaña y entrenamientos de modelos"
        ]
    )

    if app_selection == "4. Predicción de sales - Regresión polinomial":
        # Ejecutar la primera aplicación
        from apps.app1 import main as app1_main
        app1_main()
    elif app_selection == "3. Tendencia de Ventas en Stores":
        from apps.app3_4 import main as app3_4_main
        app3_4_main()
    elif app_selection == "1. Inversión inicial y distribución de budget":
        # from app5_copy import main as app5_main
        from apps.app5 import main as app5_main
        app5_main()
    elif app_selection == "2. Predicción de sales + analytics seasonality, trend & media":
        from apps.app6 import main as app6_main
        app6_main()
    elif app_selection == "5. Actualización de la Base de datos, periódos de campaña y entrenamientos de modelos":
        from apps.app789 import main as app789_main
        app789_main()


if __name__ == "__main__":
    main()
