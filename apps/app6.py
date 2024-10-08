import streamlit as st
import numpy as np
from src.mmm_shap import optuna_optimize, model_refit, shap_feature_importance
from src.mmm_shap import calculated_increment_sales, df_builder_tablaMedio
from src.mmm_shap import obtener_fecha_domingo
import matplotlib.pyplot as plt
import os
import pickle
from prophet import Prophet
import pandas as pd
from datetime import datetime, timedelta
import plotly.io as pio
from sklearn.metrics import r2_score
from sklearn.model_selection import TimeSeriesSplit
import json

st.set_option('deprecation.showPyplotGlobalUse', False)
pd.set_option('display.float_format', lambda x: '%.5f' % x)
np.set_printoptions(suppress=True)
np.set_printoptions(
    suppress=True,
    formatter={'float_kind': '{:16.3f}'.format},
    linewidth=130
)
pio.renderers.default = 'iframe'

if 'data_whole_sg_wp' in st.session_state:
    data_whole_sg_wp = st.session_state.data_whole_sg_wp
else:
    data_whole_sg_wp = pd.read_csv('datasetss/datasetCampignSalesNew.csv')
    data_whole_sg_wp['concat_store_group_name'] = data_whole_sg_wp["store_group_id"].astype(str) + " - " + data_whole_sg_wp["name"]
    # Completamos los valores nan en tabla medio con 'No Campaign'. Hay semanas donde se vendio pero no se le hizo campaigns.
    data_whole_sg_wp['tabla_medio'] = data_whole_sg_wp['tabla_medio'].fillna('No Campaign')
    # Completamos los costo de campaña con 0. En las semanas que no se hizo campañas
    data_whole_sg_wp['cost_campaign'] = data_whole_sg_wp['cost_campaign'].fillna(0)
    # Cuando no tenemos información de semanas, le agregamos "-"
    data_whole_sg_wp["yearweek"] = data_whole_sg_wp["yearweek"].fillna("-")
    data_whole_sg_wp['ISOweek'] = data_whole_sg_wp['ISOweek'].astype(str)
    # Eliminamos los valores de semanas que solo tienen el año
    data_whole_sg_wp = data_whole_sg_wp[data_whole_sg_wp['ISOweek'].str.len() > 4]
    data_whole_sg_wp["ISOweek"]=data_whole_sg_wp["ISOweek"].apply(obtener_fecha_domingo)
    st.session_state.data_whole_sg_wp = data_whole_sg_wp

if 'table_pivoted_r' in st.session_state:
    table_pivoted_r = st.session_state.table_pivoted_r
else:
    list_group = [ "concat_store_group_name", "tabla_medio", "ISOweek", "yearweek"]
    dict_group = {
        'cost_campaign': 'sum',
        'sales': 'mean'
    }
    data_whole_sg = df_builder_tablaMedio(data_whole_sg_wp,list_group,dict_group)
    data_whole_sg_columns = data_whole_sg.columns.tolist()
    data_whole_sg_columns.remove('No Campaign')
    # Eliminas las columnas 'No Campaign'
    table_pivoted_r = data_whole_sg[data_whole_sg_columns]
    st.session_state.table_pivoted_r = table_pivoted_r

list_store_group = table_pivoted_r['concat_store_group_name'].unique().tolist()

file_json = 'models/parameter_sg.json'


def shap_values(shap_values, data, figsize=(20, 10)):

    feature_list = data.columns

    if not isinstance(shap_values, pd.DataFrame):
        shap_v = pd.DataFrame(shap_values)
        shap_v.columns = feature_list
    else:
        shap_v = shap_values

    df_v = data.copy().reset_index().drop('index', axis=1)

    # Determine the correlation in order to plot with different colors
    corr_list = list()
    for i in feature_list:
        b = np.corrcoef(shap_v[i], df_v[i])[1][0]
        corr_list.append(b)
    corr_df = pd.concat([
        pd.Series(feature_list), pd.Series(corr_list)], axis=1
    ).fillna(0)
    # Make a data frame. Column 1 is the feature, and Column 2 is the correlation coefficient
    corr_df.columns = ['Variable', 'Corr']
    corr_df['Sign'] = np.where(corr_df['Corr'] > 0, 'red', 'blue')

    # Plot it
    shap_abs = np.abs(shap_v)
    k = pd.DataFrame(shap_abs.mean()).reset_index()
    k.columns = ['Variable', 'SHAP_abs']

    return k


def info_shap_value(dataframe_shap, features):
    list_msg = []
    if len(features) == 2:
        list_msg.append("El store group no tiene asignación de campañas")
    list_post = []
    list_neg = []
    for index, row in dataframe_shap.iterrows():
        if row['Variable'] == 'trend' or row['Variable'] == 'season':
            continue
        else:
            name_variable = row['Variable'].replace(" Weekly", "")
            if row['SHAP_abs'] > 0:
                list_post.append(name_variable)
            else:
                list_neg.append(name_variable)

    if len(list_post) == 2:
        list_msg.append(f"Los medios {list_post[0]} y {list_post[1]} influye positivamente en las ventas")
    if len(list_post) == 1:
        list_msg.append(f"Los medios {list_post[0]} influye positivamente en las ventas")

    if len(list_neg) == 2:
        list_msg.append(f"Los medios {list_neg[0]} y {list_neg[1]} no explican en las ventas")
    if len(list_neg) == 1:
        list_msg.append(f"Los medios {list_neg[0]} no explica las ventas")

    return list_msg


def arbol_regressor(store_group_name):

    st.markdown(
        f"<h1 style='font-size: 34px;text-align:center'>{store_group_name}</h1>",
        unsafe_allow_html=True
    )

    table_pivoted_sg = table_pivoted_r[
        table_pivoted_r['concat_store_group_name'] == store_group_name
    ]
    table_prophet_sg = table_pivoted_sg.rename(
        columns={'sales': 'y', 'ISOweek': 'ds'}
    )[
        ['ds', 'y', 'concat_store_group_name']
    ]

    table_prophet_index = table_prophet_sg[['ds', 'y']]

    if os.path.exists(f"models/trained_models/{store_group_name}.pkl"):
        with open(f"models/trained_models/{store_group_name}.pkl", 'rb') as f:
            prophet = pickle.load(f)
    else:
        prophet = Prophet(yearly_seasonality=True)
        prophet.fit(table_prophet_index)
        with open(f"models/trained_models/{store_group_name}.pkl", 'wb') as f:
            pickle.dump(prophet, f)

    prophet_predict = prophet.predict(table_prophet_index)
    final_data_store_group = table_pivoted_sg.copy().reset_index()
    final_data_store_group['trend'] = prophet_predict['trend']
    final_data_store_group['season'] = prophet_predict['yearly']

    target = 'sales'
    data_sg = data_whole_sg_wp[
        data_whole_sg_wp['concat_store_group_name'] == store_group_name
    ]
    media_channels = data_sg['tabla_medio'].unique().tolist()
    if 'No Campaign' in media_channels:
        media_channels.remove('No Campaign')
    features = ['trend', 'season'] + media_channels

    for tabla_medio in media_channels:
        final_data_store_group[tabla_medio] = final_data_store_group[tabla_medio].fillna(0)
    final_data_store_group

    # se creearan tres divisiones
    tscv = TimeSeriesSplit(n_splits=3, test_size=20)

    adstock_features_params = {}
    # Colocamos los parámetros de adstock
    adstock_features_params['Google Weekly_adstock'] = (0.3, 0.8)
    adstock_features_params['Facebook Weekly_adstock'] = (0.1, 0.4)

    final_data_store_group_wi = final_data_store_group.drop("index", axis=1)

    with open(file_json, "r") as archivo:
        params_adstock = json.load(archivo)

    if store_group_name not in params_adstock:

        OPTUNA_TRIALS = 1000
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

        params_adstock[store_group_name] = {
            "adstock_alphas": experiment.best_trial.user_attrs["adstock_alphas"],
            "params": experiment.best_trial.user_attrs["params"]
        }

        best_params = experiment.best_trial.user_attrs["params"]
        adstock_params = experiment.best_trial.user_attrs["adstock_alphas"]

        best_params = params_adstock[store_group_name]["params"]
        adstock_params = params_adstock[store_group_name]["adstock_alphas"]

        with open(file_json, "w") as archivo:
            json.dump(params_adstock, archivo, indent=4)
    else:
        best_params = params_adstock[store_group_name]["params"]
        adstock_params = params_adstock[store_group_name]["adstock_alphas"]

    START_ANALYSIS_INDEX = round(final_data_store_group_wi.shape[0] * 0)
    END_ANALYSIS_INDEX = round(final_data_store_group_wi.shape[0] * 1)

    result = model_refit(
        data=final_data_store_group_wi,
        target=target,
        features=features,
        media_channels=media_channels,
        model_params=best_params,
        adstock_params=adstock_params,
        start_index=START_ANALYSIS_INDEX,
        end_index=END_ANALYSIS_INDEX
    )

    r2_metric = r2_score(y_true=result["y_true_interval"], y_pred=result["prediction_interval"])

    st.markdown(
        """
        <h3 style='font-size: 25px;margin-top:30px;margin-bottom:15px'>
                Evolución de ventas: Real vs Predicción
        </h3>
        """,
        unsafe_allow_html=True
    )

    fig, ax = plt.subplots(figsize=(20, 10))
    etiquetas_mostradas = result["x_input_interval_nontransformed"]['ISOweek'][::20]
    _ = ax.plot(result['x_input_interval_nontransformed']['ISOweek'], result["prediction_interval"], color="blue", label="predicted")
    _ = ax.plot(result['x_input_interval_nontransformed']['ISOweek'], result["y_true_interval"], 'ro', label="true")
    _ = plt.title(f"R2: {np.round(r2_metric,3)}")
    _ = ax.legend()
    ax.set_xticks(etiquetas_mostradas)
    st.pyplot(fig)

    fig_shapp = shap_feature_importance(
        result["df_shap_values"],
        result["x_input_interval_transformed"]
    )
    st.markdown(
        """ <h3 style='font-size: 25px;margin-top:30px;margin-bottom:15px'>
                Gráfico de Importancia de Atributos con SHAP
            </h3>
        """,
        unsafe_allow_html=True
    )
    st.pyplot(fig_shapp)

    date_to_estimate = datetime.today()
    date_to_trashold = date_to_estimate - timedelta(days=1*30)
    isoweeek_serie = pd.to_datetime(final_data_store_group_wi['ISOweek'])
    data_store_filter_by_date = final_data_store_group_wi[isoweeek_serie > date_to_trashold]

    if not data_store_filter_by_date.empty:
        average_sales = data_store_filter_by_date['sales'].mean()
    else:
        date_to_estimate = max(isoweeek_serie) + timedelta(days=7)
        date_to_trashold = date_to_estimate - timedelta(days=1*30)
        data_store_filter_by_date = final_data_store_group_wi[isoweeek_serie > date_to_trashold]
        average_sales = data_store_filter_by_date['sales'].mean()

    st.markdown(
        """ <h3 style='font-size: 25px;margin-top:30px;margin-bottom:15px'>
                Resumen del store group
            </h3>""",
        unsafe_allow_html=True
    )

    shap_values_df = shap_values(result["df_shap_values"], result["x_input_interval_transformed"])
    for msg in info_shap_value(shap_values_df, features):
        st.write(msg)

    st.write(f"Promedio de ventas semanales: {round(average_sales)}")
    if media_channels != []:
        total_cost_campaign = 0
        for tabla_medio in media_channels:
            cost_tabla_medio = final_data_store_group_wi[final_data_store_group_wi[tabla_medio] > 0][tabla_medio].mean()
            name_variable = tabla_medio.replace(" Weekly", "")
            st.write(f"Promedio de inversión semanal {name_variable}: {round(cost_tabla_medio)}")
            total_cost_campaign += cost_tabla_medio

    st.markdown("<h3 style='font-size: 25px;margin-top:30px;margin-bottom:15px'>Predicción de ventas semanales</h3>", unsafe_allow_html=True)

    season = st.date_input("Seleccione la semana para la que desea predecir:", date_to_estimate)

    season_trend = pd.DataFrame({'ds': [season]})
    prohet_prediction = prophet.predict(season_trend)
    prediction_trend = prohet_prediction[['trend', 'yearly']].rename(columns={'yearly': 'season'})

    list_input = {}
    for tabla_medio in media_channels:
        name_variable = tabla_medio.replace(" Weekly", "")
        list_input[tabla_medio] = st.number_input(f"Seleccione el monto a invertir semanalmente en {name_variable}: ", value=0)

    if st.button("Predecir sales"):
        for key, value in list_input.items():
            prediction_trend[key] = value
        prediction = result["model"].predict(prediction_trend)
        prediction_str = f"La predicción de ventas es: {round(prediction[0])} un"
        st.markdown(f"<h3 style='font-size: 25px;margin-top:30px;margin-bottom:15px'>{prediction_str}</h3>", unsafe_allow_html=True)

    st.markdown("<h3 style='font-size: 25px;margin-top:30px;margin-bottom:15px'>Predicción de crecimiento porcentual</h3>", unsafe_allow_html=True)
    input_investment = st.number_input("Ingrese el crecimiento porcentual deseado por semana (%): ", value=0)

    if st.button("Predecir investment"):
        calculated_investment = calculated_increment_sales(
                                result['model'],
                                input_investment,
                                result['df_shap_values'],
                                result['x_input_interval_nontransformed'],
                                final_data_store_group_wi,
                                features)
        st.markdown(f"<p style='font-size: 25px;margin-top:30px;margin-bottom:15px'>{calculated_investment[0]}</p>", unsafe_allow_html=True)


def main():

    with st.sidebar:
        st.markdown(
            '<h1 style="font-size: 34px;">Filtros </h1>',
            unsafe_allow_html=True
        )

        campaing_store_group = data_whole_sg_wp['campaign'].unique().tolist()

        camaping_new_client = st.selectbox(
            "Seleccione el nombre de la campaña: ",
            campaing_store_group
        )

        list_store_group_campaign = data_whole_sg_wp.query(
            "campaign in @camaping_new_client"
        )["concat_store_group_name"].unique().tolist()

        camaping_new_client = st.selectbox(
            "Seleccione el Store Group:",
            list_store_group_campaign
        )

    arbol_regressor(camaping_new_client)
