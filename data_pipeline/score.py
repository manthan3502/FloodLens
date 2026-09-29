"""Materialize index outputs from real PostGIS features, with determinism evidence."""

import hashlib
import json
from collections import Counter
from contextlib import closing

from backend.app.ml.susceptibility import CONFIG, score_cell
from data_pipeline.feasibility import ROOT
from data_pipeline.load import bulk_execute, connect

DDL = """
CREATE TABLE IF NOT EXISTS model_metadata (id text PRIMARY KEY, model_type text NOT NULL, trained_at timestamptz, pr_auc_spatial_cv double precision, pr_auc_temporal_holdout double precision, feature_list jsonb NOT NULL, notes jsonb NOT NULL);
CREATE TABLE IF NOT EXISTS risk_results (grid_cell_id text REFERENCES grid_cells(id), scenario_id text REFERENCES rainfall_scenarios(id), risk_score double precision NOT NULL CHECK(risk_score BETWEEN 0 AND 1), risk_category text NOT NULL, computed_at timestamptz NOT NULL DEFAULT now(), PRIMARY KEY(grid_cell_id,scenario_id));
"""


def main():
    with closing(connect()) as conn, closing(conn.cursor()) as cursor:
        for statement in DDL.split(";"):
            if statement.strip():
                cursor.execute(statement)
        cursor.execute(
            "SELECT percentile_cont(0.05) WITHIN GROUP (ORDER BY elevation), percentile_cont(0.95) WITHIN GROUP (ORDER BY elevation) FROM grid_cells"
        )
        bounds = list(cursor.fetchone())
        cursor.execute(
            "SELECT g.id,g.elevation,g.slope,g.dist_to_river,avg(e.flood_fraction) FILTER(WHERE e.coverage_fraction>=0.8) FROM grid_cells g LEFT JOIN grid_flood_evidence e ON e.grid_cell_id=g.id GROUP BY g.id ORDER BY g.id"
        )
        cells = [
            dict(
                zip(
                    [
                        "id",
                        "elevation",
                        "slope",
                        "dist_to_river",
                        "historical_evidence",
                    ],
                    row,
                    strict=True,
                )
            )
            for row in cursor.fetchall()
        ]
        cursor.execute(
            "SELECT id,rainfall_24h_mm,rainfall_72h_mm FROM rainfall_scenarios ORDER BY id"
        )
        scenarios = [
            dict(zip(["id", "rainfall_24h_mm", "rainfall_72h_mm"], row, strict=True))
            for row in cursor.fetchall()
        ]
        evidence = {
            "gate_b": "GO WITH REDUCED SCOPE",
            "model_type": "susceptibility_index",
            "cells": len(cells),
            "elevation_bounds_5_95": bounds,
            "history_unknown_cells": sum(
                c["historical_evidence"] is None for c in cells
            ),
            "scenarios": {},
        }
        for scenario in scenarios:
            first = [score_cell(cell, scenario, bounds) for cell in cells]
            second = [score_cell(cell, scenario, bounds) for cell in cells]
            assert first == second
            rows = [
                (c["id"], scenario["id"], s["risk_score"], s["risk_category"])
                for c, s in zip(cells, first, strict=True)
            ]
            bulk_execute(
                cursor,
                "INSERT INTO risk_results(grid_cell_id,scenario_id,risk_score,risk_category) VALUES (%s,%s,%s,%s) ON CONFLICT(grid_cell_id,scenario_id) DO UPDATE SET risk_score=excluded.risk_score,risk_category=excluded.risk_category,computed_at=now()",
                rows,
            )
            evidence["scenarios"][scenario["id"]] = {
                "categories": dict(Counter(s["risk_category"] for s in first)),
                "min": min(s["risk_score"] for s in first),
                "max": max(s["risk_score"] for s in first),
                "deterministic_sha256": hashlib.sha256(
                    json.dumps(rows).encode()
                ).hexdigest(),
            }
        notes = {
            "gate_b": evidence["gate_b"],
            "config": CONFIG,
            "elevation_bounds": bounds,
            "limitations": "Uncalibrated index, not flood probability. SAR 2019 sparse; 2021 scene precedes peak response. No supervised model or accuracy metrics.",
            "data_processed": "2026-09-29",
            "history_missing_rule": "neutral 0.5 when no event has >=80% cell coverage",
        }
        cursor.execute(
            "INSERT INTO model_metadata VALUES (%s,%s,NULL,NULL,NULL,%s,%s) ON CONFLICT(id) DO UPDATE SET notes=excluded.notes,feature_list=excluded.feature_list",
            (
                CONFIG["version"],
                "susceptibility_index",
                json.dumps(list(CONFIG["weights"])),
                json.dumps(notes),
            ),
        )
        conn.commit()
    (ROOT / "docs/evidence/m2-scoring.json").write_text(
        json.dumps(evidence, indent=2), encoding="utf-8"
    )
    print(json.dumps(evidence, indent=2))


if __name__ == "__main__":
    main()
