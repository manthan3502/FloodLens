# Learning notes

## M0 — Foundation (in progress)

### What was built and why

The project now has a Python web API, a React map, database configuration and repeatable data-source probes. This separates environment problems from scientific-data problems before building scores on unverified inputs.

### Important files and libraries

- `backend/app/main.py`: FastAPI receives HTTP requests; Uvicorn runs the server.
- `frontend/src/App.tsx`: React renders the page; Leaflet draws the map and tiles.
- `docker-compose.yml`: describes a PostgreSQL server with the PostGIS spatial extension and persistent storage.
- `data_pipeline/feasibility*.py`: HTTPX checks real sources; Rasterio reads rasters.
- `data_pipeline/inspect_boundaries.py`: Shapely checks polygons; Pyogrio reads shapefile metadata.
- `docs/evidence/`: actual probe results, distinct from assumptions.

### Concepts and decisions

A monorepo keeps the API, frontend, pipeline and documentation together. PostGIS adds geometry types, spatial indexes and queries to PostgreSQL. Docker Compose describes the local database reproducibly; a YAML file alone does not prove that the database runs. CORS controls which browser origins may read the API. Gate A checks real data before downstream work starts.

### Five interview questions

1. **Why PostGIS?** It can join and query geographic shapes and export GeoJSON without reimplementing spatial operations in the API.
2. **Why a monorepo?** One small project can keep API contracts, pipeline changes and UI changes in the same version history.
3. **What does the health endpoint prove?** That the web process answers requests. This liveness endpoint does not prove data readiness.
4. **Why test data access first?** A published dataset name is not proof that its files, permissions or coverage work for our region.
5. **What is CORS?** A browser policy for cross-origin API access. We allow the known frontend origins rather than every website.

### Current lesson

Both village sources can be downloaded; that alone does not establish coverage quality. Earth Engine needs real authorization. Missing authorization is not evidence of poor SAR label quality and cannot justify the Gate B index fallback by itself.
