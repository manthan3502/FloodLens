"""Distinguish multipart settlements from unnamed shapes before M1 ingestion."""

import json
from collections import defaultdict

import geopandas as gpd

from data_pipeline.coverage_audit import ALIASES, TARGETS
from data_pipeline.feasibility import CACHE, ROOT


def main():
    features = []
    for path in CACHE.glob("mh*.geojson"):
        for feature in json.loads(path.read_text(encoding="utf-8"))["features"]:
            props = feature["properties"]
            if (
                props.get("DISTRICT") == "Kolhapur"
                and ALIASES.get(props.get("SUB_DIST"), props.get("SUB_DIST")) in TARGETS
            ):
                features.append(feature)
    frame = gpd.GeoDataFrame.from_features(features, crs=4326).to_crs(32643)
    frame["tehsil"] = frame.SUB_DIST.replace(ALIASES)
    results = {}
    for tehsil, rows in frame.groupby("tehsil"):
        codes = defaultdict(list)
        for _, row in rows.iterrows():
            codes[row.CEN_2001].append(row.NAME.strip())
        unnamed = rows[rows.NAME.str.strip() == ""]
        named = rows[rows.NAME.str.strip() != ""]
        repeats = {code: names for code, names in codes.items() if len(names) > 1}
        results[tehsil] = {
            "raw_polygons": len(rows),
            "unnamed_polygons": len(unnamed),
            "unnamed_area_km2": float(unnamed.area.sum() / 1e6),
            "named_unique_settlements": len(named.groupby(["CEN_2001", "NAME"])),
            "repeated_codes": repeats,
            "name_conflicts": [
                code for code, names in repeats.items() if len(set(names)) > 1
            ],
            "decision": "Same code and same name may be dissolved into multipart settlements in M1. Blank names with truncated tehsil codes are not village identifiers; keep an explicit exclusion/coverage record.",
        }
    path = ROOT / "docs/evidence/boundary-identifiers.json"
    path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
