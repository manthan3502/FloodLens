"""Recheck only previously blocked runtime and Earth Engine acceptance evidence."""

import json
import os
import subprocess
from datetime import UTC, datetime

import ee

from data_pipeline.feasibility import ROOT

PROJECT = os.environ.get("GEE_PROJECT", "floodlens-510018")
POINTS = {
    "Karvir": [74.22, 16.70],
    "Panhala": [74.10, 16.83],
    "Hatkanangale": [74.43, 16.75],
    "Shirol": [74.60, 16.73],
}


def database_probe():
    sql = """SELECT json_build_object(
        'postgis_version', PostGIS_Version(),
        'spatial_roundtrip', ST_Distance(
          ST_Transform(ST_Transform(ST_SetSRID(ST_Point(74.22,16.70),4326),32643),4326),
          ST_SetSRID(ST_Point(74.22,16.70),4326)) < 1e-8,
        'geojson', ST_AsGeoJSON(ST_SetSRID(ST_Point(74.22,16.70),4326))::json
    );"""
    result = subprocess.run(
        [
            "docker",
            "compose",
            "exec",
            "-T",
            "db",
            "psql",
            "-U",
            "floodlens",
            "-d",
            "floodlens",
            "-At",
            "-v",
            "ON_ERROR_STOP=1",
            "-c",
            sql,
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=60,
        check=True,
    )
    return json.loads(result.stdout)


def satellite_probe():
    try:
        ee.Initialize(project=PROJECT)
        ee.data.setDeadline(60000)
        report = {}
        for tehsil, coordinates in POINTS.items():
            point = ee.Geometry.Point(coordinates)
            area = point.buffer(1000)
            counts = {}
            for year, start, end in [
                (2019, "2019-08-01", "2019-08-15"),
                (2021, "2021-07-15", "2021-08-01"),
            ]:
                scenes = (
                    ee.ImageCollection("COPERNICUS/S1_GRD")
                    .filterBounds(area)
                    .filterDate(start, end)
                    .filter(ee.Filter.eq("instrumentMode", "IW"))
                    .filter(
                        ee.Filter.listContains("transmitterReceiverPolarisation", "VV")
                    )
                )
                counts[str(year)] = scenes.size()
            report[tehsil] = ee.Dictionary(
                {
                    "scene_counts": ee.Dictionary(counts),
                    "srtm_sample_m": ee.Image("USGS/SRTMGL1_003").reduceRegion(
                        ee.Reducer.mean(), area, 30, maxPixels=100000
                    ),
                    "worldpop_2020_sample": ee.ImageCollection(
                        "WorldPop/GP/100m/pop_age_sex_cons_unadj"
                    )
                    .filter(ee.Filter.eq("country", "IND"))
                    .filter(ee.Filter.eq("year", 2020))
                    .mosaic()
                    .select("population")
                    .reduceRegion(ee.Reducer.sum(), area, 100, maxPixels=100000),
                }
            ).getInfo()
        return {
            "status": "access_verified",
            "project": PROJECT,
            "samples": report,
            "population_note": "Constrained 2020 WorldPop population band, UN-adjusted per the Earth Engine catalog. Exact collection: WorldPop/GP/100m/pop_age_sex_cons_unadj. Replaces the stalled unadjusted country download; not the unconstrained population probe.",
        }
    except (ee.EEException, ValueError, OSError) as exc:
        return {"status": "blocked", "project": PROJECT, "error": str(exc)}


def main():
    report = {
        "checked_at": datetime.now(UTC).isoformat(),
        "database": database_probe(),
        "earth_engine": satellite_probe(),
    }
    path = ROOT / "docs/evidence/m0-runtime-recheck.json"
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
