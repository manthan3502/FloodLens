"""Bounded feasibility probes for public mirrors; no scientific claims."""

import concurrent.futures
import json

import httpx
import rasterio
from rasterio.windows import Window

from data_pipeline.feasibility import CACHE, ROOT


def osm_probe():
    results = []
    for endpoint in [
        "https://overpass.private.coffee/api/interpreter",
        "https://overpass.kumi.systems/api/interpreter",
    ]:
        try:
            query = "[out:json][timeout:25];(way[waterway](16.65,74.15,16.80,74.35);way[highway=primary](16.65,74.15,16.80,74.35););out geom;"
            response = httpx.post(endpoint, data={"data": query}, timeout=40)
            response.raise_for_status()
            data = response.json()
            (CACHE / "osm-sample.json").write_text(json.dumps(data), encoding="utf-8")
            results.append(
                {
                    "source": endpoint,
                    "status": "sample_fetched",
                    "elements": len(data["elements"]),
                    "bbox": [74.15, 16.65, 74.35, 16.80],
                }
            )
            if data["elements"]:
                break
        except (httpx.HTTPError, ValueError) as exc:
            results.append({"source": endpoint, "error": str(exc)})
    return results


def dem_probe():
    url = "https://copernicus-dem-30m.s3.amazonaws.com/Copernicus_DSM_COG_10_N16_00_E074_00_DEM/Copernicus_DSM_COG_10_N16_00_E074_00_DEM.tif"
    try:
        with (
            rasterio.Env(
                GDAL_HTTP_TIMEOUT="30", GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR"
            ),
            rasterio.open(url) as src,
        ):
            row, col = src.index(74.22, 16.70)
            data = src.read(1, window=Window(col, row, 32, 32), masked=True)
            return {
                "source": url,
                "dataset": "Copernicus GLO-30 (approved DEM fallback)",
                "crs": str(src.crs),
                "valid_pixels": int(data.count()),
                "min_m": float(data.min()),
                "max_m": float(data.max()),
                "status": "sample_read",
            }
    except rasterio.errors.RasterioError as exc:
        return {"source": url, "error": str(exc)}


def main():
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        osm = pool.submit(osm_probe)
        dem = pool.submit(dem_probe)
        report = {"osm": osm.result(), "dem": dem.result()}
    path = ROOT / "docs/evidence/gate-a-alternatives.json"
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
