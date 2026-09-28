# M0 — Feasibility + Foundation

**Status: IN PROGRESS. Gate A OPEN. M1 has not started.**

## Implemented

Git initialized on `main`; FastAPI `/health`; React/Vite/TypeScript Leaflet foundation; PostGIS Compose configuration; environment template and ignore rules; Python and frontend tests/lint; real dataset probes and download evidence; initial architecture, methodology, limitations and learning notes.

## Verification so far

- Backend: 2 tests passed, including liveness and rejection of an unknown CORS origin.
- Running HTTP API: `/health` returned `{"status":"ok"}`.
- Frontend: production build, 1 actual Leaflet render test and ESLint passed.
- Dependency audit after updating Vitest to 4.1.11: zero known npm vulnerabilities reported.
- Python: Ruff and Black checks passed for backend and feasibility scripts.
- Real browser: Edge loaded 21 map tiles with no page errors; screenshot visually inspected (`docs/evidence/m0-map.png`). The in-app browser failed to initialize twice; the installed Playwright runtime provided verification.
- PostGIS: **not run**. Docker is absent and Windows reports WSL is not installed.

## Gate A

See `docs/data-sources.md` and machine-readable `docs/evidence/*.json`. Real rainfall records fetched; both boundary candidates downloaded. Copernicus GLO-30 returned 1,024 elevation pixels. Direct OSM API samples fetched for all four target areas after Overpass failures. Full coverage, WorldPop clipping and Earth Engine remain unverified. No village/grid-cluster fallback decision has been made. Authentication failure must not be misrepresented as unusable flood labels.

DataMeet: 136 Karvir + 137 Panhala + 68 Hatkanangale (source spelling `Hatkalangale`) + 56 Shirol polygons; all valid, none empty or duplicate. Available IITB reference coverage fractions: Karvir 0.9977, Panhala 0.9964, Shirol 0.9943. Hatkanangale's tehsil reference is absent from that archive. Census 2001 identifiers are nonunique in three tehsils and require reconciliation. No authoritative completeness claim is made.

## Manual prerequisites

PRD §36 A applies to Earth Engine authorization and the Windows permissions needed to install/start Docker with WSL. Requests were issued while independent foundation work continued. Existing Git Credential Manager authentication for `manthan3502` was verified without exposing its token.

## Git record

Foundation commit `d32dd6f` pushed to the private repository https://github.com/manthan3502/FloodLens. A separate M0 feasibility commit records source evidence and follow-up scripts. Use `git log --oneline` for its exact hash. No commit claims that Gate A passed. Raw data, credentials and local tools are ignored.

## Next action

Complete Earth Engine authentication and set the project ID; run PostGIS after Docker/WSL installation. Resume source quality checks, especially population, Sentinel-1 and Hatkanangale coverage. Resolve Gate A with evidence, then immediately begin M1. M2–M8 remain unstarted and are not represented by fabricated milestone completion records.
