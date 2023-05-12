import os
from dotenv import load_dotenv
import requests
import streamlit as st

load_dotenv('./frontend/.env')


st.set_page_config(page_title="Monitors", page_icon="🎼")

st.title("Monitors")

monitors = requests.get(
    f'{os.getenv("BACKEND_URL")}/monitors/getmonitors/false').json()

cols = st.columns((1, 2, 2, 1, 1, 1, 1, 1, 1, 1, 2))

fields = ["№", 'description', 'url', 'method', 'body', 'expected_status', 'expected_result_regex',
          'expected_headers_regex', 'max_duration_ms', 'minute_interval', 'action']

for col, field_name in zip(cols, fields):
    # header
    col.write(field_name)

for x, monitor in enumerate(monitors):
    cols = st.columns(
        (1, 2, 2, 1, 1, 1, 1, 1, 1, 1, 2))
    cols[0].write(x)  # index

    for col_index, col in enumerate(cols[1:-1]):
        col.write(monitor[fields[col_index+1]])

    actions_col = cols[-1].empty()
    delete_action = actions_col.button('Delete', key=monitor['_id'])

    if delete_action:
        requests.delete(
            f'{os.getenv("BACKEND_URL")}/monitors/{monitor["_id"]}')
        st.experimental_rerun()
