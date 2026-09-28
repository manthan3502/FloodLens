"""Download and inspect candidate boundaries and small raster windows for M0."""

import concurrent.futures
import json

import rasterio
from rasterio.windows import from_bounds

from data_pipeline.feasibility import ROOT, fetch


def raster_probe(name, url):
    try:
        with rasterio.Env(
            GDAL_HTTP_TIMEOUT="45", GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR"
        ):
            with rasterio.open(url) as src:
                window = from_bounds(74.22, 16.69, 74.23, 16.70, src.transform)
                values = src.read(1, window=window, masked=True)
                return {
                    "name": name,
                    "url": url,
                    "crs": str(src.crs),
                    "resolution": src.res,
                    "sample_bounds": [74.22, 16.69, 74.23, 16.70],
                    "valid_pixels": int(values.count()),
                    "min": float(values.min()),
                    "max": float(values.max()),
                    "sum": float(values.sum()),
                    "status": "sample_read_only",
                }
    except (rasterio.errors.RasterioError, ValueError) as exc:
        return {"name": name, "url": url, "status": "failed", "error": str(exc)}


def main():
    tasks = [
        (
            f"mh{i}.geojson",
            f"https://raw.githubusercontent.com/datameet/indian_village_boundaries/master/mh/mh{i}.geojson",
            None,
        )
        for i in [1, 2]
    ]
    tasks.extend(
        [
            (
                "iitb-villages.zip",
                "https://www.cse.iitb.ac.in/~pocra/MahaCensus_shapefile_data1.1/Shape_File_3July/kolhapur.zip",
                None,
            ),
            (
                "iitb-tehsils.zip",
                "https://www.cse.iitb.ac.in/~pocra/MahaCensus_shapefile_data1.2/Boundary_Shape_File_21July/kolhapur.zip",
                None,
            ),
        ]
    )
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(lambda args: fetch(*args), tasks))
    for endpoint in [
        "https://overpass.kumi.systems/api/interpreter",
        "https://overpass-api.de/api/interpreter",
    ]:
        query = "[out:json][timeout:50];(way[waterway=river](16.5,73.9,17.05,74.85);way[waterway=stream](16.5,73.9,17.05,74.85);way[highway=primary](16.5,73.9,17.05,74.85);way[highway=secondary](16.5,73.9,17.05,74.85);way[highway=tertiary](16.5,73.9,17.05,74.85););out geom;"
        result = fetch("osm-retry.json", endpoint, {"data": query})
        results.append(result)
        if result.get("elements", 0) > 0:
            break
    results.append(
        raster_probe(
            "worldpop-constrained",
            "https://data.worldpop.org/GIS/Population/Global_2000_2020_Constrained/2020/BSGM/IND/ind_ppp_2020_constrained.tif",
        )
    )
    output = ROOT / "docs/evidence/gate-a-spatial.json"
    output.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(output.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
