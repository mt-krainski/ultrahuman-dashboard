from datetime import datetime

import pandas as pd
import plotly.express as px
import streamlit as st
from ultrahuman_api import get

st.title("Ultrahuman Ring Air Enhanced Dashboard")

data = get(datetime(2025, 3, 6)).data.temp

# Convert the List[ValueTimestamp] object to a pandas dataframe
df = pd.DataFrame(
    [
        {"value": vt.value, "timestamp": datetime.fromtimestamp(vt.timestamp)}
        for vt in data.values
    ]
)

# Display the dataframe
fig = px.line(df, x="timestamp", y="value", title="Temperature Over Time")
fig.update_yaxes(range=[20, 45])
st.plotly_chart(fig)


data = get(datetime(2025, 3, 1)).data.hr

# Convert the List[ValueTimestamp] object to a pandas dataframe
df = pd.DataFrame(
    [
        {"value": vt.value, "timestamp": datetime.fromtimestamp(vt.timestamp)}
        for vt in data.values
    ]
)

# Display the dataframe
fig = px.line(df, x="timestamp", y="value", title="Heart Rate Over Time")
fig.update_yaxes(range=[40, 180])
st.plotly_chart(fig)
