import streamlit as st


def main():

    app_selection_1 = st.sidebar.selectbox(
        "",
        [
            "1. Actualización de la Base de datos",
            "2. Configuración periodos de campaña de SGs",
            "3. Entrenamiento de modelos"
        ]
    )

    if app_selection_1 == "1. Actualización de la Base de datos":
        from apps.app7 import main as app7_main
        app7_main()
    elif app_selection_1 == "2. Configuración periodos de campaña de SGs":
        from apps.app8 import main as app8_main
        app8_main()
    elif app_selection_1 == "3. Entrenamiento de modelos":
        from apps.app9 import main as app9_main
        app9_main()
