"""Reproducible M0 probes. Success here is evidence, not automatic Gate A approval."""

import concurrent.futures
import hashlib
import json
import os
from datetime import UTC, datetime
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "data/raw/feasibility"
REPORT = ROOT / "docs/evidence/gate-a-probes.json"


def fetch(name, url, params=None):
    try:
        with httpx.Client(timeout=90, follow_redirects=True) as client:
            response = client.get(url, params=params)
            response.raise_for_status()
        content = response.content
        CACHE.mkdir(parents=True, exist_ok=True)
        (CACHE / name).write_bytes(content)
        result = {
            "name": name,
            "url": str(response.url),
            "http_status": response.status_code,
            "bytes": len(content),
            "sha256": hashlib.sha256(content).hexdigest(),
            "status": "fetched_not_yet_validated",
        }
        if "rainfall" in name:
            daily = response.json()["daily"]
            values = daily["precipitation_sum"]
            result.update(
                days=len(values),
                nulls=values.count(None),
                total_mm=sum(v for v in values if v is not None),
            )
        elif name.startswith("osm"):
            elements = response.json()["elements"]
            result.update(
                elements=len(elements),
                rivers=sum("waterway" in e.get("tags", {}) for e in elements),
                roads=sum("highway" in e.get("tags", {}) for e in elements),
            )
        return result
    except (httpx.HTTPError, ValueError, KeyError, OSError) as exc:
        return {"name": name, "url": url, "status": "failed", "error": str(exc)}


def earth_engine():
    import ee

    try:
        ee.Initialize(project=os.environ.get("GEE_PROJECT"))
        area = ee.Geometry.Rectangle([73.9, 16.5, 74.85, 17.05])
        return {
            "name": "earth_engine",
            "status": "authenticated",
            "sentinel1_2019_count": ee.ImageCollection("COPERNICUS/S1_GRD")
            .filterBounds(area)
            .filterDate("2019-08-01", "2019-08-15")
            .size()
            .getInfo(),
        }
    except (ee.EEException, ValueError, OSError) as exc:
        return {"name": "earth_engine", "status": "blocked", "error": str(exc)}


def main():
    tasks = [
        (
            "datameet-list.json",
            "https://api.github.com/repos/datameet/indian_village_boundaries/contents/mh",
            None,
        ),
        (
            "iitb-boundaries.html",
            "https://www.cse.iitb.ac.in/~pocra/MahaCensus_shapefile_data1.2/Boundary.html",
            None,
        ),
        (
            "srtm-opentopography.json",
            "https://portal.opentopography.org/API/globaldem",
            {
                "demtype": "SRTMGL1",
                "south": 16.69,
                "north": 16.70,
                "west": 74.22,
                "east": 74.23,
                "outputFormat": "GTiff",
            },
        ),
        (
            "worldpop-catalog.json",
            "https://www.worldpop.org/rest/data/pop/wpgp?iso3=IND",
            None,
        ),
    ]
    for year, start, end in [(2019, "08-01", "08-15"), (2021, "07-15", "07-31")]:
        tasks.append(
            (
                f"rainfall-{year}.json",
                "https://archive-api.open-meteo.com/v1/archive",
                {
                    "latitude": 16.7,
                    "longitude": 74.25,
                    "start_date": f"{year}-{start}",
                    "end_date": f"{year}-{end}",
                    "daily": "precipitation_sum",
                    "timezone": "Asia/Kolkata",
                },
            )
        )
    query = '[out:json][timeout:60];(way["waterway"~"^(river|stream)$"](16.5,73.9,17.05,74.85);way["highway"~"^(primary|secondary|tertiary)$"](16.5,73.9,17.05,74.85););out geom;'
    tasks.append(
        ("osm.json", "https://overpass-api.de/api/interpreter", {"data": query})
    )
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
        results = list(pool.map(lambda args: fetch(*args), tasks))
    results.append(earth_engine())
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(
        json.dumps(
            {
                "checked_at": datetime.now(UTC).isoformat(),
                "gate": "OPEN: review evidence and geometry before deciding",
                "probes": results,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print(REPORT.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
