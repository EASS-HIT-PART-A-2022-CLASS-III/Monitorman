import os
from dotenv import load_dotenv
import requests
import streamlit as st

load_dotenv("./frontend/.env")

st.set_page_config(page_title="Update Monitor", page_icon="🆙")

st.title("Update Monitor")

monitors = requests.get(
    f'{os.getenv("BACKEND_URL")}/monitors/v1/getmonitors/false').json()


def get_monitor_desc(monitor):
    return monitor["description"]


def reset_initialized():
    del st.session_state['initialized']


monitor_val = st.selectbox(
    "Monitor", monitors, format_func=get_monitor_desc, on_change=reset_initialized)

if monitor_val is None:
    st.warning('No monitor to update')
else:
    if 'initialized' not in st.session_state:
        st.session_state['initialized'] = True

        for key in monitor_val:
            st.session_state[key] = monitor_val[key]

    st.text_area("Description", key='description')
    st.text_input("Url", key="url")
    st.text_area("Body", key="body")
    st.selectbox("Method", ["GET", "POST", "PUT", "DELETE"], key='method')
    st.selectbox("Interval (Minutes)", [
        1, 2, 5, 10, 30, 60], key='minute_interval')

    st.number_input("Expected Status", step=1, min_value=0, value=200, key='expected_status'
                    )

    # Every form must have a submit button.
    submitted = st.button("Submit")

    if submitted:
        res = requests.put(
            f'{os.getenv("BACKEND_URL")}/monitors/v1/{monitor_val["_id"]}',
            json=st.session_state.to_dict(),
        )

        if res.status_code == 200:
            st.success(f"Monitor updated successfully", icon="✅")
        else:
            st.error(f"Failed to update monitor", icon="🚨")
