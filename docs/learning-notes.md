# Learning notes

## M1 — Data pipeline

We converted real village polygons and satellite/rainfall/OSM inputs into a regular 250 m grid. Exact village-cell intersection areas let later scores be averaged without assigning an entire edge cell to just one village. `processing/grid.py`, `ingestion/gee_rasters.py`, `ingestion/osm.py`, `ingestion/rainfall.py`, `processing/features.py`, `validation.py`, and `load.py` are the key files.

GeoPandas organizes geographic tables; Shapely intersects shapes; Rasterio reads raster pixels; Earth Engine extracts satellite data; pg8000 writes to PostGIS. EPSG:32643 is a projected coordinate system measured in metres. Latitude/longitude degrees are unsuitable for a 250 m spacing calculation.

Five interview questions:

1. **Why radar for floods?** Sentinel-1 can observe through clouds. Changes in radar backscatter can indicate water, but vegetation and viewing geometry can mislead it.
2. **What does Otsu do?** It divides a histogram into two groups by maximizing between-group variance. It does not prove those groups are flooded and dry.
3. **Why slope masking?** Steep slopes can create radar shadows that resemble water. We exclude slopes of at least five degrees in this prototype mask.
4. **What is a zonal statistic?** A summary of raster pixels within a shape, such as total modeled population in a village. We preserve the native population grid to avoid changing people-per-pixel counts.
5. **Why keep missing data null?** No observation is not the same as zero population or no flooding. Missingness must stay visible and affect confidence and ranking policy explicitly.

The 2019 SAR overlap is only about 5.9%. The 2021 image predates documented rescue operations. These limitations are evidence for Gate B, not reasons to invent labels or report an accuracy score.

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

Repeated village IDs sometimes represent separate pieces of the same settlement. The named repeated IDs here have matching names; M1 dissolved these shapes into multipart geometry. Blank names with truncated codes cannot be treated as known villages. The 397 raw polygons represent 380 named settlements plus nine unnamed polygons after combining repeated named pieces.

## M3 — PostGIS-backed API

Built FastAPI routes, SQLAlchemy connections and Alembic migrations. The risk service joins exact cell–village intersection areas and calls the index. Key files: `backend/app/api/routes.py`, `services/risk_service.py`, `core/db.py`, `backend/migrations/`. FastAPI/Pydantic validates inputs, PostGIS prepares GeoJSON, and SQLAlchemy manages pooled connections.

1. **What is GeoJSON?** A Feature pairs geometry with properties; a FeatureCollection contains those features. Web coordinates are longitude/latitude.
2. **Why migrate the database?** Versioned schema changes make a fresh installation reproducible without manual table edits.
3. **What do 422, 404 and 503 mean?** Invalid fields, missing object and temporarily unavailable data, respectively.
4. **How does a scenario request work?** Validate its preset, score cached real grid features, area-weight into villages, then serialize the map and explanation fields.
5. **Why cache features?** Offline data stays fixed between processing runs. Caching avoids repeated heavy reads; restart after a refresh so results cannot silently use stale features.

## M2 — Susceptibility scoring

Built a deterministic five-factor index because the SAR dates and coverage cannot support defensible supervised validation. Key files: `backend/app/ml/susceptibility.py`, its JSON config, `data_pipeline/score.py`, and `docs/methodology.md`. Standard Python math implements the formula; pg8000 reads and stores PostGIS rows; pytest checks missing values, bounds and repeatability.

1. **Why no Random Forest?** Sparse 2019 and early 2021 masks are weak labels; fitting them would not establish accurate flood prediction.
2. **Is 0.7 a 70% flood chance?** No. It is a relative index formed from weighted normalized factors.
3. **What is spatial leakage?** Nearby cells share terrain and observations; a random split can make performance look better than geographic holdouts.
4. **What do PR-AUC and temporal holdout mean?** PR-AUC summarizes precision/recall for rare positives. Temporal holdout tests a different event. Neither is claimed here because usable independent labels are missing.
5. **How are unknowns handled?** Required terrain features fail loudly if missing; unknown historical evidence is explicitly assigned neutral 0.5 and flagged. Population stays null and is excluded from susceptibility.

## M4 — Interactive map

Built React/Leaflet components backed by the real API. Important files: `frontend/src/App.tsx`, `api/client.ts`, `components/Map.tsx`, `components/VillageDetail.tsx`. React owns scenario/selection state; Leaflet draws GeoJSON; AbortController prevents old requests from overwriting new selections. Vitest tests interactions and Playwright checks the real browser.

1. **What is a choropleth?** Polygons colored by a measured or computed property, here relative susceptibility.
2. **How does rainfall recolor the map?** The preset triggers an API request; React passes the new GeoJSON to Leaflet.
3. **Why simplify geometry?** Fewer vertices reduce transfer/render costs while topology-preserving simplification retains valid village shapes.
4. **Why show errors explicitly?** A blank or stale map could be mistaken for low risk; loading and unavailable states prevent that interpretation.
5. **Is the dashed overlay actual flood extent?** No. It marks village summaries of incomplete SAR change evidence and is labeled accordingly.
