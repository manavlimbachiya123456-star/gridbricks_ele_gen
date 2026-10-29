from __future__ import annotations

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str
    service: str
    data_source: str


class AnalysisResponse(BaseModel):
    month: str
    decision_cutoff_utc: str
    source: str
    retrieval_status: str
    limitation: str | None = None
    metrics: dict
    rows: list[dict]


class HistoryResponse(BaseModel):
    start_time: str
    decision_cutoff_utc: str
    rows: list[dict]

