import os
from dotenv import load_dotenv
import requests
import streamlit as st

load_dotenv("./frontend/.env")

st.set_page_config(page_title="Add Monitor", page_icon="🆕")

st.title("Add Monitor")

st.text_area("Description", key='description')
st.text_input("Url", key="url")
st.text_area("Body", key="body")
st.selectbox("Method", ["GET", "POST", "PUT", "DELETE"], key='method')
st.selectbox("Interval (Minutes)", [
             1, 2, 5, 10, 30, 60], key='minute_interval', index=2)
st.number_input("Expected Status", step=1, min_value=0, value=200, key='expected_status'
                )

# Every form must have a submit button.
submitted = st.button("Submit")

if submitted:
    res = requests.post(
        f'{os.getenv("BACKEND_URL")}/monitors/v1', json=st.session_state.to_dict()
    )

    if res.status_code == 201:
        st.success(f"Monitor added successfully", icon="✅")
    else:
        st.error(f"Failed to add monitor", icon="🚨")
