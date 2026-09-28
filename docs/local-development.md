# Local development

Prerequisites: Python 3.12, Node.js 22.12+ (Node 24 tested), Git, Docker Desktop with a running Linux-container backend.

Run from the repository root in PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements-lock.txt
Copy-Item .env.example .env
docker compose up -d
docker compose exec db psql -U floodlens -d floodlens -c 'SELECT PostGIS_Version();'
.venv\Scripts\python -m uvicorn app.main:app --app-dir backend --reload
```

In another terminal:

```powershell
cd frontend
npm ci
npm run dev
```

Open http://localhost:5173. The M0 map explicitly reports that data verification is pending. No seed dataset exists yet.

## Checks

```powershell
.venv\Scripts\python -m pytest backend
.venv\Scripts\python -m ruff check backend data_pipeline
.venv\Scripts\python -m black --check backend data_pipeline
cd frontend
npm run build
npm test
npm run lint
```

## Source probes

From the root, run `python -m data_pipeline.feasibility`, then `python -m data_pipeline.feasibility_spatial`, `python -m data_pipeline.inspect_boundaries` and `python -m data_pipeline.probe_public_alternatives`. Use the virtual-environment Python. Raw downloads stay ignored under `data/raw/`; small evidence summaries are versioned under `docs/evidence/`.

For Earth Engine, register a noncommercial project, enable the API, then run `.venv\Scripts\earthengine authenticate`. Set `GEE_PROJECT` in the shell to that project ID before the probes. Never paste access tokens or service-account keys into chat or commit them.

This guide is provisional until the M7 fresh-clone verification. On 2026-09-29 IST, Docker Compose started PostGIS successfully and spatial SQL checks passed on this host.

The registered Earth Engine project is `floodlens-510018`. Project registration and local OAuth consent are separate steps. To authorize this Python client, run `.venv\Scripts\earthengine authenticate --auth_mode=localhost:8085`, then complete the Google browser consent. Set `$env:GEE_PROJECT='floodlens-510018'` before running the probes. `python -m data_pipeline.verify_m0_runtime` rechecks the database and per-tehsil Earth Engine access without repeating earlier downloads.
