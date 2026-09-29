"""Calibrate rainfall presets from ten monsoons of actual reanalysis values."""

import concurrent.futures
import json

import httpx
import numpy as np
import pandas as pd

from data_pipeline.feasibility import ROOT
from data_pipeline.verify_m0_runtime import POINTS


def fetch(name):
    path = ROOT / f"data/raw/feasibility/rainfall-climatology-{name}.json"
    if not path.exists():
        lon, lat = POINTS[name]
        response = httpx.get(
            "https://archive-api.open-meteo.com/v1/archive",
            params={
                "latitude": lat,
                "longitude": lon,
                "start_date": "2015-01-01",
                "end_date": "2024-12-31",
                "daily": "precipitation_sum",
                "timezone": "Asia/Kolkata",
            },
            timeout=120,
        )
        response.raise_for_status()
        path.write_text(response.text, encoding="utf-8")
    daily = json.loads(path.read_text())["daily"]
    series = pd.Series(daily["precipitation_sum"], index=pd.to_datetime(daily["time"]))
    if series.isna().any() or (series < 0).any():
        raise ValueError(f"Invalid rainfall data for {name}")
    season = series.index.month.isin([6, 7, 8, 9])
    return (
        series[season].to_numpy(),
        series.rolling(3).sum()[season].dropna().to_numpy(),
    )


def main():
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        values = list(pool.map(fetch, POINTS))
    daily, rolling = np.concatenate([v[0] for v in values]), np.concatenate(
        [v[1] for v in values]
    )
    scenarios = []
    for name, quantile in [("normal", 0.50), ("heavy", 0.95), ("extreme", 0.99)]:
        day = round(float(np.quantile(daily, quantile)), 2)
        three = round(float(np.quantile(rolling, quantile)), 2)
        scenarios.append(
            {
                "id": name,
                "name": name.title(),
                "rainfall_24h_mm": day,
                "rainfall_72h_mm": max(day, three),
            }
        )
    report = {
        "method": "Pooled four-tehsil sample points; June–September 2015–2024 daily and rolling 3-day precipitation; separate 50th/95th/99th percentiles. Modeled reanalysis scenarios, not forecasts or independent station measurements.",
        "daily_sample_count": len(daily),
        "scenarios": scenarios,
    }
    (ROOT / "data/interim/rainfall-scenarios.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )
    (ROOT / "docs/evidence/m1-rainfall.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
