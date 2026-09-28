"""Compare actual village polygons to available academic tehsil boundaries."""

import json

import geopandas as gpd
from shapely import make_valid

from data_pipeline.feasibility import CACHE, ROOT

ALIASES = {
    "Hatkalangale": "Hatkanangale",
    "hatkanangle": "Hatkanangale",
    "karvir": "Karvir",
    "panhala": "Panhala",
    "shirol": "Shirol",
}
TARGETS = {"Karvir", "Panhala", "Hatkanangale", "Shirol"}


def main():
    frames = []
    for filename in ["mh1.geojson", "mh2.geojson"]:
        data = json.loads((CACHE / filename).read_text(encoding="utf-8"))
        features = [
            f
            for f in data["features"]
            if f["properties"].get("DISTRICT") == "Kolhapur"
            and ALIASES.get(
                f["properties"].get("SUB_DIST"), f["properties"].get("SUB_DIST")
            )
            in TARGETS
        ]
        if features:
            frame = gpd.GeoDataFrame.from_features(features, crs=4326).to_crs(32643)
            frame["tehsil"] = frame.SUB_DIST.replace(ALIASES)
            frames.append(frame)
    boundary = gpd.read_file(
        f"/vsizip/{(CACHE / 'iitb-tehsils.zip').as_posix()}"
    ).to_crs(32643)
    boundary["tehsil"] = boundary.taluka_nam.replace(ALIASES)
    report = []
    for frame in frames:
        for tehsil, villages in frame.groupby("tehsil"):
            available = boundary[boundary.tehsil == tehsil]
            village_union = villages.geometry.union_all()
            row = {
                "tehsil": tehsil,
                "datameet_polygons": len(villages),
                "valid_polygons": int(villages.is_valid.sum()),
                "village_union_km2": village_union.area / 1e6,
                "census_2001_codes_unique": bool(villages.CEN_2001.is_unique),
            }
            if len(available):
                tehsil_geom = make_valid(available.geometry.union_all())
                row.update(
                    reference_area_km2=tehsil_geom.area / 1e6,
                    covered_fraction=village_union.intersection(tehsil_geom).area
                    / tehsil_geom.area,
                    area_outside_reference_km2=village_union.difference(
                        tehsil_geom
                    ).area
                    / 1e6,
                )
            else:
                row["coverage_status"] = (
                    "Tehsil missing in downloaded IITB boundary archive; full coverage not established."
                )
            report.append(row)
    path = ROOT / "docs/evidence/tehsil-coverage.json"
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
