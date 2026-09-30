# M8 — Deployment, documentation and portfolio

Status: **complete — Gate D GO, 30 September 2026**. See [the full Definition of Done checklist](../gate-d.md).

## Live deployment

- Dashboard: https://floodlens-lilac.vercel.app
- API: https://floodlens-nz9r.onrender.com
- Database: Supabase PostGIS, accessed through verified TLS.
- Repository remains private; no visibility or paid-plan change was made.

## Final verification

The fresh Edge browser walkthrough rendered 380 real village polygons, exercised Normal → Heavy → Extreme rainfall, five → three teams, village detail, population, five score contributions, SAR highlighting and methodology. Every village score increased with rainfall. Priority responses were deterministic and matched list order, blue map outlines and selected detail. Desktop and 390 px mobile captures were inspected. No page errors or failed API responses occurred. Production CORS accepted the Vercel origin and rejected an unrelated origin.

The measured first load was 16.766 seconds; the full desktop/mobile test took 76.494 seconds. This used a fresh browser session; the Render service was not deliberately suspended. Free-tier wake-up may take longer. Machine-readable results: `docs/evidence/production-smoke.json`.

All seven production API smoke routes returned 200. All **57 Python tests passed locally and against the actual Supabase database with production TLS/CORS settings**. Database tests were reviewed to contain read-only queries; startup tests mock mutations. All **6 frontend tests**, frontend lint/build, Ruff and Black passed. Two upstream deprecation warnings remain, with no skips. M7's real-data validation and literal fresh-clone evidence remain valid and were not repeated.

## Final artifacts and cleanup

README, deployment, architecture, methodology wording, limitations, demo guide and student notes now describe the verified live system. Production screenshots include desktop, mobile and methodology. `docs/evidence/floodlens-production-demo.webm` is the actual production walkthrough recording. The repeatable script is `scripts/verify-production.cjs`.

Reviewed and retained `.gitignore`'s Vercel exclusion and `.vercelignore`. Corrected Black formatting in two deployment files. No unrelated application behavior changed. Secret checks covered tracked environment files, known production credentials in Git history, and private-key/GitHub-token patterns. No matches were found. Local credentials, caches, dependencies and raw rasters remain ignored.

## Deployment fixes retained in history

- `d78f7a0`: manual Docker service runs migration/seed bootstrap.
- `cf7519a`: Supabase public CA loaded with certificate and hostname verification.
- `855e01c`: shared verified TLS for Alembic, API, seed and scoring.
- `7609b1e`: immediate initialization listener, all-table completeness check and Uvicorn handoff.

Supabase bootstrap and data-backed production routes were subsequently verified. Seed progress messages precede the final transaction commit; partial progress logs alone do not prove persisted rows. Subsequent starts check all seed tables and skip a complete import. Render variables remain `ENV`, `DATABASE_URL`, `CORS_ALLOWED_ORIGINS`; Render supplies `PORT`.

## Gate decision

**GO. FLOODLENS COMPLETE** under the approved Gate A/B reduced scope: source-boundary limitations and a transparent susceptibility index. No supervised ML accuracy or operational flood-warning claim is made. The completion commit contains this record, production evidence and the Gate D checklist; Git history identifies the exact commit without a self-referential hash.
