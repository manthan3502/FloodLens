"""Fetch real waterways/major roads and preserve raw source records."""

import concurrent.futures
import json
import math
from xml.etree import ElementTree

import geopandas as gpd
import httpx
from shapely.geometry import LineString, box

from data_pipeline.feasibility import ROOT

RAW = ROOT / "data/raw/osm"


def read_osm_xml(content):
    root = ElementTree.fromstring(content)
    nodes = {
        node.attrib["id"]: (float(node.attrib["lon"]), float(node.attrib["lat"]))
        for node in root.findall("node")
    }
    features = []
    for way in root.findall("way"):
        tags = {tag.attrib["k"]: tag.attrib["v"] for tag in way.findall("tag")}
        kind = (
            "river"
            if tags.get("waterway") in {"river", "stream"}
            else (
                "road"
                if tags.get("highway") in {"primary", "secondary", "tertiary"}
                else None
            )
        )
        if kind is None:
            continue
        refs = [nd.attrib["ref"] for nd in way.findall("nd")]
        if len(refs) < 2 or any(ref not in nodes for ref in refs):
            continue
        features.append(
            {
                "osm_id": way.attrib["id"],
                "kind": kind,
                "name": tags.get("name", ""),
                "geometry": LineString([nodes[ref] for ref in refs]),
            }
        )
    return features


def fetch_tile(job):
    index, bounds = job
    label = f"{index:03d}" if isinstance(index, int) else index
    path = RAW / f"tile-{label}.osm"
    if not path.exists():
        with httpx.Client(timeout=120, follow_redirects=True) as client:
            response = client.get(
                "https://api.openstreetmap.org/api/0.6/map",
                params={"bbox": ",".join(map(str, bounds))},
            )
            if (
                response.status_code == 400
                and "too many nodes" in response.text.lower()
            ):
                if label.count("-") >= 4:
                    raise ValueError("OSM extract still too dense after subdivision")
                west, south, east, north = bounds
                midx, midy = (west + east) / 2, (south + north) / 2
                children = [
                    [west, south, midx, midy],
                    [midx, south, east, midy],
                    [west, midy, midx, north],
                    [midx, midy, east, north],
                ]
                return [
                    feature
                    for child, bbox in enumerate(children)
                    for feature in fetch_tile((f"{label}-{child}", bbox))
                ]
            response.raise_for_status()
            ElementTree.fromstring(response.content)
            path.write_bytes(response.content)
    return read_osm_xml(path.read_bytes())


def main():
    RAW.mkdir(parents=True, exist_ok=True)
    villages = gpd.read_file(ROOT / "data/interim/villages.gpkg").to_crs(4326)
    bounds = villages.total_bounds
    boundary = villages.geometry.union_all().buffer(0.015)
    # Bounded map requests are a same-source transport fallback after recorded
    # Overpass failures; two workers and cached responses limit provider load.
    jobs = []
    step = 0.08
    for xi in range(
        math.floor((bounds[0] - 0.015) / step), math.ceil((bounds[2] + 0.015) / step)
    ):
        for yi in range(
            math.floor((bounds[1] - 0.015) / step),
            math.ceil((bounds[3] + 0.015) / step),
        ):
            tile = [
                round(xi * step, 6),
                round(yi * step, 6),
                round((xi + 1) * step, 6),
                round((yi + 1) * step, 6),
            ]
            if boundary.intersects(box(*tile)):
                jobs.append((len(jobs), tile))
    features = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        for batch in pool.map(fetch_tile, jobs):
            features.extend(batch)
    frame = (
        gpd.GeoDataFrame(features, crs=4326)
        .drop_duplicates(["osm_id", "kind"])
        .to_crs(32643)
    )
    if frame[frame.kind == "river"].empty or frame[frame.kind == "road"].empty:
        raise ValueError("Missing required OSM geometry")
    frame.to_file(ROOT / "data/interim/osm.gpkg", driver="GPKG")
    report = {
        "tiles": len(jobs),
        "way_counts": frame.groupby("kind").size().to_dict(),
        "source": "OpenStreetMap map API",
        "license": "ODbL",
        "transport_fallback": "Overpass requests failed during M0; same OSM source fetched in bounded cached map extracts.",
    }
    (ROOT / "docs/evidence/m1-osm.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )
    print(report)


if __name__ == "__main__":
    main()
