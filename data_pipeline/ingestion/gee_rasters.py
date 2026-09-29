"""Offline, cached Earth Engine GeoTIFF downloads at explicitly aligned grids."""

import concurrent.futures
import hashlib
import json
import math
import time

import ee
import geopandas as gpd
import httpx
import rasterio

from data_pipeline.feasibility import ROOT
from data_pipeline.verify_m0_runtime import PROJECT

OUT = ROOT / "data/raw/rasters"
NODATA = -99999


def products(bounds):
    region = ee.Geometry.Rectangle(bounds, proj="EPSG:32643", geodesic=False)
    dem = ee.Image("USGS/SRTMGL1_003").select("elevation")
    population = (
        ee.ImageCollection("WorldPop/GP/100m/pop_age_sex_cons_unadj")
        .filter(ee.Filter.eq("country", "IND"))
        .filter(ee.Filter.eq("year", 2020))
        .first()
        .select("population")
    )
    result = {"terrain": dem.addBands(ee.Terrain.slope(dem)), "population": population}
    for year, pre_start, pre_end, during_start, during_end in [
        (2019, "2019-06-01", "2019-08-01", "2019-08-01", "2019-08-15"),
        (2021, "2021-06-01", "2021-07-15", "2021-07-15", "2021-08-01"),
    ]:
        scenes = (
            ee.ImageCollection("COPERNICUS/S1_GRD")
            .filterBounds(region)
            .filter(ee.Filter.eq("instrumentMode", "IW"))
            .filter(ee.Filter.listContains("transmitterReceiverPolarisation", "VV"))
            .filter(ee.Filter.eq("orbitProperties_pass", "DESCENDING"))
        )
        # Only a relative orbit present in both windows may enter change detection.
        pre = scenes.filterDate(pre_start, pre_end)
        during = scenes.filterDate(during_start, during_end)
        manifest = {
            "pre": pre.aggregate_array("system:index").getInfo(),
            "during": during.aggregate_array("system:index").getInfo(),
            "orbits_pre": pre.aggregate_array("relativeOrbitNumber_start").getInfo(),
            "orbits_during": during.aggregate_array(
                "relativeOrbitNumber_start"
            ).getInfo(),
        }
        (ROOT / f"docs/evidence/m1-sentinel-{year}-sources.json").write_text(
            json.dumps(manifest, indent=2), encoding="utf-8"
        )
        if manifest["pre"] and manifest["during"]:
            common = set(manifest["orbits_pre"]) & set(manifest["orbits_during"])
            if not common:
                raise ValueError(f"No matched orbit for {year}")
            orbit = min(common)

            def composite(collection):
                # Average speckle in linear power, not decibels. Preserve masks.
                db = (
                    collection.filter(ee.Filter.eq("relativeOrbitNumber_start", orbit))
                    .select("VV")
                    .median()
                )
                return (
                    ee.Image(10)
                    .pow(db.divide(10))
                    .focalMean(radius=30, units="meters")
                    .log10()
                    .multiply(10)
                )

            result[f"sar{year}"] = (
                composite(pre)
                .rename("pre_vv_db")
                .addBands(composite(during).rename("during_vv_db"))
            )
    return result


def download_tile(job):
    name, image, bounds, index, scale = job
    path = OUT / f"{name}-{index:03d}.tif"
    if path.exists():
        with rasterio.open(path) as src:
            if src.count:
                return {"file": path.name, "bytes": path.stat().st_size, "cached": True}
    for attempt in range(3):
        try:
            region = ee.Geometry.Rectangle(bounds, proj="EPSG:32643", geodesic=False)
            if name == "population":
                projection = image.projection().getInfo()
                crs, transform = projection["crs"], projection["transform"]
            else:
                crs, transform = "EPSG:32643", [scale, 0, 0, 0, -scale, 0]
            url = (
                image.toFloat()
                .unmask(NODATA)
                .getDownloadURL(
                    {
                        "region": region,
                        "crs": crs,
                        "crs_transform": transform,
                        "format": "GEO_TIFF",
                    }
                )
            )
            response = httpx.get(url, timeout=180, follow_redirects=True)
            response.raise_for_status()
            partial = path.with_suffix(".partial")
            partial.write_bytes(response.content)
            with rasterio.open(partial) as src:
                if not src.width or not src.height:
                    raise ValueError("Empty raster")
            partial.replace(path)
            print(f"Downloaded {path.name}: {len(response.content)} bytes", flush=True)
            return {
                "file": path.name,
                "bytes": len(response.content),
                "sha256": hashlib.sha256(response.content).hexdigest(),
            }
        except (httpx.HTTPError, ee.EEException, rasterio.errors.RasterioError):
            if attempt == 2:
                raise
            time.sleep(2 * (attempt + 1))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    ee.Initialize(project=PROJECT)
    ee.data.setDeadline(180000)
    villages = gpd.read_file(ROOT / "data/interim/villages.gpkg")
    bounds = villages.total_bounds.tolist()
    images = products(bounds)
    jobs = []
    for name, image in images.items():
        scale = 100 if name == "population" else 30
        # Size here controls download extents only. Population preserves its
        # native angular pixel grid so resampling never changes people/pixel.
        size = scale * 768
        index = 0
        for x in range(
            math.floor(bounds[0] / size) * size,
            math.ceil(bounds[2] / size) * size,
            size,
        ):
            for y in range(
                math.floor(bounds[1] / size) * size,
                math.ceil(bounds[3] / size) * size,
                size,
            ):
                jobs.append((name, image, [x, y, x + size, y + size], index, scale))
                index += 1
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        results = list(pool.map(download_tile, jobs))
    (ROOT / "docs/evidence/m1-raster-downloads.json").write_text(
        json.dumps(results, indent=2), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
