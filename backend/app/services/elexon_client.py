from __future__ import annotations

import asyncio
from datetime import datetime
import httpx
import pandas as pd


class ElexonClient:
    base_url = "https://data.elexon.co.uk/bmrs/api/v1"

    def __init__(self, timeout: float = 60.0):
        self.timeout = timeout
        self._cache: dict[tuple[str, str, str], list[dict]] = {}

    async def _get_stream(self, dataset: str, start: datetime, end: datetime) -> list[dict]:
        key = (dataset, start.isoformat(), end.isoformat())
        if key in self._cache:
            return self._cache[key]
        params = {"publishDateTimeFrom": start.isoformat(), "publishDateTimeTo": end.isoformat()}
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(f"{self.base_url}/datasets/{dataset}/stream", params=params)
            response.raise_for_status()
            payload = response.json()
        if not isinstance(payload, list):
            raise ValueError(f"Unexpected {dataset} response shape")
        self._cache[key] = payload
        return payload

    async def fetch_actuals(self, start: datetime, end: datetime) -> pd.DataFrame:
        records = await self._get_stream("FUELHH", start, end)
        frame = pd.DataFrame(records)
        if frame.empty:
            return pd.DataFrame(columns=["start_time", "publish_time", "actual"])
        frame = frame[frame["fuelType"].eq("WIND")].copy()
        frame.rename(columns={"startTime": "start_time", "publishTime": "publish_time", "generation": "actual"}, inplace=True)
        return frame[["start_time", "publish_time", "actual"]]

    async def fetch_forecasts(self, start: datetime, end: datetime) -> pd.DataFrame:
        records = await self._get_stream("WINDFOR", start, end)
        frame = pd.DataFrame(records)
        if frame.empty:
            return pd.DataFrame(columns=["start_time", "publish_time", "forecast"])
        frame.rename(columns={"startTime": "start_time", "publishTime": "publish_time", "generation": "forecast"}, inplace=True)
        return frame[["start_time", "publish_time", "forecast"]]

    async def fetch_forecast_history(self, start_time: datetime) -> pd.DataFrame:
        # WINDFOR stream is publication-time filtered. Query a bounded historical
        # window around the delivery date so all versions can be selected locally.
        start = start_time.replace(hour=0, minute=0, second=0, microsecond=0) - pd.Timedelta(days=8).to_pytimedelta()
        end = start_time.replace(hour=0, minute=0, second=0, microsecond=0) + pd.Timedelta(days=1).to_pytimedelta()
        return await self.fetch_forecasts(start, end)

