from datetime import datetime, timedelta

import pandas as pd
import plotly.express as px
import streamlit as st
from ultrahuman_api import get

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
# - the number of nights of core sleep (5.5h+)
# - the number of insomnia nights
# - Sleep efficiency: time asleep / time in bed (90% is a good score)
# - how consistent is the wake up time (number of days you arise within half hour of
#    your desired time)
#
# Other notes:
# - Temperature drop
# - Sleep HR pattern (https://ouraring.com/blog/sleeping-heart-rate/?srsltid=AfmBOorjLb4HOEcb11rhBya2CIdSoPox-CZOM8B2phnxxG28qV2dE58f)
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
# - How many days of more-than-enough sleep (8h+)
# - Rising time consistency - what time did you wake up, is it consistent?

st.title("Ultrahuman Ring Air Enhanced Dashboard")

now = datetime.now()
today = now.date()
data = get(today - timedelta(days=1))

col1, col2, col3 = st.columns(3)

# previous_day_data = get(today - timedelta(days=2))
bedtime_start = datetime.fromtimestamp(data.data.sleep.bedtime_start)
bedtime_end = datetime.fromtimestamp(data.data.sleep.bedtime_end)
time_in_bed = bedtime_end - bedtime_start

prior_wakefulness_seconds = (now - bedtime_end).seconds
hours, remainder = divmod(prior_wakefulness_seconds, 3600)
minutes, _ = divmod(remainder, 60)
col3.metric("Prior wakefulness", f"{hours}h {minutes}m")

st.divider()

# Time to fall asleep
first_segment = data.data.sleep.sleep_graph["data"][0]
time_to_fall_asleep = 0
if first_segment["type"] == "awake":
    time_to_fall_asleep = first_segment["end"] - first_segment["start"]

col1, col2, col3 = st.columns(3)
col1.metric("Went to bed", bedtime_start.strftime("%H:%M"))
col2.metric("Got up", bedtime_end.strftime("%H:%M"))

col3.metric("Time to fall asleep", f"{round(time_to_fall_asleep / 60):d}m")

time_asleep = 0
awake_segments = []
for segment in data.data.sleep.sleep_graph["data"]:
    if segment["type"] != "awake":
        time_asleep += segment["end"] - segment["start"]
    else:
        awake_segments.append(segment["end"] - segment["start"])

col1, col2, col3 = st.columns(3)

hours, remainder = divmod(time_in_bed.total_seconds(), 3600)
minutes, _ = divmod(remainder, 60)
col1.metric("Time in bed", f"{int(hours)}h {int(minutes)}m")

hours, remainder = divmod(time_asleep, 3600)
minutes, _ = divmod(remainder, 60)
col2.metric("Time asleep", f"{int(hours)}h {int(minutes)}m")

sleep_efficiency = time_asleep / time_in_bed.total_seconds()
col3.metric("Sleep efficiency", f"{sleep_efficiency:.0%}")


col1, col2 = st.columns(2)
# Convert the List[ValueTimestamp] object to a pandas dataframe
df = pd.DataFrame(
    [
        {"value": vt.value, "timestamp": datetime.fromtimestamp(vt.timestamp)}
        for vt in data.data.temp.values
    ]
)

# Display the dataframe
fig = px.line(
    df[df["timestamp"] < bedtime_end],
    x="timestamp",
    y="value",
    title="Temperature Over Time",
)
fig.update_yaxes(range=[33, 38])
col1.plotly_chart(fig)

# Convert the List[ValueTimestamp] object to a pandas dataframe
df = pd.DataFrame(
    [
        {"value": vt.value, "timestamp": datetime.fromtimestamp(vt.timestamp)}
        for vt in data.data.hr.values
    ]
)

# Display the dataframe
fig = px.line(
    df[df["timestamp"] < bedtime_end],
    x="timestamp",
    y="value",
    title="Heart Rate Over Time",
)
fig.update_yaxes(range=[40, 100])
col2.plotly_chart(fig)
