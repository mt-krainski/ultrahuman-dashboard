"""This module provides functions to create and annotate plots using Plotly."""

from datetime import datetime, timedelta

import pandas as pd
import plotly.express as px
from plotly.graph_objs import Figure

from ultrahuman_dashboard.schemas import ParsedData


def plot_overnight(df: pd.DataFrame, title: str) -> Figure:
    """
    Plot an overnight line chart using the provided DataFrame.

    Args:
        df (pandas.DataFrame): The DataFrame containing the data to be plotted.
            It must have columns 'timestamp' and 'value'.
        title (str): The title of the plot.

    Returns:
        Figure: The generated line plot.
    """
    overnight_plot_range_start = datetime.combine(
        datetime.today() - timedelta(days=1), datetime.min.time()
    ) + timedelta(hours=22)
    overnight_plot_range_end = datetime.combine(
        datetime.today(), datetime.min.time()
    ) + timedelta(hours=8)
    fig = px.line(
        df[
            (df["timestamp"] > overnight_plot_range_start)
            & (df["timestamp"] < overnight_plot_range_end)
        ],
        x="timestamp",
        y="value",
        title=title,
    )
    fig.update_xaxes(range=[overnight_plot_range_start, overnight_plot_range_end])
    return fig


def stamp_bedtime_start(fig: Figure, today_metrics: ParsedData) -> None:
    """
    Add a vertical line to the given figure at the timestamp of bedtime start.

    Args:
        fig (Figure): The figure to which the vertical line will be added.
        today_metrics (ParsedData): A dictionary containing today's metrics.
    """
    fig.add_vline(
        x=today_metrics["bedtime_start"].timestamp() * 1000,
        line={"color": "rgba(255, 215, 0, 0.5)", "dash": "dash"},
        annotation_text="Went to bed",
        annotation_position="top left",
    )


def stamp_fell_asleep(fig: Figure, today_metrics: ParsedData) -> None:
    """
    Add a vertical line to the figure indicating the time the user fell asleep.

    Args:
        fig (Figure): The figure to which the vertical line will be added.
        today_metrics (ParsedData): A dictionary containing today's metrics.
    """
    fig.add_vline(
        x=(
            today_metrics["bedtime_start"] + today_metrics["time_to_fall_asleep"]
        ).timestamp()
        * 1000,
        line={"color": "rgba(0, 139, 0, 0.5)", "dash": "dash"},
        annotation_text="Fell asleep",
        annotation_position="top right",
    )


def stamp_bedtime_end(fig: Figure, today_metrics: ParsedData) -> None:
    """
    Add a vertical line to the figure indicating the end of bedtime.

    Args:
        fig (Figure): The figure to which the vertical line will be added.
        today_metrics (ParsedData): A dictionary containing today's metrics.
    """
    fig.add_vline(
        x=today_metrics["bedtime_end"].timestamp() * 1000,
        line={"color": "rgba(255, 215, 0, 0.5)", "dash": "dash"},
        annotation_text="Got up",
        annotation_position="top right",
    )
