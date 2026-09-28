"""Download actual small raster clips to verify extraction, not only metadata."""

import hashlib
import json

import ee
import httpx
import numpy as np
import rasterio

from data_pipeline.feasibility import CACHE, ROOT
from data_pipeline.verify_m0_runtime import POINTS, PROJECT


def main():
    ee.Initialize(project=PROJECT)
    images = {
        "srtm": ee.Image("USGS/SRTMGL1_003").select("elevation"),
        "population_constrained": ee.ImageCollection(
            "WorldPop/GP/100m/pop_age_sex_cons_unadj"
        )
        .filter(ee.Filter.eq("country", "IND"))
        .filter(ee.Filter.eq("year", 2020))
        .first()
        .select("population"),
        "sentinel1_2021": ee.ImageCollection("COPERNICUS/S1_GRD")
        .filterBounds(ee.Geometry.Point(POINTS["Karvir"]))
        .filterDate("2021-07-15", "2021-08-01")
        .select("VV")
        .first(),
    }
    report = []
    for name, image in images.items():
        region = ee.Geometry.Point(POINTS["Karvir"]).buffer(500).bounds()
        url = image.getDownloadURL(
            {
                "region": region,
                "scale": 100 if name.startswith("population") else 30,
                "format": "GEO_TIFF",
            }
        )
        response = httpx.get(url, timeout=120, follow_redirects=True)
        response.raise_for_status()
        path = CACHE / f"gee-{name}-clip.tif"
        path.write_bytes(response.content)
        with rasterio.open(path) as src:
            values = src.read(1, masked=True).astype(float)
            nodata_pixels = int(np.count_nonzero(values.data == -99999))
            values = np.ma.masked_equal(values, -99999)
            if name == "population_constrained":
                assert values.min() >= 0, "Negative population outside nodata sentinel"
            assert values.count() > 0, f"Empty clip: {name}"
            report.append(
                {
                    "dataset": name,
                    "bytes": path.stat().st_size,
                    "sha256": hashlib.sha256(response.content).hexdigest(),
                    "crs": str(src.crs),
                    "valid_pixels": int(values.count()),
                    "nodata_sentinel_pixels": nodata_pixels,
                    "min": float(values.min()),
                    "max": float(values.max()),
                }
            )
    path = ROOT / "docs/evidence/gee-raster-clips.json"
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
