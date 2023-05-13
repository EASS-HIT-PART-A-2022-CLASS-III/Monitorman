import os
from dotenv import load_dotenv
import requests
import streamlit as st

load_dotenv("./frontend/.env")

st.set_page_config(page_title="Update Monitor", page_icon="🆙")

st.title("Update Monitor")

monitors = requests.get(
    f'{os.getenv("BACKEND_URL")}/monitors/v1/getmonitors/false'
).json()


def get_monitor_desc(monitor):
    return monitor["description"]


def reset_initialized():
    del st.session_state["initialized"]


monitor_val = st.selectbox(
    "Monitor", monitors, format_func=get_monitor_desc, on_change=reset_initialized
)

if monitor_val is None:
    st.warning("No monitor to update")
else:
    if "initialized" not in st.session_state:
        st.session_state["initialized"] = True

        for key in monitor_val:
            if key == "checks":
                for check in monitor_val[key]:
                    if monitor_val[key][check] is not None:
                        st.session_state[f"update_{check}"] = monitor_val[key][check]
            else:
                st.session_state[f"update_{key}"] = monitor_val[key]

    st.text_area("Description", key="update_description")
    st.text_input("Url", key="update_url")
    st.text_area("Body", key="update_body")
    st.selectbox("Method", ["GET", "POST", "PUT", "DELETE"], key="update_method")
    st.selectbox(
        "Interval (Minutes)", [1, 2, 5, 10, 30, 60], key="update_minute_interval"
    )

    st.number_input(
        "Expected Status", step=1, min_value=0, key="update_expected_status"
    )
    st.text_input("Expected Result Regex", key="update_expected_result_regex")
    st.text_input("Expected Headers Regex", key="update_expected_headers_regex")

    st.number_input(
        "Expected Max Duration(ms)",
        step=1,
        min_value=0,
        key="update_expected_max_duration_ms",
    )

    # Every form must have a submit button.
    submitted = st.button("Submit")

    if submitted:
        send_obj = {}
        as_dict = st.session_state.to_dict()

        for key in as_dict:
            if key.startswith("update_"):
                if "expected_" in key:
                    if send_obj.get("checks") is None:
                        send_obj["checks"] = {}

                    send_obj["checks"][key.removeprefix("update_")] = as_dict[key]
                else:
                    send_obj[key.removeprefix("update_")] = as_dict[key]

        res = requests.put(
            f'{os.getenv("BACKEND_URL")}/monitors/v1/{monitor_val["_id"]}',
            json=send_obj,
        )

        if res.status_code == 200:
            st.success(f"Monitor updated successfully", icon="✅")
        else:
            st.error(f"Failed to update monitor", icon="🚨")
