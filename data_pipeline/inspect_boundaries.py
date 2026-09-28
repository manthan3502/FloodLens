"""Record per-tehsil candidate geometry quality without choosing a fallback early."""

import json
from collections import defaultdict

import pyogrio
from shapely.geometry import shape

from data_pipeline.feasibility import CACHE, ROOT

TEHSILS = {"Karvir", "Panhala", "Hatkalangale", "Hatkanangle", "Hatkanangale", "Shirol"}


def main():
    counts = defaultdict(
        lambda: {"count": 0, "invalid": 0, "empty": 0, "duplicates": 0}
    )
    seen = set()
    for filename in ["mh1.geojson", "mh2.geojson"]:
        data = json.loads((CACHE / filename).read_text(encoding="utf-8"))
        for feature in data["features"]:
            props = feature["properties"]
            tehsil = props.get("SUB_DIST")
            if props.get("DISTRICT", "").lower() != "kolhapur" or tehsil not in TEHSILS:
                continue
            geometry = shape(feature["geometry"])
            row = counts[tehsil]
            row["count"] += 1
            row["invalid"] += int(not geometry.is_valid)
            row["empty"] += int(geometry.is_empty)
            row["duplicates"] += int(geometry.wkb in seen)
            seen.add(geometry.wkb)
    archives = {}
    for filename in ["iitb-villages.zip", "iitb-tehsils.zip"]:
        path = f"/vsizip/{(CACHE / filename).as_posix()}"
        layers = pyogrio.list_layers(path)
        archives[filename] = []
        for layer, _ in layers:
            info = pyogrio.read_info(path, layer=layer)
            archives[filename].append(
                {
                    "layer": layer,
                    "features": info["features"],
                    "crs": info["crs"],
                    "fields": info["fields"].tolist()[:20],
                    "bounds": info["total_bounds"],
                }
            )
    output = ROOT / "docs/evidence/boundary-quality.json"
    output.write_text(
        json.dumps(
            {
                "datameet": dict(counts),
                "iitb": archives,
                "decision": "Candidate inspection only; coverage against tehsil geometry and Census joins still required.",
            },
            indent=2,
            default=list,
        ),
        encoding="utf-8",
    )
    print(output.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
