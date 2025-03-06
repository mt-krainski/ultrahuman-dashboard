"""
This module defines Pydantic models for the Ultrahuman Dashboard API response schema.

Classes:
    ValueTimestamp: Represents a value with a timestamp.
    HRObject: Represents heart rate data.
    TempObject: Represents temperature data.
    HRVObject: Represents heart rate variability data.
    StepsObject: Represents steps data.
    NightRHRObject: Represents night resting heart rate data.
    AvgSleepHRVObject: Represents average sleep heart rate variability data.
    GlucoseObject: Represents glucose data.
    SingleValueMetric: Represents a metric with a single value.
    SleepObject: Represents sleep data.
    Data: Represents the main data structure containing various metrics.
    UltrahumanApiResponse: Represents the API response structure.
"""

from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, model_validator


class ValueTimestamp(BaseModel):
    value: Union[int, float, None]
    timestamp: int


class HRObject(BaseModel):
    day_start_timestamp: int
    title: str
    values: List[ValueTimestamp]
    last_reading: int
    unit: str


class TempObject(BaseModel):
    day_start_timestamp: int
    title: str
    values: List[ValueTimestamp]
    last_reading: float
    unit: str


class HRVObject(BaseModel):
    day_start_timestamp: int
    title: str
    values: List[ValueTimestamp]
    subtitle: str
    avg: int
    trend_title: Optional[str] = None
    trend_direction: Optional[str] = None


class StepsObject(BaseModel):
    day_start_timestamp: int
    values: List[ValueTimestamp]
    subtitle: str
    total: float
    avg: float
    trend_title: Optional[str] = None
    trend_direction: Optional[str] = None


class NightRHRObject(BaseModel):
    day_start_timestamp: int
    title: str
    values: List[ValueTimestamp]
    subtitle: str
    avg: int
    trend_title: Optional[str] = None
    trend_direction: Optional[str] = None


class AvgSleepHRVObject(BaseModel):
    value: int
    day_start_timestamp: int


class GlucoseObject(BaseModel):
    day_start_timestamp: int
    title: str
    values: List[ValueTimestamp]


# For metrics that simply have a day_start_timestamp, title, and a single value.
class SingleValueMetric(BaseModel):
    day_start_timestamp: int
    title: Optional[str] = None
    value: Optional[Union[int, float]]


class SleepObject(BaseModel):
    bedtime_start: int
    bedtime_end: int
    quick_metrics: List[Any]
    quick_metrics_tiled: List[Any]
    sleep_stages: List[Any]
    sleep_graph: Dict[str, Any]
    movement_graph: Dict[str, Any]
    hr_graph: Dict[str, Any]
    hrv_graph: Dict[str, Any]
    temp_graph: Dict[str, Any]
    respiratory_graph: Optional[Any]
    summary: List[Any]
    sleep_inertia_trend: Dict[str, Any]
    sleep_inertia_interpretation: Dict[str, Any]
    score_trend: Dict[str, Any]
    index_tracking_params: List[Any]
    spo2: Optional[Dict[str, Any]] = None
    toss_turn: Dict[str, Any]
    sleep_cycles: Dict[str, Any]


class Data(BaseModel):
    hr: Optional[HRObject] = None
    temp: Optional[TempObject] = None
    hrv: Optional[HRVObject] = None
    steps: Optional[StepsObject] = None
    night_rhr: Optional[NightRHRObject] = None
    avg_sleep_hrv: Optional[AvgSleepHRVObject] = None
    sleep: Optional[SleepObject] = None
    glucose: Optional[GlucoseObject] = None
    metabolic_score: Optional[SingleValueMetric] = None
    glucose_variability: Optional[SingleValueMetric] = None
    average_glucose: Optional[SingleValueMetric] = None
    hba1c: Optional[SingleValueMetric] = None
    time_in_target: Optional[SingleValueMetric] = None
    recovery_index: Optional[SingleValueMetric] = None
    movement_index: Optional[SingleValueMetric] = None
    vo2_max: Optional[SingleValueMetric] = None
    sleep_rhr: Optional[SingleValueMetric] = None

    @model_validator(mode="before")
    def transform_metric_data(self, values: Dict[str, Any]) -> Dict[str, Any]:
        """Transform metric_data from a list of objects to individual metric objects.

        Args:
            values (Dict[str, Any]): metric_data values

        Returns:
            Dict[str, Any]: new data structure
        """
        metric_list = values.get("metric_data")
        if isinstance(metric_list, list):
            for item in metric_list:
                metric_type = item.get("type")
                metric_obj = item.get("object")
                if metric_type and metric_obj is not None:
                    key = metric_type.lower()
                    values[key] = metric_obj
            values.pop("metric_data", None)
        return values


class UltrahumanApiResponse(BaseModel):
    data: Data
    error: Optional[Any]
    status: int
