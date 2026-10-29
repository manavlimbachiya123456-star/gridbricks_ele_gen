from __future__ import annotations

import numpy as np
import pandas as pd


def calculate_metrics(frame: pd.DataFrame) -> dict[str, float | int | None]:
    """Calculate accuracy metrics for rows containing forecast and actual MW."""
    if frame.empty:
        return {
            "mae": None, "rmse": None, "mape": None, "bias": None,
            "mean_actual": None, "mean_forecast": None, "valid_intervals": 0,
            "matched_intervals": 0, "expected_intervals": 0, "coverage_pct": 0.0,
            "missing_forecast": 0, "missing_actual": 0, "duplicate_intervals": 0,
        }

    expected = int(frame["start_time"].nunique()) if "start_time" in frame else len(frame)
    valid = frame.dropna(subset=["forecast", "actual"]).copy()
    if valid.empty:
        result = calculate_metrics(pd.DataFrame())
        result["expected_intervals"] = expected
        result["coverage_pct"] = 0.0 if expected else 100.0
        return result

    signed = valid["forecast"] - valid["actual"]
    absolute = signed.abs()
    non_zero = valid["actual"] != 0
    pct = (absolute[non_zero] / valid.loc[non_zero, "actual"].abs()) * 100
    missing_forecast = int(frame["forecast"].isna().sum())
    missing_actual = int(frame["actual"].isna().sum())
    duplicates = int(frame.duplicated("start_time").sum()) if "start_time" in frame else 0
    return {
        "mae": float(absolute.mean()),
        "rmse": float(np.sqrt(np.mean(np.square(signed)))),
        "mape": float(pct.mean()) if not pct.empty else None,
        "bias": float(signed.mean()),
        "mean_actual": float(valid["actual"].mean()),
        "mean_forecast": float(valid["forecast"].mean()),
        "valid_intervals": int(len(valid)),
        "matched_intervals": int(len(valid)),
        "expected_intervals": expected,
        "coverage_pct": float(len(valid) / expected * 100) if expected else 0.0,
        "missing_forecast": missing_forecast,
        "missing_actual": missing_actual,
        "duplicate_intervals": duplicates,
    }

