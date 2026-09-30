# M0 — Feasibility + Foundation

**Status: COMPLETE. Gate A: GO WITH REDUCED SCOPE, 2026-09-29 IST.**

## Final acceptance decision

Docker/PostGIS, API tests, frontend build/test/lint and the real browser map check passed. Local Google consent is complete. Actual SRTM, constrained WorldPop and Sentinel-1 GeoTIFF clips were downloaded and opened, with valid pixels and recorded hashes. Raster nodata `-99999` is excluded explicitly; other negative population values are rejected.

Use `USGS/SRTMGL1_003` and the **population band** of `WorldPop/GP/100m/pop_age_sex_cons_unadj` (2020, constrained, UN-adjusted per the official catalog). This is an explicit equivalent constrained population product via GEE, not a silent switch to unconstrained GP. Stop the slow unadjusted country download; incomplete bytes remain ignored.

DataMeet polygons are usable as the primary units across the four tehsils: 380 named settlements after dissolving repeated named parts. Nine unnamed pieces and incomplete independent Hatkanangale coverage are documented exceptions requiring explicit M1 treatment, not invented village IDs or labels. Real OSM roads/rivers and rainfall are accessible; M1 must verify full feature coverage.

**Reduced scope:** 2019 event-window Sentinel-1 coverage is absent at all four feasibility sample locations; monsoon inventory and GRD_FLOAT cross-check confirm the gap. July 2021 coverage is accessible. Per PRD M1's weak-label fallback, carry unavailable observations as unknown into Gate B; do not manufacture 2019 labels, claim two-event validation, or equate unknown with dry. The pre-approved susceptibility-index decision remains for M2 after actual mask quality checks. No district switch, tehsil shrink or new feature was introduced.

Reproducible evidence: `m0-runtime-recheck.json`, `gee-raster-clips.json`, `sentinel-scene-inventory.json`, `boundary-identifiers.json`, `tehsil-coverage.json`, `rainfall-tehsil-probes.json`, `osm-samples.json`, `browser-m0.json`. Earlier entries below preserve the investigation history; this final decision supersedes their pending status.

## Implemented

Git initialized on `main`; FastAPI `/health`; React/Vite/TypeScript Leaflet foundation; PostGIS Compose configuration; environment template and ignore rules; Python and frontend tests/lint; real dataset probes and download evidence; initial architecture, methodology, limitations and learning notes.

## Verification so far

- Backend: 2 tests passed, including liveness and rejection of an unknown CORS origin.
- Running HTTP API: `/health` returned `{"status":"ok"}`.
- Frontend: production build, 1 actual Leaflet render test and ESLint passed.
- Dependency audit after updating Vitest to 4.1.11: zero known npm vulnerabilities reported.
- Python: Ruff and Black checks passed for backend and feasibility scripts.
- Real browser: Edge loaded 21 map tiles with no page errors; screenshot visually inspected (`docs/evidence/m0-map.png`). The in-app browser failed to initialize twice; the installed Playwright runtime provided verification.
- PostGIS: **passed on 2026-09-29 IST**. Docker 29.8.1, Compose v5.5.1; `docker compose up -d --wait` produced a healthy database. Actual SQL returned PostGIS 3.5, a passing EPSG:4326 → EPSG:32643 → EPSG:4326 round-trip, and valid point GeoJSON. See `docs/evidence/m0-runtime-recheck.json`.

## Gate A

See `docs/data-sources.md` and machine-readable `docs/evidence/*.json`. Real rainfall records fetched; both boundary candidates downloaded. Copernicus GLO-30 returned 1,024 elevation pixels. Direct OSM API samples fetched for all four target areas after Overpass failures. Full coverage, WorldPop clipping and Earth Engine remain unverified. No village/grid-cluster fallback decision has been made. Authentication failure must not be misrepresented as unusable flood labels.

DataMeet: 136 Karvir + 137 Panhala + 68 Hatkanangale (source spelling `Hatkalangale`) + 56 Shirol polygons; all valid, none empty or duplicate. Available IITB reference coverage fractions: Karvir 0.9977, Panhala 0.9964, Shirol 0.9943. Hatkanangale's tehsil reference is absent from that archive. Census 2001 identifiers are nonunique in three tehsils and require reconciliation. No authoritative completeness claim is made.

## Manual prerequisites

PRD §36 A applies to Earth Engine authorization and the Windows permissions needed to install/start Docker with WSL. Requests were issued while independent foundation work continued. Existing Git Credential Manager authentication for `manthan3502` was verified without exposing its token.

### Resumed checks — 2026-09-29 IST

Docker/WSL setup is complete and verified; no further Docker installation action is needed. The user supplied registered project `floodlens-510018`. The local Earth Engine Python client still returns an authorization-required error: noncommercial project registration did not create local OAuth credentials. Started `earthengine authenticate --auth_mode=localhost:8085`; the command is waiting for Google sign-in/consent. This is PRD §36 A, not a label-quality failure and not a Gate B decision.

All eight rainfall queries (four tehsils × two event windows) returned HTTP 200 with no null daily values. Boundary identifier audit found 380 named unique settlements; repeated named codes have matching names and can be dissolved into multipart polygons. Nine unnamed shapes need explicit treatment in M1. These findings are recorded in `rainfall-tehsil-probes.json` and `boundary-identifiers.json`.

WorldPop remote byte-range retry returned HTTP 200 and the whole 531,062,384-byte object instead of HTTP 206. A separate streaming full-download attempt writes only to ignored `.download` storage; population pixels remain unverified until a complete file or another approved product is read successfully. Gate A remains OPEN.

## Git record

Foundation commit `d32dd6f` pushed to the public repository https://github.com/manthan3502/FloodLens. A separate M0 feasibility commit records source evidence and follow-up scripts. Use `git log --oneline` for its exact hash. No commit claims that Gate A passed. Raw data, credentials and local tools are ignored.

## Next action

Commit and push the completed M0 evidence, then immediately begin M1 data processing. M2–M8 remain unstarted.
