from datetime import datetime, timedelta

import pandas as pd
import streamlit as st

from ultrahuman_dashboard.formatting import format_time, format_timedelta
from ultrahuman_dashboard.plots import (
    plot_overnight,
    stamp_bedtime_end,
    stamp_bedtime_start,
    stamp_fell_asleep,
)
from ultrahuman_dashboard.schemas import samples_to_df
from ultrahuman_dashboard.ultrahuman_api import get_from_ultrahuman_api, parse_data

# TODO: The questions from the Insomnia program sleep diary
# Daily notes:
# - What time did you get into bed? What time did you turn off the lights?
# - About how long did it take you to fall asleep?
# - How many times did you awaken during the night?
# - For each awakening, how long did it last?
# - What time was your final wake-up for the day? What time did you get out of bed?
# - How many hours did you sleep last night?
# - How many hours did you spend in bed last night?
# - How would you rate the quality of your sleep last night?
# - What time do you usually get into bed? Get out of bed?
# - Does the amount of time spent in bed exceed the amount of time you sleep?
#     By how much?
# - Do you have an inconsistent rising time or sleep later or weekends compared to
#     weekdays?
# - Do you nap? If yes - how many times per week, for how long
# - Prior wakefulness - how long are you awake; time between getting up and going to
#     sleep
#
# Weekly summary:
# - How many nights per week do you have difficulty falling asleep?
# - On these nights, how much time, on average, does it take you to fall asleep?
# - How many nights per week do you wake up and have difficulty falling back asleep?
# - On these nights, how often do you typically wake up?
# - On average, what is the total amount of time that you lie awake during the night
#   after these awakenings?
# - How many days per week is your final wake-up earlier than desired?
# - On nights when you have insomnia, how many hours on average do you sleep?
# - On nights when you don't have insomnia, how many hours on average do you sleep?
# - How many nights per week do you experience a good night of sleep?
# - How many nights per week do you take sleeping pills? Number of pills? Typical dose?
# - What is your average sleep quality rating on a scale of 1 to 5?
#
# Refreshed summary
# - the number of good nights of sleep
# - the number of nights of core sleep (5.5+ h)
# - the number of insomnia nights
# - Sleep efficiency: time asleep / time in bed (90% is a good score)
# - how consistent is the wake up time (number of days you arise within half hour of
#    your desired time)
#
# Other notes:
# - Temperature drop
# - Sleep HR pattern (https://ouraring.com/blog/sleeping-heart-rate/?srsltid=AfmBOorjLb4HOEcb11rhBya2CIdSoPox-CZOM8B2phnxxG28qV2dE58f)  # noqa: SC100,E501
#
#
# Daily Reports:
# - Time in bed - (from - to)
# - Time asleep - (from - to)
# - Sleep efficiency
# - How long it took to fall asleep
# - How many times you woke up, and for how long on average
# - Prior wakefulness - right now (how many hours since last wake up)
# - Temperature drop
# - Sleep HR pattern
#
# Weekly reports:
# - Time asleep
# - time to fall asleep
# - sleep efficiency
# - How many times you wake up during the night
# - How many days of effective sleep (sleep efficiency above 90%)
# - How many days of core sleep
# - How many days of more-than-enough sleep (8+ h)
# - Rising time consistency - what time did you wake up, is it consistent?

CORE_SLEEP_TIME = timedelta(hours=5, minutes=30)
PRIOR_WAKEFULNESS_TARGET = timedelta(hours=16)
SLEEP_EFFICIENCY_TARGET = 0.9


st.title("Ultrahuman Ring Air Enhanced Dashboard")

now = datetime.now()
today = now.date()
data = get_from_ultrahuman_api(today)
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
    delta=f"{today_metrics['sleep_efficiency_delta']:.0%}",
)


col1, col2 = st.columns(2)


df = samples_to_df(data.data.temp.values)
df_previous_day = samples_to_df(previous_day_data.data.temp.values)
df = pd.concat([df_previous_day, df])

fig = plot_overnight(df, "Temperature Over Time")
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
