"""Prepare real village units and a reproducible UTM 250 m analysis grid."""

import json

import geopandas as gpd
import numpy as np
from shapely.geometry import box

from data_pipeline.coverage_audit import ALIASES, TARGETS
from data_pipeline.feasibility import CACHE, ROOT

OUT = ROOT / "data/interim"


def villages():
    features = []
    for path in sorted(CACHE.glob("mh*.geojson")):
        for feature in json.loads(path.read_text(encoding="utf-8"))["features"]:
            props = feature["properties"]
            if (
                props.get("DISTRICT") == "Kolhapur"
                and ALIASES.get(props.get("SUB_DIST"), props.get("SUB_DIST")) in TARGETS
            ):
                features.append(feature)
    frame = gpd.GeoDataFrame.from_features(features, crs=4326).to_crs(32643)
    frame["tehsil"] = frame.SUB_DIST.replace(ALIASES)
    frame["name"] = frame.NAME.str.strip()
    frame = frame.drop(columns="NAME")
    unnamed = frame[frame.name == ""]
    unnamed.to_file(OUT / "unnamed-source-polygons.gpkg", driver="GPKG")
    frame = frame[frame.name != ""].dissolve(
        by=["tehsil", "CEN_2001", "name"], as_index=False
    )
    frame["id"] = "v-" + frame.CEN_2001
    if not frame.id.is_unique:
        raise ValueError("Conflicting village IDs after name-aware dissolve")
    frame["source"] = "village_polygon"
    frame = frame[
        ["id", "name", "tehsil", "source", "CEN_2001", "geometry"]
    ].sort_values("id")
    frame.to_file(OUT / "villages.gpkg", driver="GPKG")
    return frame


def make_grid(frame, spacing=250):
    """Keep full regular cells; assign display owner by largest intersection.

    The exact cell-village intersections are saved separately for area weighting.
    This avoids pretending a whole boundary cell belongs entirely to one village.
    """
    if frame.crs.to_epsg() != 32643:
        raise ValueError("Grid inputs must use EPSG:32643")
    xmin, ymin, xmax, ymax = frame.total_bounds
    cells = []
    union = frame.geometry.union_all()
    for x in np.arange(np.floor(xmin / spacing) * spacing, xmax, spacing):
        for y in np.arange(np.floor(ymin / spacing) * spacing, ymax, spacing):
            geom = box(x, y, x + spacing, y + spacing)
            if union.intersects(geom):
                cells.append({"id": f"g-{int(x)}-{int(y)}", "geometry": geom})
    grid = gpd.GeoDataFrame(cells, crs=32643)
    parts = gpd.overlay(
        grid.rename(columns={"id": "grid_cell_id"}),
        frame[["id", "geometry"]].rename(columns={"id": "village_id"}),
        how="intersection",
        keep_geom_type=False,
    )
    parts["area_m2"] = parts.area
    parts = parts[parts.area_m2 > 0].copy()
    owners = parts.sort_values(
        ["area_m2", "village_id"], ascending=[False, True]
    ).drop_duplicates("grid_cell_id")
    grid["village_id"] = grid.id.map(owners.set_index("grid_cell_id").village_id)
    grid = grid[grid.village_id.notna()].copy()
    return grid, parts


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    frame = villages()
    grid, parts = make_grid(frame)
    grid.to_file(OUT / "grid.gpkg", driver="GPKG")
    parts.to_file(OUT / "grid-village-parts.gpkg", driver="GPKG")
    report = {
        "villages": len(frame),
        "grid_cells": len(grid),
        "intersection_parts": len(parts),
        "crs": "EPSG:32643",
        "spacing_m": 250,
        "bounds_utm": frame.total_bounds.tolist(),
        "unnamed_policy": "Nine unnamed source polygons are quarantined, not silently labeled or included in village population. Their area and coverage are reported as a limitation.",
    }
    (ROOT / "docs/evidence/m1-grid.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
