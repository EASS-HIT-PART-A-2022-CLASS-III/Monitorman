import os
from dotenv import load_dotenv
import pandas as pd
import requests
import streamlit as st

load_dotenv("./frontend/.env")

st.set_page_config(page_title="Monitors", page_icon="🎼")

st.title("Monitors")

monitors = requests.get(
    f'{os.getenv("BACKEND_URL")}/monitors/v1/getmonitors/false'
).json()

if len(monitors) == 0:
    st.warning("No monitors to display")
else:
    for monitor in monitors:
        del monitor["results"]
        del monitor["_id"]

    df = pd.DataFrame(data=monitors)
    st.dataframe(df)
