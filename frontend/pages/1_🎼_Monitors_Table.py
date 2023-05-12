import os
from dotenv import load_dotenv
import requests
import streamlit as st

load_dotenv('./frontend/.env')


def get_columns():
    return st.columns((1, 2, 2, 1, 1, 1, 1, 1, 1, 1, 2, 2))


st.set_page_config(page_title="Monitors", page_icon="🎼")

st.title("Monitors")

monitors = requests.get(
    f'{os.getenv("BACKEND_URL")}/monitors/v1/getmonitors/false').json()

cols = get_columns()

fields = ["№", 'description', 'url', 'method', 'body', 'expected_status', 'expected_result_regex',
          'expected_headers_regex', 'expected_max_duration_ms', 'minute_interval', 'delete', 'trigger']

for col, field_name in zip(cols, fields):
    # header
    col.write(field_name)

for x, monitor in enumerate(monitors):
    cols = get_columns()
    cols[0].write(x)  # index

    for col_index, col in enumerate(cols[1:-2]):
        col.write(monitor[fields[col_index+1]])

    delete_col = cols[-2].empty()

    delete_action = delete_col.button(
        'Delete', key='table_button_delete_'+monitor['_id'])

    if delete_action:
        requests.delete(
            f'{os.getenv("BACKEND_URL")}/monitors/v1/{monitor["_id"]}')
        st.experimental_rerun()

    trigger_col = cols[-1].empty()

    trigger_action = trigger_col.button(
        'Trigger', key='table_button_trigger_'+monitor['_id'])

    if trigger_action:
        requests.get(
            f'{os.getenv("SCHEDULER_URL")}/scheduler/v1/{monitor["_id"]}')
