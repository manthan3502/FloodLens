# M7 — Testing and hardening

Status: complete. Setup hardening commit: `b06cdbd`.

Full pinned Linux suite: **52 Python tests passed** (42 backend + 10 pipeline). Full real-data validation passed with zero population conservation error and previously documented null/SAR exceptions. Ruff and Black passed. Frontend: six tests, lint and production build passed; npm reported zero vulnerabilities. Two upstream deprecation warnings remain (Starlette/httpx and Rasterio affine multiplication); no tests were skipped.

Production review: explicit HTTPS CORS required, verified database TLS for production, bounded connection pool, no debug mode, secrets supplied by environment, no raw-data download at runtime. Pinned backend dependencies and immutable migration SQL. Fixed scoring's missing evidence directory on fresh installs and a test subprocess's implicit Python path.

Literal GitHub clone at `b06cdbd` into ignored `.cache/fresh-clone`: new Compose project/volume, migration→real seed→score, `npm ci`→six tests→production build, 42 backend tests and all seven live HTTP endpoints passed. Browser on port 5174/API 8001 rendered 380 villages and completed Extreme→three priorities→detail with no page errors. Only documented port/CORS overrides were applied; no intermediates or credentials were copied. Evidence: `m7-fresh-clone.json`.

Added CI using a real PostGIS service and the processed seed. Remote CI status is not assumed from local success. Next: M8 deployment, documentation and production verification. Gate D is still pending.
