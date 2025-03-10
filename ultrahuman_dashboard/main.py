from datetime import datetime, timedelta
from typing import List

import pandas as pd
import streamlit as st
from pydantic import ValidationError

from ultrahuman_dashboard.formatting import format_time, format_timedelta
from ultrahuman_dashboard.plots import (
    plot_overnight,
    stamp_bedtime_end,
    stamp_bedtime_start,
    stamp_fell_asleep,
)
from ultrahuman_dashboard.schemas import ParsedData, samples_to_df
from ultrahuman_dashboard.ultrahuman_api import get_from_ultrahuman_api, parse_data

HISTORICAL_DATA_RANGE = 28


st.set_page_config(page_title="Sleep Dashboard", layout="centered")

st.markdown(
    """
    <style>
        .stMainBlockContainer {
            margin-top: -5em;
        }
        #MainMenu {visibility: hidden;}
        .stAppDeployButton {display:none;}
        .stAppHeader {display:none;}
        footer {visibility: hidden;}
        #stDecoration {display:none;}
    </style>
""",
    unsafe_allow_html=True,
)

st.title("My Sleep Dashboard")
st.divider()

now = datetime.now()
today = now.date()
data = get_from_ultrahuman_api(now)
previous_day_data = get_from_ultrahuman_api(today - timedelta(days=1))

today_metrics = parse_data(data)


col1, col2, col3 = st.columns(3)
col2.metric("Prior wakefulness", format_timedelta(today_metrics["prior_wakefulness"]))
col3.metric("Sleep target", format_time(today_metrics["sleep_target"]))

st.divider()

col1, col2, col3 = st.columns(3)
col1.metric("Went to bed", format_time(today_metrics["bedtime_start"]))
col2.metric("Got up", format_time(today_metrics["bedtime_end"]))

col3.metric(
    "Time to fall asleep", format_timedelta(today_metrics["time_to_fall_asleep"])
)

col1, col2, col3 = st.columns(3)

col1.metric("Time in bed", format_timedelta(today_metrics["time_in_bed"]))

if today_metrics["core_sleep_delta"] < timedelta(0):
    col2.metric(
        "Time asleep",
        format_timedelta(today_metrics["time_asleep"]),
        delta=f"{format_timedelta(today_metrics['core_sleep_delta'])}",
    )
else:
    col2.metric("Time asleep", format_timedelta(today_metrics["time_asleep"]))

col3.metric(
    "Sleep efficiency",
    f"{today_metrics['sleep_efficiency']:.0%}",
    delta=(
        f"{today_metrics['sleep_efficiency_delta']:.0%}"
        if (
            today_metrics["sleep_efficiency_delta"] > 1
            or today_metrics["sleep_efficiency_delta"] < -1
        )
        else None
    ),
)

st.divider()

col1, col2 = st.columns(2)


df = samples_to_df(data.data.temp.values)
df_previous_day = samples_to_df(previous_day_data.data.temp.values)
df = pd.concat([df_previous_day, df])

fig = plot_overnight(df, "Temperature")
stamp_bedtime_start(fig, today_metrics)
stamp_fell_asleep(fig, today_metrics)
stamp_bedtime_end(fig, today_metrics)
fig.update_yaxes(range=[33, 38])
col1.plotly_chart(fig)


df = samples_to_df(data.data.hr.values)
df_previous_day = samples_to_df(previous_day_data.data.hr.values)
df = pd.concat([df_previous_day, df])

fig = plot_overnight(df, "Heart Rate")
stamp_bedtime_start(fig, today_metrics)
stamp_fell_asleep(fig, today_metrics)
stamp_bedtime_end(fig, today_metrics)

fig.update_yaxes(range=[40, 120])
col2.plotly_chart(fig)


historical_data: List[ParsedData] = []
with st.spinner(f"Loading data for the last {HISTORICAL_DATA_RANGE} days..."):
    progress_bar = st.progress(0)
    for day in range(HISTORICAL_DATA_RANGE, 1, -1):
        try:
            data = get_from_ultrahuman_api(today - timedelta(days=day))
        except ValidationError:
            continue
        historical_data.append(parse_data(data))
        progress_bar.progress(
            (HISTORICAL_DATA_RANGE - day) / (HISTORICAL_DATA_RANGE - 1)
        )

progress_bar.empty()

historical_data.append(parse_data(previous_day_data))
historical_data.append(today_metrics)

historical_data_df = pd.DataFrame(historical_data)
historical_data_df["time_asleep_h"] = (
    historical_data_df["time_asleep"].dt.total_seconds() / 3600
)
historical_data_df["time_to_fall_asleep_h"] = (
    historical_data_df["time_to_fall_asleep"].dt.total_seconds() / 3600
)

historical_data_df["bedtime_end_time"] = (
    historical_data_df["bedtime_end"].dt.hour
    + historical_data_df["bedtime_end"].dt.minute / 60
)

st.line_chart(historical_data_df, x="day", y="time_asleep_h")
st.line_chart(historical_data_df, x="day", y="time_to_fall_asleep_h")
st.line_chart(historical_data_df, x="day", y="sleep_efficiency")
st.line_chart(historical_data_df, x="day", y="bedtime_end_time")
