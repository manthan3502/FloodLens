# Local development

## Fresh clone: application without satellite credentials

Install Git, Node.js 22.12+ (24 tested) and Docker Desktop with Linux containers. Python on the host is optional. Use PowerShell from the repository root:

```powershell
git clone https://github.com/manthan3502/FloodLens.git
cd FloodLens
Copy-Item .env.example .env
docker compose up -d --wait db
docker compose build api
docker compose run --rm api alembic -c backend/alembic.ini upgrade head
docker compose run --rm api python -m data_pipeline.seed
docker compose run --rm api python -m data_pipeline.score
docker compose up -d api
cd frontend
npm ci
npm run dev
```

Open http://localhost:5173. The API is http://localhost:8000 and OpenAPI is `/docs`. The processed real-data seed needs no Earth Engine access. Do not copy raw data or credentials into the clone. This project is private until its owner changes visibility; GitHub access is needed to clone it.

Keep `.env` local. The included password is for localhost development only. After changing API origin, set `VITE_API_BASE_URL` in `frontend/.env.local` and rebuild/restart Vite; set the exact frontend origin in `CORS_ALLOWED_ORIGINS`. Production requires HTTPS origins and a TLS database connection. Restart the API after a data refresh because feature snapshots are cached.

For a second isolated local stack, set `API_PORT=8001`, `DB_PORT=5433` in its `.env`, then use `docker compose -p floodlens-check ...` consistently. Add `http://localhost:5174,http://127.0.0.1:5174` to its CORS setting; frontend `.env.local` uses `VITE_API_BASE_URL=http://localhost:8001`; run `npm run dev -- --port 5174`. These overrides avoid disturbing the primary stack.

## Verification

```powershell
docker compose run --rm api python -m pytest backend/tests -q
docker compose run --rm api ruff check backend data_pipeline scripts
docker compose run --rm api black --check backend data_pipeline scripts
docker compose exec -T api python scripts/smoke_api.py
cd frontend
npm test
npm run lint
npm run build
```

Backend integration tests read the seeded database. For isolated testing use the second-stack instructions above. Browser checks use Playwright with Edge: install Playwright locally or set `PLAYWRIGHT_MODULE` to its module path, then run `node scripts/verify-workflow.cjs` and `node scripts/verify-integration.cjs`. M4's earlier test remains available as `scripts/verify-m4.cjs`.

## Full offline pipeline verification

```powershell
docker build -f data_pipeline/Dockerfile.visualqa -t floodlens-pipeline .
$env:DATABASE_URL = ((Get-Content .env | Where-Object { $_ -like 'DATABASE_URL=*' }) -split '=',2)[1] -replace 'localhost','db'
docker run --rm --network floodlens_default --env DATABASE_URL --volume "${PWD}:/work" floodlens-pipeline python -m pytest backend/tests data_pipeline/tests -q
docker run --rm --volume "${PWD}:/work" floodlens-pipeline python data_pipeline/validation.py --stage all
```

Full raster validation requires the ignored `data/interim` artifacts generated offline; its recorded real-data result is in `docs/evidence/m1-validation.json`. A fresh clone uses the seed and database integration checks instead of claiming to regenerate missing raw rasters. Linux execution avoids Windows Application Control restrictions on compiled scientific libraries without changing host security policy.

## Reprocess sources only when refreshing data

Authenticate Earth Engine locally (`earthengine authenticate --auth_mode=localhost:8085`), set `GEE_PROJECT` to your registered project, then run the modules in order: `data_pipeline.feasibility`, `data_pipeline.processing.grid`, `data_pipeline.ingestion.osm`, `data_pipeline.ingestion.rainfall`, `data_pipeline.ingestion.gee_rasters`, `data_pipeline.processing.features`, `data_pipeline.validation`, `data_pipeline.load`, `data_pipeline.score`. Source audit and extraction dates are in `docs/data-sources.md`. Never commit OAuth tokens, service-account credentials or `.env`.
