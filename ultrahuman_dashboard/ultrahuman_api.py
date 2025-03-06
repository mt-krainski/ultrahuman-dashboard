import os
from datetime import datetime

import requests

from ultrahuman_dashboard.schemas import UltrahumanApiResponse

ULTRAHUMAN_PARTNER_API = "https://partner.ultrahuman.com/api/v1/metrics"
ULTRAHUMAN_USER_EMAIL = os.environ.get("ULTRAHUMAN_USER_EMAIL")
ULTRAHUMAN_API_SECRET = os.environ.get("ULTRAHUMAN_API_SECRET")


def get(date: datetime):
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
