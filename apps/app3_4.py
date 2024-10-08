
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from apps.app3 import main as app3_main
from apps.app4 import main as app4_main

plt.style.use({
    'axes.facecolor': '#0e1118',
    'axes.edgecolor': 'white',
    'axes.labelcolor': 'white',
    'text.color': 'white',
    'xtick.color': 'white',
    'ytick.color': 'white',
    'grid.color': '#0e1118',
    'figure.facecolor': '#0e1118',
    'figure.edgecolor': '#0e1118',
    'savefig.facecolor': '#0e1118',
    'savefig.edgecolor': '#1a1a1a',
})

data_sw = pd.read_csv("datasets/dataset_to_detect_performance_of_stores.csv")


unique_combinations = data_sw[
    ["id_storeGroup", "name_storeGroup", "campaign_storeGroup"]
].drop_duplicates(
    ["id_storeGroup", "name_storeGroup", "campaign_storeGroup"]
)
unique_combinations_campaign = unique_combinations[
    "campaign_storeGroup"
].drop_duplicates()
relations_storeGroup_products = data_sw[
    ["id_storeGroup", "sku_id"]
].drop_duplicates(["id_storeGroup", "sku_id"])


def main():
    with st.sidebar:
        st.markdown(
            '<h1 style="font-size: 34px;">Filtros </h1>',
            unsafe_allow_html=True
        )

        options = [
            "Stores con tendencia negativa",
            "Stores con tendencia positiva"
        ]

        app_selection = st.selectbox(
            "Seleccione la tendencia que desea analizar:",
            options
        )

    if app_selection == "Stores con tendencia negativa":
        app3_main()
    else:
        app4_main()
