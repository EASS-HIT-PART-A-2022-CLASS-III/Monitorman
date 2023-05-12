import os
import re
from dotenv import load_dotenv
import requests
import streamlit as st
import pandas as pd

load_dotenv("./frontend/.env")

st.set_page_config(page_title="Monitor Checks", page_icon="☑️")

st.title("Monitor Checks")


def get_monitors():
    return requests.get(f'{os.getenv("BACKEND_URL")}/monitors/v1/getmonitors/true').json()


def get_monitor_desc(monitor):
    return monitor["description"]


def result_to_color(res):
    return f'background-color: {"green" if res else "red"}'


def color_results(val):
    checked_with = val['checked_with']

    results = []
    results.append(result_to_color(
        val['status'] == checked_with['expected_status']))
    results.append('')
    results.append(result_to_color(checked_with['expected_max_duration_ms'] is None or
                                   val['duration_ms'] <= checked_with['expected_max_duration_ms']))

    results.append(result_to_color(checked_with['expected_result_regex'] is None or
                                   0 < len(re.findall(checked_with['expected_result_regex'], val['content'], re.DOTALL))))
    results.append(result_to_color(
        val['status'] == checked_with['expected_status']))
    results.append('')

    return results


monitors = get_monitors()

if len(monitors) == 0:
    st.warning('No monitor to check')
else:
    monitor_val = st.selectbox(
        "Monitor", monitors, format_func=get_monitor_desc)
    select_monitor = st.button('Select Monitor')

    if select_monitor:
        df = pd.DataFrame(data=monitor_val['results'])
        st.dataframe(df.style.apply(color_results, axis=1))
