from __future__ import annotations

from datetime import datetime, time, timezone
import calendar
import json
import pandas as pd
from fastapi import APIRouter, HTTPException, Query

from app.schemas import AnalysisResponse, HealthResponse, HistoryResponse
from app.services.elexon_client import ElexonClient
from app.services.forecast_service import match_forecast_actuals, normalize_timestamp, select_latest_forecasts
from app.services.metrics import calculate_metrics

router = APIRouter(prefix="/api")
client = ElexonClient()


def month_bounds(month: str) -> tuple[datetime, datetime]:
    try:
        parsed = datetime.strptime(month, "%Y-%m").replace(tzinfo=timezone.utc)
    except ValueError as exc:
        raise HTTPException(422, "month must use YYYY-MM") from exc
    last = calendar.monthrange(parsed.year, parsed.month)[1]
    return parsed, parsed.replace(day=last, hour=23, minute=59, second=59)


async def build_analysis(month: str, cutoff: time = time(12, 0)) -> dict:
    start, end = month_bounds(month)
    try:
        actuals, forecasts = await __import__("asyncio").gather(
            client.fetch_actuals(start, end), client.fetch_forecasts(start, end)
        )
        rows = match_forecast_actuals(forecasts, actuals, cutoff)
        metrics = calculate_metrics(rows)
        return {
            "month": month, "decision_cutoff_utc": cutoff.strftime("%H:%M"),
            "source": "Elexon Insights API FUELHH/WINDFOR", "retrieval_status": "live",
            "limitation": "WINDFOR stream history is filtered by publication time; rows without an eligible version are excluded from matched metrics.",
            "metrics": metrics, "rows": json.loads(rows.to_json(orient="records", date_format="iso")) if not rows.empty else [],
        }
    except Exception as exc:
        raise HTTPException(502, f"Elexon API retrieval failed: {exc}") from exc


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(status="ok", service="uk-wind-forecast-api", data_source="Elexon Insights API")


@router.get("/forecast-analysis")
async def analysis(month: str = Query("2026-01"), cutoff_utc: str = Query("12:00")) -> dict:
    try:
        cutoff = time.fromisoformat(cutoff_utc)
    except ValueError as exc:
        raise HTTPException(422, "cutoff_utc must use HH:MM") from exc
    return await build_analysis(month, cutoff)


@router.get("/metrics")
async def metrics(month: str = Query("2026-01"), cutoff_utc: str = Query("12:00")) -> dict:
    result = await analysis(month, cutoff_utc)
    return {"month": result["month"], "decision_cutoff_utc": result["decision_cutoff_utc"], "metrics": result["metrics"]}


@router.get("/forecast-history")
async def history(start_time: str) -> dict:
    try:
        target = normalize_timestamp(start_time).to_pydatetime()
        forecasts = await client.fetch_forecast_history(target)
        forecasts["start_time"] = forecasts["start_time"].map(normalize_timestamp)
        target_ts = normalize_timestamp(start_time)
        rows = forecasts[forecasts["start_time"].eq(target_ts)].copy()
        cutoff = time(12, 0)
        decision = pd.Timestamp.combine((target_ts - pd.Timedelta(days=1)).date(), cutoff).tz_localize("UTC")
        if not rows.empty:
            rows["eligible"] = rows["publish_time"].map(normalize_timestamp) <= decision
            rows["decision_cutoff_utc"] = decision.isoformat()
        return {"start_time": target_ts.isoformat(), "decision_cutoff_utc": decision.isoformat(), "rows": json.loads(rows.to_json(orient="records", date_format="iso")) if not rows.empty else []}
    except Exception as exc:
        raise HTTPException(502, f"Elexon API retrieval failed: {exc}") from exc

