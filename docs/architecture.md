# Architecture

Approved design: React/Leaflet → FastAPI → PostgreSQL/PostGIS. Offline Python processing prepares spatial features before deployment. Runtime requests apply a cheap rainfall-scenario adjustment and deterministic priority ranking.

## M0 implementation

`backend/app/main.py` serves liveness only and allows the configured frontend origins. `/health` does not test database readiness. `frontend/src/App.tsx` displays the base map and an explicit data-pending state. `docker-compose.yml` defines PostGIS, persistent storage, a health check and a localhost-only database port.

There are no data endpoints, risk models or priority services yet. Those belong to M1–M5 after Gate A resolves.

The analysis CRS will be EPSG:32643 for metre-based distances and areas; map responses will use longitude/latitude GeoJSON. Village polygons are preferred where evidence confirms usable coverage. No fallback has yet been selected.
