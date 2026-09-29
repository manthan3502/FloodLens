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

Open http://localhost:5173. The M0 map remains a preview until M4. A real processed seed is available under `data/processed/`.

## M1 seed and Linux verification

The Linux verification image avoids host-specific compiled-library restrictions. From the repository root:

```powershell
docker build -f data_pipeline/Dockerfile.visualqa -t floodlens-visualqa data_pipeline
$env:DATABASE_URL = ((Get-Content .env | Where-Object { $_ -like 'DATABASE_URL=*' }) -split '=',2)[1] -replace 'localhost','db'
docker run --rm --network floodlens_default --env DATABASE_URL --volume "${PWD}:/work" floodlens-visualqa python -m data_pipeline.seed
docker run --rm --network floodlens_default --env DATABASE_URL --volume "${PWD}:/work" floodlens-visualqa python -m pytest data_pipeline/tests -q
```

The seed needs no Earth Engine credentials. Full raster validation and mask plotting additionally require the ignored offline intermediates; tests use small fixtures plus the restored PostGIS data. Reproducing raw ingestion requires Earth Engine authorization and the documented source pipeline.

## Checks

M3's backend can run entirely in Docker after `.env` exists:

```powershell
docker compose build api
docker compose run --rm api alembic -c backend/alembic.ini upgrade head
docker compose run --rm api python -m data_pipeline.seed
docker compose run --rm api python -m data_pipeline.score
docker compose up -d api
```

The API listens on http://localhost:8000. Do not run another Uvicorn on the same port. The feature snapshot is fixed for a run; restart the API after loading new data. `scripts/smoke_api.py` checks all endpoints over HTTP.

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
