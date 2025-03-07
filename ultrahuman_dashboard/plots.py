from datetime import datetime, timedelta

import plotly.express as px

OVERNIGHT_PLOT_RANGE_START = datetime.combine(
    datetime.today() - timedelta(days=1), datetime.min.time()
) + timedelta(hours=22)
OVERNIGHT_PLOT_RANGE_END = datetime.combine(
    datetime.today(), datetime.min.time()
) + timedelta(hours=8)


def plot_overnight(df, title):

    return px.line(
        df[
            (df["timestamp"] > OVERNIGHT_PLOT_RANGE_START)
            & (df["timestamp"] < OVERNIGHT_PLOT_RANGE_END)
        ],
        x="timestamp",
        y="value",
        title=title,
    )


def stamp_bedtime_start(fig, today_metrics):
    fig.add_vline(
        x=today_metrics["bedtime_start"].timestamp() * 1000,
        line=dict(color="rgba(255, 215, 0, 0.5)", dash="dash"),
        annotation_text="Went to bed",
        annotation_position="top left",
    )


def stamp_fell_asleep(fig, today_metrics):
    fig.add_vline(
        x=(
            today_metrics["bedtime_start"] + today_metrics["time_to_fall_asleep"]
        ).timestamp()
        * 1000,
        line=dict(color="rgba(0, 139, 0, 0.5)", dash="dash"),
        annotation_text="Fell asleep",
        annotation_position="top right",
    )


def stamp_bedtime_end(fig, today_metrics):
    fig.add_vline(
        x=today_metrics["bedtime_end"].timestamp() * 1000,
        line=dict(color="rgba(255, 215, 0, 0.5)", dash="dash"),
        annotation_text="Got up",
        annotation_position="top right",
    )
