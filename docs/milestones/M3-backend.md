# M3 — Backend

Status: complete. M2 pushed as `23e3c3b`.

Implemented Alembic revision 0001 for the PRD tables, including persisted priority weights. SQLAlchemy uses pg8000 and a bounded connection pool. The risk service reads real grid features, invokes M2's index for each requested preset and aggregates exact intersection areas. It exposes raw factors, weighted contributions, unknown SAR coverage, modeled population and separate accessibility context.

All seven specified endpoints work; priority calculation returns the explicitly labeled M5 stub. Villages use EPSG:4326 MultiPolygon GeoJSON with topology-preserving 15 m simplification. Input errors use a consistent field-level 422 shape, missing villages return 404, and database failures return a non-sensitive 503. Requests log path, status and latency.

Verification: **29 backend tests passed** against a separate local PostGIS database restored from the real seed. Migration applied there and to the development database. Live HTTP smoke checks returned 200 for all seven endpoints. Ruff and Black passed after formatting. A geometry-type regression discovered during tests was fixed using ST_Multi after simplification.

The immutable offline feature snapshot is cached per worker; a dataset refresh requires restarting the API. No user records or remote data were deleted. Backend runs in Docker to avoid the host's compiled-library restrictions. Next: M4 frontend and map, with priority data deferred to M5.
