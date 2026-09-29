"""Offline feature extraction; missing SAR observations are never dry labels."""

import json
from contextlib import ExitStack

import geopandas as gpd
import numpy as np
import rasterio
from pyproj import Transformer
from rasterio.features import rasterize
from rasterio.merge import merge
from rasterio.windows import from_bounds
from shapely import distance
from shapely.strtree import STRtree

from data_pipeline.feasibility import ROOT

RAW = ROOT / "data/raw/rasters"
OUT = ROOT / "data/interim"
NODATA = -99999


def mosaic(name):
    with ExitStack() as stack:
        sources = [
            stack.enter_context(rasterio.open(p))
            for p in sorted(RAW.glob(f"{name}-*.tif"))
        ]
        if not sources:
            raise ValueError(f"Missing raster product {name}")
        array, transform = merge(sources, nodata=np.float32(NODATA))
        return array, transform, sources[0].crs


def otsu(values):
    values = np.asarray(values, dtype=float)
    values = values[np.isfinite(values)]
    if values.size < 2 or np.ptp(values) == 0:
        raise ValueError("Otsu needs varied finite observations")
    hist, edges = np.histogram(values, bins=256)
    centers = (edges[:-1] + edges[1:]) / 2
    weight = np.cumsum(hist)
    mean = np.cumsum(hist * centers)
    denom = weight * (weight[-1] - weight)
    variance = np.divide(
        (mean[-1] * weight - mean * weight[-1]) ** 2,
        denom,
        out=np.zeros_like(mean),
        where=denom > 0,
    )
    return float(centers[np.argmax(variance)])


def window_values(array, transform, bounds):
    window = from_bounds(*bounds, transform)
    r0, c0 = max(0, int(np.ceil(window.row_off - 0.5))), max(
        0, int(np.ceil(window.col_off - 0.5))
    )
    r1 = min(array.shape[-2], int(np.ceil(window.row_off + window.height - 0.5)))
    c1 = min(array.shape[-1], int(np.ceil(window.col_off + window.width - 0.5)))
    return array[..., r0:r1, c0:c1]


def main():
    villages = (
        gpd.read_file(OUT / "villages.gpkg").sort_values("id").reset_index(drop=True)
    )
    grid = gpd.read_file(OUT / "grid.gpkg")
    osm = gpd.read_file(OUT / "osm.gpkg")
    terrain, transform, crs = mosaic("terrain")
    for band, name in enumerate(["elevation", "slope"]):
        result = []
        for geom in grid.geometry:
            data = window_values(terrain[band], transform, geom.bounds)
            valid = data[(data != NODATA) & np.isfinite(data)]
            result.append(float(valid.mean()) if len(valid) else None)
        grid[name] = result
    centers = grid.geometry.centroid.values
    for kind, name in [("river", "dist_to_river"), ("road", "dist_to_road")]:
        lines = osm[osm.kind == kind].geometry.values
        if len(lines) == 0:
            raise ValueError(f"No {kind} data")
        tree = STRtree(lines)
        grid[name] = distance(centers, lines[tree.nearest(centers)])
    print("Terrain and distance features extracted", flush=True)
    pop, pop_transform, pop_crs = mosaic("population")
    pop = pop[0]
    if np.any((pop != NODATA) & (pop < 0)):
        raise ValueError("Negative population other than nodata")
    village_raster = rasterize(
        ((geom, i + 1) for i, geom in enumerate(villages.to_crs(pop_crs).geometry)),
        out_shape=pop.shape,
        transform=pop_transform,
        fill=0,
        dtype="int32",
    )
    valid = (village_raster > 0) & (pop != NODATA) & np.isfinite(pop)
    totals = np.bincount(
        village_raster[valid], weights=pop[valid], minlength=len(villages) + 1
    )
    valid_counts = np.bincount(village_raster[valid], minlength=len(villages) + 1)
    villages["population_estimate"] = [
        float(totals[i + 1]) if valid_counts[i + 1] else None
        for i in range(len(villages))
    ]
    rows, cols = np.where(valid)
    xs, ys = rasterio.transform.xy(pop_transform, rows, cols)
    px, py = Transformer.from_crs(pop_crs, 32643, always_xy=True).transform(xs, ys)
    keys = [
        f"g-{int(x // 250) * 250}-{int(y // 250) * 250}"
        for x, y in zip(px, py, strict=True)
    ]
    sums = {}
    for key, value in zip(keys, pop[valid], strict=True):
        sums[key] = sums.get(key, 0.0) + float(value)
    grid["population"] = grid.id.map(sums)
    grid["population_pixel_available"] = grid.population.notna()
    events = {}
    aoi = rasterize(
        ((geom, 1) for geom in villages.geometry),
        out_shape=terrain.shape[1:],
        transform=transform,
        fill=0,
        dtype="uint8",
    )
    for year in [2019, 2021]:
        sar, sar_transform, _ = mosaic(f"sar{year}")
        if sar.shape[1:] != terrain.shape[1:] or sar_transform != transform:
            raise ValueError("SAR and terrain pixel grids differ")
        coverage = (
            (sar[0] != NODATA)
            & (sar[1] != NODATA)
            & (aoi == 1)
            & (terrain[1] != NODATA)
        )
        change = sar[1] - sar[0]
        sample = change[coverage & (terrain[1] < 5)]
        threshold = (
            min(otsu(sample), -1.5) if len(sample) > 1 and np.ptp(sample) else -1.5
        )
        flood = (
            coverage
            & (change < threshold)
            & (terrain[1] < 5)
            & (sar[1] < -15)
            & (sar[0] >= -15)
        )
        profile = {
            "driver": "GTiff",
            "height": flood.shape[0],
            "width": flood.shape[1],
            "count": 1,
            "dtype": "uint8",
            "crs": crs,
            "transform": transform,
            "nodata": 255,
            "compress": "deflate",
        }
        mask = np.where(coverage, flood.astype("uint8"), 255).astype("uint8")
        with rasterio.open(OUT / f"flood-{year}.tif", "w", **profile) as dst:
            dst.write(mask, 1)
        fractions, coverages = [], []
        for geom in grid.geometry:
            pixels = window_values(mask, transform, geom.bounds)
            seen = pixels != 255
            fractions.append(float((pixels[seen] == 1).mean()) if seen.any() else None)
            coverages.append(float(seen.mean()) if seen.size else 0.0)
        grid[f"flood_fraction_{year}"] = fractions
        grid[f"evidence_coverage_{year}"] = coverages
        events[year] = {
            "change_threshold_db": threshold,
            "covered_pixels": int(coverage.sum()),
            "flood_pixels": int(flood.sum()),
            "coverage_fraction": float(coverage.sum() / np.count_nonzero(aoi)),
            "method": "Matched descending orbit, linear-power speckle mean, Otsu change threshold capped at -1.5 dB, during VV<-15 dB, slope<5 degrees, pre VV>=-15 dB water screen. Unvalidated proxy.",
        }
        print(f"SAR {year}: {events[year]}", flush=True)
    grid.to_file(OUT / "grid-features.gpkg", driver="GPKG")
    villages.to_file(OUT / "villages-features.gpkg", driver="GPKG")
    report = {
        "cells": len(grid),
        "villages": len(villages),
        "population_sum_villages": float(villages.population_estimate.sum()),
        "population_sum_grid": float(grid.population.sum()),
        "population_conservation_difference": float(
            villages.population_estimate.sum() - grid.population.sum()
        ),
        "population_grid_nulls": int(grid.population.isna().sum()),
        "population_method": "Native population pixels assigned once by center to stable-ID village raster and UTM grid. No valid source pixel remains null. Overlapping villages use stable last-ID wins to avoid double counting.",
        "events": events,
    }
    (ROOT / "docs/evidence/m1-feature-summary.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
