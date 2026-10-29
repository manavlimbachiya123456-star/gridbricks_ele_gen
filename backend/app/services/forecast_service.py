from __future__ import annotations

from datetime import datetime, time, timezone
import pandas as pd


def normalize_timestamp(value: str | datetime) -> pd.Timestamp:
    timestamp = pd.Timestamp(value)
    if timestamp.tzinfo is None:
        timestamp = timestamp.tz_localize("UTC")
    return timestamp.tz_convert("UTC")


def select_latest_forecasts(forecasts: pd.DataFrame, cutoff: time = time(12, 0)) -> pd.DataFrame:
    """Select the latest version published by the configurable UTC cutoff.

    The default assumption is 12:00 UTC on the day before delivery. A row is
    eligible when its publication timestamp is <= delivery_date - 1 day at cutoff.
    """
    if forecasts.empty:
        return forecasts.copy()
    work = forecasts.copy()
    work["start_time"] = work["start_time"].map(normalize_timestamp)
    work["publish_time"] = work["publish_time"].map(normalize_timestamp)
    cutoffs = work["start_time"].map(
        lambda ts: pd.Timestamp.combine((ts - pd.Timedelta(days=1)).date(), cutoff).tz_localize("UTC")
    )
    eligible = work[work["publish_time"] <= cutoffs].copy()
    if eligible.empty:
        return eligible
    return (eligible.sort_values("publish_time")
            .drop_duplicates("start_time", keep="last")
            .sort_values("start_time")
            .reset_index(drop=True))


def match_forecast_actuals(
    forecasts: pd.DataFrame, actuals: pd.DataFrame, cutoff: time = time(12, 0)
) -> pd.DataFrame:
    selected = select_latest_forecasts(forecasts, cutoff)
    actual = actuals.copy()
    if not actual.empty:
        actual["start_time"] = actual["start_time"].map(normalize_timestamp)
        actual = actual.sort_values("publish_time").drop_duplicates("start_time", keep="last")
    result = pd.merge(
        selected[["start_time", "publish_time", "forecast"]] if not selected.empty else
        pd.DataFrame(columns=["start_time", "publish_time", "forecast"]),
        actual[["start_time", "actual"]] if not actual.empty else
        pd.DataFrame(columns=["start_time", "actual"]),
        on="start_time", how="outer",
    ).sort_values("start_time").reset_index(drop=True)
    if not result.empty:
        result["signed_error"] = result["forecast"] - result["actual"]
        result["absolute_error"] = result["signed_error"].abs()
        result["percentage_error"] = result["absolute_error"].div(result["actual"].abs()).where(result["actual"] != 0) * 100
    return result

