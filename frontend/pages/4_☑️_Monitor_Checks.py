import copy
import json
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
    return requests.get(
        f'{os.getenv("BACKEND_URL")}/monitors/v1/getmonitors/true'
    ).json()


def get_monitor_desc(monitor):
    return monitor["description"]


def result_to_color(res):
    return f'background-color: {"green" if res else "red"}'


def color_results(val):
    checked_with = val["checked_with"]

    results = []
    results.append(result_to_color(val["status"] == checked_with["expected_status"]))
    results.append("")
    results.append(
        result_to_color(
            checked_with["expected_max_duration_ms"] is None
            or val["duration_ms"] <= checked_with["expected_max_duration_ms"]
        )
    )

    results.append(
        result_to_color(
            checked_with["expected_result_regex"] is None
            or 0
            < len(
                re.findall(
                    checked_with["expected_result_regex"], val["content"], re.DOTALL
                )
            )
        )
    )

    results.append(
        result_to_color(
            checked_with["expected_headers_regex"] is None
            or 0
            < len(
                re.findall(
                    checked_with["expected_headers_regex"],
                    json.dumps(val["headers"]),
                    re.DOTALL,
                )
            )
        )
    )

    results.append("")

    return results


monitors = get_monitors()

if len(monitors) == 0:
    st.warning("No monitor to check")
else:
    monitor_val = st.selectbox("Monitor", monitors, format_func=get_monitor_desc)

    if monitor_val is not None:
        monitor_copy = copy.copy(monitor_val)

        del monitor_copy["_id"]
        del monitor_copy["results"]

    st.write(monitor_copy)

    cols = st.columns((1, 1, 1, 1))

    select_monitor = cols[0].button("Show Monitor Results")

    if select_monitor:
        results = monitor_val["results"]

        if len(results) == 0:
            st.warning("Monitor has no results yet")
        else:
            df = pd.DataFrame(data=results)
            st.dataframe(df.style.apply(color_results, axis=1))

    delete_val = cols[1].button("Delete Monitor")

    if delete_val:
        requests.delete(f'{os.getenv("BACKEND_URL")}/monitors/v1/{monitor_val["_id"]}')
        st.experimental_rerun()

    trigger_val = cols[2].button("Trigger Monitor")

    if trigger_val:
        requests.get(f'{os.getenv("SCHEDULER_URL")}/scheduler/v1/{monitor_val["_id"]}')
        st.experimental_rerun()

    clear_results_val = cols[3].button("Clear Monitor Results")

    if clear_results_val:
        requests.get(
            f'{os.getenv("BACKEND_URL")}/monitors/v1/clear_results/{monitor_val["_id"]}'
        )
        st.experimental_rerun()
