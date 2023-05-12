import os
from dotenv import load_dotenv
import requests
import streamlit as st

load_dotenv("./frontend/.env")

st.set_page_config(page_title="Add Monitor", page_icon="🆕")

st.title("Add Monitor")

st.text_area("Description", key="add_description")
st.text_input("Url", key="add_url")
st.text_area("Body", key="add_body")
st.selectbox("Method", ["GET", "POST", "PUT", "DELETE"], key="add_method")
st.selectbox("Interval (Minutes)", [
             1, 2, 5, 10, 30, 60], key="add_minute_interval", index=2)
st.number_input("Expected Status", step=1, min_value=0, value=200, key="add_expected_status"
                )
st.text_input("Expected Result Regex", key="add_expected_result_regex")
st.number_input("Expected Max Duration(ms)", step=1, min_value=0,
                key="add_expected_max_duration_ms", value=10000)

# Every form must have a submit button.
submitted = st.button("Submit")

if submitted:

    send_obj = {}
    as_dict = st.session_state.to_dict()

    for key in as_dict:
        if key.startswith('add_'):
            if 'expected_' in key:
                if send_obj.get('checks') is None:
                    send_obj['checks'] = {}

                send_obj['checks'][key.removeprefix(
                    'add_')] = as_dict[key]
            else:
                send_obj[key.removeprefix('add_')] = as_dict[key]

    res = requests.post(
        f'{os.getenv("BACKEND_URL")}/monitors/v1', json=send_obj)

    if res.status_code == 201:
        st.success(f"Monitor added successfully", icon="✅")
    else:
        st.error(f"Failed to add monitor", icon="🚨")
