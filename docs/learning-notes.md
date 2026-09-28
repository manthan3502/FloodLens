# Learning notes

## M0 â€” Foundation (complete)

M0 completion update: PostGIS, Earth Engine authentication, real raster downloads, rainfall and boundary probes passed. Gate A is GO WITH REDUCED SCOPE because 2019 SAR availability is incomplete. This demonstrates why dataset feasibility must be tested rather than assumed from catalog names. A missing observation is unknown, not evidence that no flooding occurred. The constrained population product is selected explicitly; nodata is not a negative population.

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

The sources use different spellings for Hatkanangale. Always inspect attribute values before concluding that an area is missing. All 397 target DataMeet polygons are valid, yet three tehsils have repeated Census identifiers: geometry validity and identifier quality are separate checks. The map passed a real Edge browser check, and the first foundation commit was pushed as `d32dd6f` while M0 remained open.

### Resumed M0: permissions and geometry

Docker now runs the real PostGIS database. We tested coordinate conversion into metres and back, plus GeoJSON serialization inside PostgreSQL. This proves spatial functions actually execute, beyond a container simply starting.

Earth Engine project registration establishes an eligible project; OAuth consent gives this particular local client permission to act as your account. Both are necessary. A project ID is not a credential.

Repeated village IDs sometimes represent separate pieces of the same settlement. The named repeated IDs here have matching names; M1 can dissolve these shapes into one multipart geometry. Blank names with truncated codes cannot be treated as known villages. The 397 raw polygons represent 380 named settlements plus nine unnamed polygons after combining repeated named pieces.
