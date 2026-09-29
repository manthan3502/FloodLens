from contextlib import closing

from data_pipeline.load import connect


def test_real_postgis_data_and_unknown_observations():
    with closing(connect()) as conn, closing(conn.cursor()) as cursor:
        cursor.execute(
            "SELECT count(*), count(*) FILTER (WHERE NOT ST_IsValid(geom)), count(DISTINCT ST_SRID(geom)) FROM grid_cells"
        )
        count, invalid, crs_count = cursor.fetchone()
        assert count > 30000
        assert invalid == 0
        assert crs_count == 1
        cursor.execute(
            "SELECT count(*) FROM grid_flood_evidence WHERE coverage_fraction=0 AND flooded IS NOT NULL"
        )
        assert cursor.fetchone()[0] == 0
        cursor.execute("SELECT count(*),count(population_estimate) FROM villages")
        total, known = cursor.fetchone()
        assert (total, known) == (380, 371)
