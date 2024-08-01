import pandas as pd
import streamlit as st
from src.commons.functions import obtener_fecha_domingo
from src.commons.functions import df_builder_tablaMedio, optuna_optimize
import json
import os
import pickle
from prophet import Prophet
from sklearn.model_selection import TimeSeriesSplit


data_whole_sg_wp = pd.read_csv('datasets/datasetCampignSalesNew.csv')
data_whole_sg_wp["concat_store_group_name"] = data_whole_sg_wp["store_group_id"].astype(str) + " - " + data_whole_sg_wp["name"]
data_whole_sg_wp['tabla_medio'] = data_whole_sg_wp['tabla_medio'].fillna('No Campaign')
data_whole_sg_wp['cost_campaign'] = data_whole_sg_wp['cost_campaign'].fillna(0)
data_whole_sg_wp["yearweek"] = data_whole_sg_wp["yearweek"].fillna("-")
data_whole_sg_wp['ISOweek'] = data_whole_sg_wp['ISOweek'].astype(str)
data_whole_sg_wp = data_whole_sg_wp[data_whole_sg_wp['ISOweek'].str.len() > 4]
data_whole_sg_wp["ISOweek_wf"]=data_whole_sg_wp["ISOweek"]
data_whole_sg_wp["ISOweek"]=data_whole_sg_wp["ISOweek"].apply(obtener_fecha_domingo)

list_group = [
        "concat_store_group_name",
        "tabla_medio",
        "ISOweek",
        "ISOweek_wf",
        "yearweek",
        "campaign"
    ]
dict_group = {
    'cost_campaign': 'sum',
    'sales': 'mean'
}

data_whole_sg = df_builder_tablaMedio(data_whole_sg_wp, list_group, dict_group)
data_whole_sg_columns = data_whole_sg.columns.tolist()
data_whole_sg_columns.remove('No Campaign')
table_pivoted = data_whole_sg[data_whole_sg_columns]


def train_model(campaign_key, sg_key):

    try:
        prefix = campaign_key.split("_")[0].replace(" ", "")

        model_info_file = 'models/model_info.json'
        with open(model_info_file, "r") as archivo:
            model_info = json.load(archivo)

        parameters_sg = 'models/parameter_sg.json'
        with open(parameters_sg, "r") as archivo:
            params_adstock = json.load(archivo)

        store_group_df = table_pivoted[
            table_pivoted['concat_store_group_name'] == sg_key
        ]

        store_group_df['ISOweek_wf'] = store_group_df['ISOweek_wf'].astype(int)
        period_time_campaign = model_info[prefix]["campaigns_list"][campaign_key]
        no_campaign_periods = period_time_campaign["no_campaign"]
        campaign_period = period_time_campaign["campaign"]

        columns_tablapivoted = table_pivoted.columns
        store_group_result = pd.DataFrame(columns=columns_tablapivoted)
        if no_campaign_periods != []:
            for period in no_campaign_periods:
                start_date = int(period['start_date'])
                end_date = int(period['end_date'])
                df_campaign_part = store_group_df.query("ISOweek_wf >= @start_date and ISOweek_wf <= @end_date")
                store_group_result = pd.concat(
                    [store_group_result, df_campaign_part],
                    ignore_index=True
                )
        if campaign_period != []:
            for period in campaign_period:
                start_date = int(period['start_date'])
                end_date = int(period['end_date'])
                df_campaign_part = store_group_df.query("ISOweek_wf >= @start_date and ISOweek_wf <= @end_date")
                store_group_result = pd.concat(
                    [store_group_result, df_campaign_part],
                    ignore_index=True
                )

        table_prophet_sg = store_group_result.rename(
            columns={'sales': 'y', 'ISOweek': 'ds'}
        )[['ds', 'y', 'concat_store_group_name']]

        table_prophet_index = table_prophet_sg[['ds', 'y']]

        if os.path.exists(f"models/trained_models/{sg_key}.pkl"):
            os.remove(f"models/trained_models/{sg_key}.pkl")

        st.write("📊 Optimizando modelo 🔍")
        prophet = Prophet(yearly_seasonality=True)
        prophet.fit(table_prophet_index)
        with open(f"models/{sg_key}.pkl", 'wb') as f:
            pickle.dump(prophet, f)
        prophet_predict = prophet.predict(table_prophet_index)

        final_data_store_group = store_group_result.copy().reset_index()
        final_data_store_group['trend'] = prophet_predict['trend']
        final_data_store_group['season'] = prophet_predict['yearly']

        target = 'sales'
        data_sg = data_whole_sg_wp[
            data_whole_sg_wp['concat_store_group_name'] == sg_key
        ]
        media_channels = data_sg['tabla_medio'].unique().tolist()
        if 'No Campaign' in media_channels:
            media_channels.remove('No Campaign')
        features = ['trend','season'] + media_channels

        for tabla_medio in media_channels:
            final_data_store_group[tabla_medio] = final_data_store_group[tabla_medio].fillna(0)
        final_data_store_group

        final_data_store_group_wi = final_data_store_group.drop("index",axis=1)

        adstock_features_params = {}
        # Colocamos los parámetros de adstock
        adstock_features_params['Google Weekly_adstock'] = (0.3, 0.8)
        adstock_features_params['Facebook Weekly_adstock'] = (0.1, 0.4)

        OPTUNA_TRIALS = 1000

        number_of_splits = 3
        optuna_optimize_state = True
        num_filas = final_data_store_group_wi.shape[0]
        while number_of_splits < 6 and optuna_optimize_state:
            try:

                test_size = min(15, num_filas // number_of_splits)
                tscv = TimeSeriesSplit(n_splits=number_of_splits, test_size=test_size)

                experiment = optuna_optimize(
                    trials=OPTUNA_TRIALS,
                    data=final_data_store_group_wi,
                    target=target,
                    features=features,
                    adstock_features=media_channels,
                    adstock_features_params=adstock_features_params,
                    media_features=media_channels,
                    tscv=tscv,
                    is_multiobjective=False
                )
                optuna_optimize_state = False
            except Exception as e:
                number_of_splits += 1

        params_adstock[sg_key] = {
            "adstock_alphas": experiment.best_trial.user_attrs["adstock_alphas"],
            "params": experiment.best_trial.user_attrs["params"]
        }
        st.write("✅ El modelo ha terminado de entrenarse.")
    except Exception as error:
        st.write(error)


def main():

    # Lógica de la primera aplicación
    imagen_local = './assets/img/logo2x.png'
    st.sidebar.image(imagen_local, use_column_width=True)

    st.markdown(
        '<h1 style="font-size: 34px;">Entrenamiento de modelos</h1>',
        unsafe_allow_html=True
    )

    list_campaign = table_pivoted['campaign'].unique().tolist()
    selected_campaign = st.sidebar.selectbox(
        "Seleccione la campaña donde pertenece el SG",
        list_campaign
    )

    table_pivoted_filtered = table_pivoted[
        table_pivoted['campaign'] == selected_campaign
    ]
    list_store_group = table_pivoted_filtered[
        'concat_store_group_name'
    ].unique().tolist()

    selected_sg = st.sidebar.selectbox(
        "Seleccione el SG para el cual quiere entrenar el modelo",
        list_store_group
    )

    if st.sidebar.button("Entrenar modelo"):
        train_model(selected_campaign, selected_sg)
