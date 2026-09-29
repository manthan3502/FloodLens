"""Score the immutable offline snapshot and aggregate exact intersection areas."""

import json
from functools import lru_cache

from app.core.db import query
from app.ml.susceptibility import category, score_cell


@lru_cache(maxsize=1)
def snapshot():
    villages = query(
        "SELECT id,name,tehsil,source,population_estimate,ST_AsGeoJSON(ST_Transform(ST_Multi(ST_SimplifyPreserveTopology(geom,15)),4326)) AS geometry FROM villages ORDER BY id"
    )
    cells = query(
        "SELECT g.id,g.elevation,g.slope,g.dist_to_river,g.dist_to_road,avg(e.flood_fraction) FILTER(WHERE e.coverage_fraction>=0.8) AS historical_evidence,avg(e.coverage_fraction) AS history_coverage FROM grid_cells g LEFT JOIN grid_flood_evidence e ON e.grid_cell_id=g.id GROUP BY g.id ORDER BY g.id"
    )
    parts = query(
        "SELECT grid_cell_id,village_id,area_m2 FROM grid_village_parts ORDER BY village_id,grid_cell_id"
    )
    metadata = query("SELECT notes FROM model_metadata WHERE id='index-v1'")[0]["notes"]
    scenarios = {row["id"]: row for row in query("SELECT * FROM rainfall_scenarios")}
    return villages, cells, parts, metadata, scenarios


def evaluate(scenario_id):
    villages, cells, parts, metadata, scenarios = snapshot()
    scenario = scenarios[scenario_id]
    bounds = metadata["elevation_bounds"]
    scored = {cell["id"]: (cell, score_cell(cell, scenario, bounds)) for cell in cells}
    totals = {
        v["id"]: {
            "area": 0.0,
            "score": 0.0,
            "coverage": 0.0,
            "unknown_area": 0.0,
            "raw": dict.fromkeys(
                ["elevation", "slope", "dist_to_river", "dist_to_road"], 0.0
            ),
            "contributions": dict.fromkeys(metadata["config"]["weights"], 0.0),
            "history": 0.0,
            "history_area": 0.0,
        }
        for v in villages
    }
    for part in parts:
        area = part["area_m2"]
        cell, result = scored[part["grid_cell_id"]]
        total = totals[part["village_id"]]
        total["area"] += area
        total["score"] += result["risk_score"] * area
        total["coverage"] += cell["history_coverage"] * area
        total["unknown_area"] += int(result["history_missing"]) * area
        if cell["historical_evidence"] is not None:
            total["history"] += cell["historical_evidence"] * area
            total["history_area"] += area
        for name in total["raw"]:
            total["raw"][name] += cell[name] * area
        for name, value in result["contributions"].items():
            total["contributions"][name] += value * area
    features = []
    for village in villages:
        total = totals[village["id"]]
        area = total["area"]
        score = total["score"] / area
        raw = {k: v / area for k, v in total["raw"].items()}
        contributions = {k: v / area for k, v in total["contributions"].items()}
        top = sorted(contributions, key=lambda k: (-contributions[k], k))[:3]
        road = raw["dist_to_road"]
        properties = {k: v for k, v in village.items() if k != "geometry"}
        properties.update(
            {
                "scenario_id": scenario_id,
                "risk_score": score,
                "risk_category": category(score),
                "raw_factors": raw,
                "factor_contributions": contributions,
                "top_factors": top,
                "historical_evidence": {
                    "mean_detected_fraction": (
                        total["history"] / total["history_area"]
                        if total["history_area"]
                        else None
                    ),
                    "mean_event_coverage": total["coverage"] / area,
                    "unknown_area_fraction": total["unknown_area"] / area,
                    "label": "SAR change proxy, incomplete event coverage",
                },
                "accessibility": {
                    "category": (
                        "Easy"
                        if road < 500
                        else "Moderate" if road < 2000 else "Difficult"
                    ),
                    "distance_to_major_road_m": road,
                },
                "population_status": (
                    "unknown"
                    if village["population_estimate"] is None
                    else "modeled_2020_observed_pixels"
                ),
                "explanation": f"{category(score)} relative susceptibility under {scenario['name'].lower()} rainfall. Largest index contributions: {', '.join(top).replace('_', ' ')}. Population is modeled exposure context; SAR evidence is incomplete. This is not a flood probability.",
            }
        )
        features.append(
            {
                "type": "Feature",
                "id": village["id"],
                "geometry": json.loads(village["geometry"]),
                "properties": properties,
            }
        )
    return {
        "type": "FeatureCollection",
        "features": features,
        "scenario": scenario,
        "methodology": "susceptibility_index",
        "last_processed": metadata["data_processed"],
    }


def rivers():
    rows = query(
        "SELECT id,name,ST_AsGeoJSON(ST_Transform(geom,4326)) AS geometry FROM waterways ORDER BY id"
    )
    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "id": row["id"],
                "properties": {"name": row["name"]},
                "geometry": json.loads(row["geometry"]),
            }
            for row in rows
        ],
    }
