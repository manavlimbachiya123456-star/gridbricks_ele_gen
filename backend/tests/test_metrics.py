import pandas as pd
import pytest
from app.services.metrics import calculate_metrics


def test_metrics_known_values():
    frame = pd.DataFrame({"start_time": pd.date_range("2026-01-01", periods=2, freq="h"), "forecast": [110, 90], "actual": [100, 100]})
    result = calculate_metrics(frame)
    assert result["mae"] == pytest.approx(10)
    assert result["rmse"] == pytest.approx(10)
    assert result["mape"] == pytest.approx(10)
    assert result["bias"] == pytest.approx(0)
    assert result["coverage_pct"] == pytest.approx(100)


def test_zero_actual_excluded_from_mape_and_missing_counted():
    frame = pd.DataFrame({"start_time": pd.date_range("2026-01-01", periods=2, freq="h"), "forecast": [10, None], "actual": [0, 20]})
    result = calculate_metrics(frame)
    assert result["mape"] is None
    assert result["missing_forecast"] == 1

