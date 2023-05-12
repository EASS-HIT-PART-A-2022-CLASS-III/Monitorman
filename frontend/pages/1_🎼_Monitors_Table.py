import os
from dotenv import load_dotenv
import pandas as pd
import requests
import streamlit as st

load_dotenv('./frontend/.env')

st.set_page_config(page_title="Monitors", page_icon="🎼")

st.title("Monitors")

monitors = requests.get(
    f'{os.getenv("BACKEND_URL")}/monitors/v1/getmonitors/false').json()

for monitor in monitors:
    del monitor['results']

df = pd.DataFrame(data=monitors)

st.dataframe(df)

# delete_action = delete_col.button(
#     'Delete', key='table_button_delete_'+monitor['_id'])

# if delete_action:
#     requests.delete(
#         f'{os.getenv("BACKEND_URL")}/monitors/v1/{monitor["_id"]}')
#     st.experimental_rerun()

# trigger_col = cols[-1].empty()

# trigger_action = trigger_col.button(
#     'Trigger', key='table_button_trigger_'+monitor['_id'])

# if trigger_action:
#     requests.get(
#         f'{os.getenv("SCHEDULER_URL")}/scheduler/v1/{monitor["_id"]}')
