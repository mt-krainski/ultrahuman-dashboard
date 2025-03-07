import os
from datetime import datetime, timedelta

import requests

from ultrahuman_dashboard.schemas import ParsedData, UltrahumanApiResponse

ULTRAHUMAN_PARTNER_API = "https://partner.ultrahuman.com/api/v1/metrics"
ULTRAHUMAN_USER_EMAIL = os.environ.get("ULTRAHUMAN_USER_EMAIL")
ULTRAHUMAN_API_SECRET = os.environ.get("ULTRAHUMAN_API_SECRET")

CORE_SLEEP_TIME = timedelta(hours=5, minutes=30)
PRIOR_WAKEFULNESS_TARGET = timedelta(hours=16)
SLEEP_EFFICIENCY_TARGET = 0.9


def get_from_ultrahuman_api(date: datetime):
    """Fetch data from the Ultrahuman Partner API for a specific date.

    Args:
        date (datetime): The date for which to fetch the data.

    Returns:
        UltrahumanApiResponse: The response from the Ultrahuman API, validated and
            parsed into an UltrahumanApiResponse object.
    """
    response = requests.get(
        ULTRAHUMAN_PARTNER_API,
        params={"date": date.strftime("%Y-%m-%d"), "email": ULTRAHUMAN_USER_EMAIL},
        headers={"Authorization": ULTRAHUMAN_API_SECRET},
        timeout=10,
    )

    response.raise_for_status()
    return UltrahumanApiResponse.model_validate(response.json())


def get_bedtime_start(data: UltrahumanApiResponse) -> datetime:
    """Return the bedtime start time."""
    return datetime.fromtimestamp(data.data.sleep.bedtime_start)


def get_bedtime_end(data: UltrahumanApiResponse) -> datetime:
    """
    Return the bedtime end time.

    This corrects for cases where user is awake but sleep graph is still counting sleep
    time.
    """
    bedtime_end = datetime.fromtimestamp(data.data.sleep.bedtime_end)
    for segment in reversed(data.data.sleep.sleep_graph["data"]):
        if segment["type"] == "awake":
            bedtime_end = datetime.fromtimestamp(segment["start"])
            continue

        segment_duration = segment["end"] - segment["start"]
        if segment_duration > 300:
            break

    return bedtime_end


def get_time_to_fall_asleep(data: UltrahumanApiResponse) -> timedelta:
    """
    Return the time to fall asleep.

    This is the time from bedtime to the first sleep segment of at least 5 minutes.
    """
    time_to_fall_asleep_s = 0
    for segment in data.data.sleep.sleep_graph["data"]:
        segment_duration = segment["end"] - segment["start"]
        if segment["type"] == "awake":
            time_to_fall_asleep_s += segment_duration
            continue

        if segment_duration > 300:
            break

        time_to_fall_asleep_s += segment_duration
    return timedelta(seconds=time_to_fall_asleep_s)


def get_time_asleep(data: UltrahumanApiResponse) -> timedelta:
    """
    Return the total time asleep.

    This is counted as total duration of non-awake segments.
    """
    time_asleep_s = 0
    for segment in data.data.sleep.sleep_graph["data"]:
        if segment["type"] != "awake":
            time_asleep_s += segment["end"] - segment["start"]
    return timedelta(seconds=time_asleep_s)


def parse_data(data: UltrahumanApiResponse) -> ParsedData:
    """Extract most useful data from the Ultrahuman API response."""
    now = datetime.now()
    bedtime_start = get_bedtime_start(data)
    bedtime_end = get_bedtime_end(data)
    time_in_bed = bedtime_end - bedtime_start
    prior_wakefulness = now - bedtime_end
    sleep_target = bedtime_end + PRIOR_WAKEFULNESS_TARGET
    time_to_fall_asleep = get_time_to_fall_asleep(data)
    time_asleep = get_time_asleep(data)
    core_sleep_delta = time_asleep - CORE_SLEEP_TIME
    sleep_efficiency = time_asleep.total_seconds() / time_in_bed.total_seconds()
    sleep_efficiency_delta = sleep_efficiency - SLEEP_EFFICIENCY_TARGET
    return {
        "bedtime_start": bedtime_start,
        "bedtime_end": bedtime_end,
        "time_in_bed": time_in_bed,
        "prior_wakefulness": prior_wakefulness,
        "sleep_target": sleep_target,
        "time_to_fall_asleep": time_to_fall_asleep,
        "time_asleep": time_asleep,
        "core_sleep_delta": core_sleep_delta,
        "sleep_efficiency": sleep_efficiency,
        "sleep_efficiency_delta": sleep_efficiency_delta,
    }
