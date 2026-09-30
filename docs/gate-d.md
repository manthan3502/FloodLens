# Gate D — Portfolio ready

**GO — FLOODLENS COMPLETE, 30 September 2026.** Gate A/B approved reduced scope remains in force.

[Live dashboard](https://floodlens-lilac.vercel.app) · [API docs](https://floodlens-nz9r.onrender.com/docs) · [Production evidence](evidence/production-smoke.json) · [Demo video](evidence/floodlens-production-demo.webm)

## PRD §48 checklist

| # | Requirement | Verified evidence |
|---|---|---|
| 1 | PASS — Real datasets processed | M1 record; m1-postgis.json; 38,083 cells and 380 settlements |
| 2 | PASS — Risk methodology implemented | M2; index-v1 scoring card and deterministic score tests; approved Gate B fallback |
| 3 | PASS — Data validation passes | M1/M7 evidence; m1-validation.json; documented null/SAR exceptions |
| 4 | PASS — Backend works | Seven live API smoke routes returned 200 |
| 5 | PASS — PostGIS works | 57 tests passed using production Supabase and verified TLS |
| 6 | PASS — Interactive map works | 380 polygons rendered; desktop/mobile screenshots |
| 7 | PASS — Rainfall scenarios work | Normal/Heavy/Extreme; every village score increases |
| 8 | PASS — Village details work | Selected name, index and five contributions verified |
| 9 | PASS — Population exposure works | Detail population matched API; missing population tests pass |
| 10 | PASS — Priority engine works | Five/three teams, deterministic responses, corrected 65/35 weights tested |
| 11 | PASS — Full integration | Live Vercel → Render → Supabase; CORS and map/list/detail agreement |
| 12 | PASS — Automated tests pass | 57 Python tests on local and production DB; 6 frontend tests |
| 13 | PASS — Lint/build pass | Ruff, Black, ESLint and Vite production build |
| 14 | PASS — Deployment works | Public dashboard/API verified; bootstrap fixes retained |
| 15 | PASS — Production smoke passes | production-smoke.json and seven-endpoint smoke |
| 16 | PASS — GitHub updated; real history | M0–M8 commits and final completion push; no fabricated commits |
| 17 | PASS — README complete | Live links, screenshot/video, formulas, setup/tests, responsible use and license |
| 18 | PASS — Methodology documented | docs/methodology.md and docs/model-card.md |
| 19 | PASS — Sources documented | docs/data-sources.md and data/processed/README.md attribution |
| 20 | PASS — Limitations documented | docs/limitations.md, including free-tier cold starts and weak SAR labels |
| 21 | PASS — M0–M8 records exist | docs/milestones/ contains all nine records |
| 22 | PASS — Learning notes exist | docs/learning-notes.md; deployment, TLS and readiness lessons |
| 23 | PASS — Screenshots/demo exist | Four production PNGs and production WebM; screenshots visually inspected |
| 24 | PASS — No committed secrets found | Tracked env-file audit, known production credential and key/token history scan |
| 25 | PASS — Repository clean | Reviewed Vercel ignores retained; final git status checked after commit/push |
| 26 | PASS — Fresh-browser live URL works | Fresh Edge desktop and mobile contexts; 16.766 s initial load; no saved browser state |

## Verification commands and scope

- `docker compose -f docker-compose.yml -f .cache/gate-d-compose.yml run --rm api python -m pytest backend/tests data_pipeline/tests -q`: **57 passed** using the existing Linux geospatial image and local PostGIS.
- `docker run --rm --env-file .env.deploy -e ENV=production -e CORS_ALLOWED_ORIGINS=https://floodlens-lilac.vercel.app -e PYTHONPATH=/work/backend:/work -v D:/Projects/FloodLens:/work floodlens-pipeline python -m pytest backend/tests data_pipeline/tests -q`: **57 passed** against Supabase. Credentials were never printed; DB checks were read-only.
- `ruff check backend data_pipeline scripts`, `black --check backend data_pipeline scripts`: **passed** in the Linux image.
- `npm test`, `npm run lint`, `npm run build` from `frontend`: **6 tests passed**, lint/build passed.
- `scripts/smoke_api.py` with the live API base: **seven routes returned 200**.
- `node scripts/verify-production.cjs` with the documented HTTPS URLs: **passed**, saved screenshot/video/JSON evidence.

These are CI-equivalent runs. Remote GitHub Actions status is reported separately; local success is not presented as a remote CI result. Two upstream deprecation warnings remain (Starlette/httpx and Rasterio); no tests were skipped. The fresh-browser check did not force a sleeping Render instance. Free-tier wake-up can exceed the measured initial load; keep the video available.
