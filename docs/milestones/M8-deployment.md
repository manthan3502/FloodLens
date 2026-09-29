# M8 — Deployment, documentation and portfolio

Status: **in progress — cloud authentication required (PRD §36.A)**. Gate D pending; no production URL exists yet.

## Completed independent work

- Render Blueprint explicitly selects the free Docker plan; Vercel Vite configuration added. Verified-TLS PostgreSQL connections and explicit production HTTPS CORS are required.
- Deployment startup applies migrations, seeds an empty database and scores missing metadata before Uvicorn. Tested with a new empty local database: 380 settlements and 38,083 cells loaded, scoring hashes matched, all seven HTTP endpoints returned 200.
- Migration 0002 enables row-level security on 11 tables so a managed database's anonymous API cannot become a write path. Local SQL confirmed all 11 protected; backend owner connections still work.
- README, architecture, methodology, source audit, scoring card, limitations, student notes, local setup, deployment instructions, MIT software license and demo walkthrough prepared. Source-data licenses remain separate.
- Desktop/mobile/error screenshots and real local browser demo material captured. Local assets are not presented as production proof.
- GitHub CI run [36571888866](https://github.com/manthan3502/FloodLens/actions/runs/36571888866) succeeded for M7 commit `c648fcc`.

## Actual access result

Vercel CLI 61.0.0 `whoami` returned **Logged out**. No deployment token environment variables or ignored `.env.deploy` file were present. Browser-control initialization failed twice with “trusted Node process exited unexpectedly.” No cloud resources were created, no paid plans selected, and no tokens invented. Authentication request was sent to the owner while independent documentation continued.

## Remaining work

Authenticate Vercel/Render/Supabase, provision only free resources, deploy and initialize PostGIS, set exact frontend/backend origins, run cold-browser production workflow and HTTP smoke tests, record actual URLs and production evidence, then run Gate D and make the final completion commit. Repository visibility remains private unless the owner authorizes changing it.

Do not mark FloodLens complete until deployment and production verification pass.

Final local verification after deployment preparation: all 52 Python tests passed against the bootstrap-created database with row-level security enabled; six frontend tests, lint and build passed. Recorded local demo: `docs/evidence/floodlens-local-demo.webm` (about 1.5 MB). `scripts/verify-production.cjs` requires actual HTTPS application/API URLs and remains unrun until cloud access exists.

Final startup race fixed: Compose now checks API liveness, and documented startup waits for health before verification. A retry after server initialization had already confirmed all endpoints; the health check makes that ordering explicit.
