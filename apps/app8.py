import streamlit as st
import json
import itertools


dict_convertion_prefix = {
    "No campaign": "no_campaign",
    "Campaign": "campaign"
}


class UpdateInfoModel:
    def __init__(self) -> None:
        self.data_input = {}
        self.file_name = "models/model_info.json"
        self.json = self.read_json()

    def read_json(self):
        with open(self.file_name) as file:
            return json.load(file)

    def write_json(self, data):
        with open(self.file_name, 'w') as file:
            json.dump(data, file, indent=4)

    def edit_model_json(self, prefix, campaign_key, numbers_of_row, type):

        st.write(type)
        rows_number, cols_number = numbers_of_row, 2

        data_uploaded = []
        if dict_convertion_prefix[type] in self.json[prefix]["campaigns_list"][campaign_key]:
            for period in self.json[prefix]["campaigns_list"][campaign_key][dict_convertion_prefix[type]]:
                data_uploaded.append([period["start_date"], period["end_date"]])

        cols_inputs = []
        for i, item2 in itertools.zip_longest(range(rows_number), data_uploaded, fillvalue=None):
            cols = st.columns(cols_number)
            start_end_date = []
            for j in range(cols_number):
                key = f"{dict_convertion_prefix[type]}-{i}-{j}"
                if j == 0:
                    value_to_complete = item2[0] if item2 is not None else ""
                    if i == 0:
                        user_input = cols[j].text_input("Start date", key=key, value=value_to_complete)
                    else:
                        user_input = cols[j].text_input("", key=key, value=value_to_complete)
                elif j == 1:
                    value_to_complete = item2[1] if item2 is not None else ""
                    if i == 0:
                        user_input = cols[j].text_input("End date", key=key, value=value_to_complete)
                    else:
                        user_input = cols[j].text_input("", key=key, value=value_to_complete)
                else:
                    user_input = cols[j].text_input("", key=key)
                start_end_date.append(user_input)
            cols_inputs.append(start_end_date)
        self.data_input[dict_convertion_prefix[type]] = cols_inputs

    def button_to_refresh_model_info(self, prefix, campaign_key):
        if st.button("Actualizar"):
            no_campaign_model_info = []
            for nocampaigs in self.data_input["no_campaign"]:
                if nocampaigs[0] != "" and nocampaigs[1] != "":
                    no_campaign_model_info.append({
                        "start_date": nocampaigs[0],
                        "end_date": nocampaigs[1]
                    })
            self.json[prefix]["campaigns_list"][campaign_key]["no_campaign"] = no_campaign_model_info

            campaign_model_info = []
            for campaign in self.data_input["campaign"]:
                if campaign[0] != "" and campaign[1] != "":
                    campaign_model_info.append({
                        "start_date": campaign[0],
                        "end_date": campaign[1]
                    })
            self.json[prefix]["campaigns_list"][campaign_key]["campaign"] = campaign_model_info

            self.write_json(self.json)


def main():
    # Lógica de la primera aplicación
    st.markdown(
        '<h1 style="font-size: 34px;">Actualizacion de la información del modelo</h1>',
        unsafe_allow_html=True
    )

    update_info_model = UpdateInfoModel()

    json = update_info_model.read_json()
    keys_list_prefix = list(json.keys())
    prefix = st.sidebar.selectbox(
        "Seleccione el prefijo de la campaña que desea editar",
        keys_list_prefix
    )

    list_with_key_campaign = list(json[prefix]["campaigns_list"].keys())
    campaign_key = st.sidebar.selectbox(
        "Seleccione la campaña que desea editar",
        list_with_key_campaign
    )

    input_no_campaigns = st.sidebar.number_input(
        "Ingrese la cantidad de no campaigns",
        min_value=1,
        value=3
    )

    input_campaign = 1

    update_info_model.edit_model_json(
        prefix,
        campaign_key,
        input_no_campaigns,
        "No campaign"
    )
    update_info_model.edit_model_json(
        prefix,
        campaign_key,
        input_campaign,
        "Campaign"
    )
    update_info_model.button_to_refresh_model_info(prefix, campaign_key)


if __name__ == "__main__":
    main()
