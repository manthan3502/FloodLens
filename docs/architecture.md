# Architecture

## M3 runtime

`docker compose` runs PostGIS and FastAPI. `app/core/db.py` supplies a bounded SQLAlchemy/pg8000 pool; Alembic versions the schema. `app/services/risk_service.py` caches the immutable feature snapshot, computes the selected index scenario and area-weights exact grid intersections. GeoJSON is transformed to EPSG:4326 and simplified by 15 m with topology preserved. Dataset updates require an API restart. Model metadata contains the index configuration and null ML metrics. Consistent errors and request timing surround the routers.

Approved design: React/Leaflet → FastAPI → PostgreSQL/PostGIS. Offline Python processing prepares spatial features before deployment. Runtime requests apply a cheap rainfall-scenario adjustment and deterministic priority ranking.

## M0 implementation

`backend/app/main.py` serves liveness only and allows the configured frontend origins. `/health` does not test database readiness. `frontend/src/App.tsx` displays the base map and an explicit data-pending state. `docker-compose.yml` defines PostGIS, persistent storage, a health check and a localhost-only database port.

M1 has populated PostGIS feature tables and a compact versioned seed. The grid–village intersection table preserves exact weights for future village aggregation. Offline modules under `data_pipeline/` ingest, extract, validate and load these features. Linux Docker runs scientific verification where Windows Application Control blocks binary extensions. There are no data endpoints, risk models or priority services yet; those belong to M2–M5.

The analysis CRS will be EPSG:32643 for metre-based distances and areas; map responses will use longitude/latitude GeoJSON. Village polygons are preferred where evidence confirms usable coverage. No fallback has yet been selected.
