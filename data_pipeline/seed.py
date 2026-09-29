"""Restore the small checked-in processed artifact without Earth Engine access."""

import gzip
import json
from contextlib import closing

from data_pipeline.feasibility import ROOT
from data_pipeline.load import bulk_execute, connect

TABLES = [
    "districts",
    "villages",
    "grid_cells",
    "grid_village_parts",
    "historical_flood_events",
    "grid_flood_evidence",
    "rainfall_scenarios",
    "waterways",
]


def main():
    with gzip.open(
        ROOT / "data/processed/seed.json.gz", "rt", encoding="utf-8"
    ) as file:
        data = json.load(file)
    with closing(connect()) as conn, closing(conn.cursor()) as cursor:
        for statement in (ROOT / "data_pipeline/schema.sql").read_text().split(";"):
            if statement.strip():
                cursor.execute(statement)
        for name in TABLES:
            rows = data[name]
            if not rows:
                continue
            columns = list(rows[0])
            if any(not col.replace("_", "").isalnum() for col in columns):
                raise ValueError("Unexpected artifact column")
            statement = (
                f'INSERT INTO "{name}" ('
                + ",".join(f'"{col}"' for col in columns)
                + ") VALUES ("
                + ",".join(["%s"] * len(columns))
                + ") ON CONFLICT DO NOTHING"
            )
            bulk_execute(
                cursor, statement, [[row[col] for col in columns] for row in rows]
            )
            print(f"Seeded {name}: {len(rows)} source rows", flush=True)
        conn.commit()


if __name__ == "__main__":
    main()
