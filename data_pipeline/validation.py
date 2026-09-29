"""Fail-loud data validation; documented SAR/population nodata exceptions."""

import argparse
import json
import sys
from pathlib import Path

# Support the PRD's direct invocation as well as python -m.
if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import geopandas as gpd
import numpy as np

from data_pipeline.feasibility import ROOT


def validate_geometry(frame):
    if frame.crs is None or frame.crs.to_epsg() != 32643:
        raise ValueError("Unexpected CRS; require EPSG:32643")
    if (
        frame.empty
        or not frame.geometry.is_valid.all()
        or frame.geometry.is_empty.any()
    ):
        raise ValueError("Invalid or empty geometry")
    if not frame.id.is_unique or frame.geometry.to_wkb().duplicated().any():
        raise ValueError("Duplicate ID or geometry")
    west, south, east, north = frame.to_crs(4326).total_bounds
    if not (73.7 <= west <= east <= 74.85 and 16.3 <= south <= north <= 17.1):
        raise ValueError("Coordinates outside Kolhapur study bounds")


def validate_numeric(frame):
    for name, low, high in [
        ("elevation", -100, 2000),
        ("slope", 0, 90),
        ("dist_to_river", 0, 150000),
        ("dist_to_road", 0, 150000),
    ]:
        values = frame[name]
        if (
            values.isna().any()
            or not np.isfinite(values).all()
            or not values.between(low, high).all()
        ):
            raise ValueError(f"Invalid or missing {name}")
    values = frame.population.dropna()
    if not np.isfinite(values).all() or (values < 0).any():
        raise ValueError("Invalid population")
    for year in [2019, 2021]:
        observed = frame[f"flood_fraction_{year}"]
        coverage = frame[f"evidence_coverage_{year}"]
        if (
            not observed.dropna().between(0, 1).all()
            or not coverage.between(0, 1).all()
        ):
            raise ValueError("Invalid SAR evidence range")
        if (observed.notna() & (coverage == 0)).any():
            raise ValueError("Unobserved SAR was labeled")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", choices=["all"], default="all")
    parser.parse_args()
    grid = gpd.read_file(ROOT / "data/interim/grid-features.gpkg")
    villages = gpd.read_file(ROOT / "data/interim/villages-features.gpkg")
    validate_geometry(grid)
    validate_geometry(villages)
    validate_numeric(grid)
    if (
        villages.population_estimate.isna().mean() > 0.05
        or (villages.population_estimate < 0).any()
    ):
        raise ValueError(
            "Negative village population or missingness above documented 5% ceiling"
        )
    difference = abs(villages.population_estimate.sum() - grid.population.sum())
    if difference > 0.01:
        raise ValueError(f"Population is not conserved: {difference}")
    scenarios = json.loads((ROOT / "data/interim/rainfall-scenarios.json").read_text())[
        "scenarios"
    ]
    for row in scenarios:
        if not (0 <= row["rainfall_24h_mm"] <= row["rainfall_72h_mm"] <= 2000):
            raise ValueError("Implausible rainfall scenario")
    report = {
        "status": "passed",
        "grid_cells": len(grid),
        "villages": len(villages),
        "population_conservation_error": difference,
        "documented_exceptions": {
            "village_population_nulls": villages.loc[
                villages.population_estimate.isna(), ["id", "name", "tehsil"]
            ].to_dict("records"),
            "grid_population_nulls": int(grid.population.isna().sum()),
            "reason": "Constrained raster has no valid population pixel in these cells; unknown remains null, village sums use observed population pixels",
            "unobserved_2019_cells": int(grid.flood_fraction_2019.isna().sum()),
            "unobserved_2021_cells": int(grid.flood_fraction_2021.isna().sum()),
        },
    }
    (ROOT / "docs/evidence/m1-validation.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
