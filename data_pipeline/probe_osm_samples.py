"""Small OSM map API feasibility samples when Overpass is unavailable."""

import concurrent.futures
import json
from xml.etree import ElementTree

import httpx

from data_pipeline.feasibility import CACHE, ROOT

SAMPLES = {
    "Karvir": [74.20, 16.70, 74.24, 16.74],
    "Panhala": [74.08, 16.81, 74.12, 16.85],
    "Hatkanangale": [74.41, 16.73, 74.45, 16.77],
    "Shirol": [74.58, 16.71, 74.62, 16.75],
}


def probe(item):
    name, bbox = item
    url = "https://api.openstreetmap.org/api/0.6/map"
    try:
        response = httpx.get(
            url,
            params={"bbox": ",".join(map(str, bbox))},
            timeout=45,
            follow_redirects=True,
        )
        response.raise_for_status()
        root = ElementTree.fromstring(response.content)
        ways = [
            {tag.attrib["k"]: tag.attrib["v"] for tag in way.findall("tag")}
            for way in root.findall("way")
        ]
        (CACHE / f"osm-{name}.osm").write_bytes(response.content)
        return {
            "tehsil_sample": name,
            "bbox": bbox,
            "url": str(response.url),
            "ways": len(ways),
            "rivers_streams": sum(
                w.get("waterway") in {"river", "stream"} for w in ways
            ),
            "major_roads": sum(
                w.get("highway") in {"primary", "secondary", "tertiary"} for w in ways
            ),
            "status": "sample_only_not_full_tehsil",
        }
    except (httpx.HTTPError, ElementTree.ParseError) as exc:
        return {"tehsil_sample": name, "error": str(exc)}


def main():
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        report = list(pool.map(probe, SAMPLES.items()))
    path = ROOT / "docs/evidence/osm-samples.json"
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
