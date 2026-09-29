"""Write validated artifacts to PostGIS atomically; never replace remote tables."""

import gzip
import json
import math
import os
from contextlib import closing
from urllib.parse import unquote, urlparse

import pg8000.dbapi

from data_pipeline.feasibility import ROOT


def database_url():
    url = os.environ.get("DATABASE_URL")
    if not url:
        for line in (ROOT / ".env").read_text().splitlines():
            if line.startswith("DATABASE_URL="):
                url = line.split("=", 1)[1]
    if not url:
        raise ValueError("DATABASE_URL is required")
    return url.replace("postgresql+psycopg://", "postgresql://").replace(
        "postgresql+pg8000://", "postgresql://"
    )


def number(value):
    return None if value is None or not math.isfinite(value) else float(value)


def connect():
    url = urlparse(database_url())
    return pg8000.dbapi.connect(
        user=unquote(url.username),
        password=unquote(url.password or ""),
        host=url.hostname,
        port=url.port or 5432,
        database=url.path.lstrip("/"),
    )


def multi(geom):
    from shapely import MultiPolygon

    return MultiPolygon([geom]) if geom.geom_type == "Polygon" else geom


def bulk_execute(cursor, sql, records):
    prefix, rest = sql.split("VALUES ", 1)
    template, suffix = rest.split(" ON CONFLICT", 1)
    for start in range(0, len(records), 500):
        batch = records[start : start + 500]
        statement = (
            prefix
            + "VALUES "
            + ",".join([template] * len(batch))
            + " ON CONFLICT"
            + suffix
        )
        cursor.execute(statement, [value for row in batch for value in row])


def main():
    import geopandas as gpd

    folder = ROOT / "data/interim"
    villages = gpd.read_file(folder / "villages-features.gpkg")
    grid = gpd.read_file(folder / "grid-features.gpkg")
    parts = gpd.read_file(folder / "grid-village-parts.gpkg")
    rivers = gpd.read_file(folder / "osm.gpkg").query("kind == 'river'")
    rainfall = json.loads((folder / "rainfall-scenarios.json").read_text())["scenarios"]
    evidence = json.loads((ROOT / "docs/evidence/m1-feature-summary.json").read_text())
    with closing(connect()) as conn:
        with closing(conn.cursor()) as cursor:
            for statement in (ROOT / "data_pipeline/schema.sql").read_text().split(";"):
                if statement.strip():
                    cursor.execute(statement)
            cursor.execute(
                "INSERT INTO districts VALUES ('kolhapur','Kolhapur study villages',ST_Multi(ST_GeomFromWKB(%s,32643))) ON CONFLICT(id) DO UPDATE SET geom=excluded.geom",
                (villages.geometry.union_all().wkb,),
            )
            bulk_execute(
                cursor,
                "INSERT INTO villages VALUES (%s,'kolhapur',%s,%s,%s,%s,ST_GeomFromWKB(%s,32643)) ON CONFLICT(id) DO UPDATE SET population_estimate=excluded.population_estimate,geom=excluded.geom",
                [
                    (
                        r.id,
                        r.name,
                        r.tehsil,
                        r.source,
                        number(r.population_estimate),
                        multi(r.geometry).wkb,
                    )
                    for r in villages.itertuples()
                ],
            )
            bulk_execute(
                cursor,
                "INSERT INTO grid_cells VALUES (%s,%s,%s,%s,%s,%s,%s,ST_GeomFromWKB(%s,32643)) ON CONFLICT(id) DO UPDATE SET elevation=excluded.elevation,slope=excluded.slope,dist_to_river=excluded.dist_to_river,dist_to_road=excluded.dist_to_road,population=excluded.population,geom=excluded.geom",
                [
                    (
                        r.id,
                        r.village_id,
                        r.elevation,
                        r.slope,
                        r.dist_to_river,
                        r.dist_to_road,
                        number(r.population),
                        r.geometry.wkb,
                    )
                    for r in grid.itertuples()
                ],
            )
            grouped = parts.groupby(["grid_cell_id", "village_id"]).area_m2.sum()
            bulk_execute(
                cursor,
                "INSERT INTO grid_village_parts VALUES (%s,%s,%s) ON CONFLICT(grid_cell_id,village_id) DO UPDATE SET area_m2=excluded.area_m2",
                [(g, v, float(area)) for (g, v), area in grouped.items()],
            )
            for year, date in [(2019, "2019-08-14"), (2021, "2021-07-22")]:
                cursor.execute(
                    "INSERT INTO historical_flood_events VALUES (%s,%s,%s,%s,%s) ON CONFLICT(id) DO UPDATE SET source_method=excluded.source_method",
                    (
                        year,
                        f"{year} SAR event-window proxy",
                        date,
                        evidence["events"][str(year)]["method"],
                        f"data/interim/flood-{year}.tif",
                    ),
                )
                records = []
                for row in grid.itertuples():
                    fraction = number(getattr(row, f"flood_fraction_{year}"))
                    coverage = float(getattr(row, f"evidence_coverage_{year}"))
                    # A label needs at least 80% observed pixels; fraction remains
                    # available separately to document partial coverage.
                    flooded = (
                        fraction >= 0.1
                        if fraction is not None and coverage >= 0.8
                        else None
                    )
                    records.append((row.id, year, flooded, fraction, coverage))
                bulk_execute(
                    cursor,
                    "INSERT INTO grid_flood_evidence VALUES (%s,%s,%s,%s,%s) ON CONFLICT(grid_cell_id,event_id) DO UPDATE SET flooded=excluded.flooded,flood_fraction=excluded.flood_fraction,coverage_fraction=excluded.coverage_fraction",
                    records,
                )
            bulk_execute(
                cursor,
                "INSERT INTO rainfall_scenarios VALUES (%s,%s,%s,%s) ON CONFLICT(id) DO UPDATE SET rainfall_24h_mm=excluded.rainfall_24h_mm,rainfall_72h_mm=excluded.rainfall_72h_mm",
                [
                    (r["id"], r["name"], r["rainfall_24h_mm"], r["rainfall_72h_mm"])
                    for r in rainfall
                ],
            )
            bulk_execute(
                cursor,
                "INSERT INTO waterways VALUES (%s,%s,ST_GeomFromWKB(%s,32643)) ON CONFLICT(id) DO UPDATE SET geom=excluded.geom",
                [(r.osm_id, r.name, r.geometry.wkb) for r in rivers.itertuples()],
            )
        conn.commit()
    # Portable seed is built from database rows, retaining exact values and WKB.
    output = ROOT / "data/processed"
    output.mkdir(parents=True, exist_ok=True)
    tables = [
        "districts",
        "villages",
        "grid_cells",
        "grid_village_parts",
        "historical_flood_events",
        "grid_flood_evidence",
        "rainfall_scenarios",
        "waterways",
    ]
    with closing(connect()) as conn:
        seed = {}
        for table in tables:
            with closing(conn.cursor()) as cursor:
                cursor.execute(f'SELECT * FROM "{table}"')
                names = [col[0] for col in cursor.description]
                rows = [dict(zip(names, row, strict=True)) for row in cursor.fetchall()]
            seed[table] = rows
        with gzip.open(output / "seed.json.gz", "wt", encoding="utf-8") as file:
            json.dump(seed, file, default=str, separators=(",", ":"))
        counts = {name: len(rows) for name, rows in seed.items()}
    (ROOT / "docs/evidence/m1-postgis.json").write_text(
        json.dumps(counts, indent=2), encoding="utf-8"
    )
    print(counts)


if __name__ == "__main__":
    main()
