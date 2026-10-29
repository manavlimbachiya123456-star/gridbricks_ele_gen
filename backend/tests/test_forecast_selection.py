import pandas as pd
from datetime import time
from app.services.forecast_service import normalize_timestamp, select_latest_forecasts, match_forecast_actuals


def test_selects_latest_forecast_before_cutoff():
    frame = pd.DataFrame({
        "start_time": ["2026-01-15T10:00:00Z"] * 3,
        "publish_time": ["2026-01-13T10:00:00Z", "2026-01-14T11:59:00Z", "2026-01-14T12:01:00Z"],
        "forecast": [80, 90, 100],
    })
    selected = select_latest_forecasts(frame, time(12, 0))
    assert selected.iloc[0]["forecast"] == 90


def test_normalizes_naive_and_aware_timestamps():
    assert normalize_timestamp("2026-01-01T00:00:00").tzinfo is not None
    assert normalize_timestamp("2026-01-01T01:00:00+01:00").hour == 0


def test_matching_keeps_actual_only_intervals_visible():
    forecasts = pd.DataFrame({"start_time": ["2026-01-15T10:00:00Z"], "publish_time": ["2026-01-14T11:00:00Z"], "forecast": [90]})
    actuals = pd.DataFrame({"start_time": ["2026-01-15T10:00:00Z", "2026-01-15T10:30:00Z"], "publish_time": ["2026-01-16T00:00:00Z"] * 2, "actual": [100, 120]})
    result = match_forecast_actuals(forecasts, actuals)
    assert len(result) == 2
    assert result["forecast"].isna().sum() == 1

