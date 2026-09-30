# Deployment

Status: deployed and production-verified on 30 September 2026. [Gate D evidence](gate-d.md).

- Frontend: https://floodlens-lilac.vercel.app
- API: https://floodlens-nz9r.onrender.com
- Health: `GET /health`; villages: `GET /villages`; dashboard data: `POST /scenarios/evaluate`. Routes have no `/api/v1` prefix.
- Render: `ENV=production`, private `DATABASE_URL`, `CORS_ALLOWED_ORIGINS=https://floodlens-lilac.vercel.app`. Render supplies `PORT`.
- Vercel: `VITE_API_BASE_URL=https://floodlens-nz9r.onrender.com`.

## Topology

Vercel Hobby hosts `frontend/`; Render's explicitly **free** Docker service runs FastAPI; Supabase Free stores PostGIS data. `render.yaml` never defaults to a paid plan. The Docker image contains the 3.9 MB source-derived seed, not raw rasters. On startup, `scripts/deploy/start.py` immediately binds Render's port with a 503 initialization response, applies migrations, resumes an incomplete seed only when required, scores missing metadata, then replaces the initialization listener with Uvicorn on the same port.

## Account setup required from the owner

1. Sign in to [Supabase](https://supabase.com/dashboard), [Render](https://dashboard.render.com/) and [Vercel](https://vercel.com/login). Use free plans only. Authorize access to the existing public GitHub repository when prompted.
2. Create a free Supabase project for FloodLens. Keep its database password private. Its Connect dialog provides a PostgreSQL URL; use the **session pooler on port 5432** when direct IPv6 connectivity is unavailable, and append `?sslmode=verify-full`. URL-encode special characters in the password. The backend image includes Supabase's public Root 2021 CA and passes a verified SSL context to pg8000. Use the database owner for initialization; the browser must never receive this URL.
3. Import the repository's Render Blueprint. Set DATABASE_URL privately and CORS_ALLOWED_ORIGINS to the eventual exact HTTPS Vercel production origin. `ENV=production` requires explicit HTTPS CORS and verified database TLS. No card or paid plan is needed for this configuration; stop if the provider requires payment.
4. Import the repository into Vercel with Root Directory `frontend`. Set `VITE_API_BASE_URL` to the HTTPS Render URL. Deploy, set the final Vercel production origin in Render, and restart the API if needed. Preview origins are not broadly wildcarded.

For agent-driven deployment via APIs instead of dashboard steps, put credentials in the ignored root `.env.deploy` file (never chat): VERCEL_TOKEN, RENDER_API_KEY, SUPABASE_ACCESS_TOKEN if project creation is needed, and DATABASE_URL after project creation. Non-secret project/service IDs and URLs may be shared. Existing CLI login is also usable. Never commit the file.

## Production verification

Run `scripts/smoke_api.py` with API_BASE_URL set to the HTTPS API. Open the frontend in a fresh browser context and complete Normal→Extreme→five teams→three teams→village detail; inspect network/console errors and map/list agreement. Repeat backend tests with a separate deployed test database/configuration where appropriate; do not point destructive test fixtures at production. The final run passed: all seven API routes, three rainfall presets, five/three teams, village details, map/list agreement, CORS and mobile layout. See `docs/evidence/production-smoke.json`. Production database tests were reviewed as read-only; all 57 passed with production TLS/CORS configuration.

## Current provider limitations

[Render Free documentation](https://render.com/docs/free) says idle services sleep after 15 minutes and can take about a minute to restart; the disk is ephemeral, and free services lack shell/one-off jobs. Startup initialization avoids depending on those features. Supabase persists the database externally; no raw processing runs on Render. Limits or suspension must be documented rather than bypassed with keep-alive traffic. [Supabase connection guidance](https://supabase.com/docs/guides/database/connecting-to-postgres) explains pooler/IPv4 choices; [PostGIS guidance](https://supabase.com/docs/guides/database/extensions/postgis) covers the extension. This is a personal academic demo under [Vercel Hobby](https://vercel.com/docs/plans/hobby), not a claim of production-grade availability.

Row-level security is enabled on application tables without anonymous policies; the backend uses its private database connection. This prevents Supabase's automatic public API from becoming a write path. No Supabase browser key is needed.
