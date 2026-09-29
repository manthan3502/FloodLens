# M4 — Frontend and map

Status: complete. Built on M3 commit `ec7cbf0`; preserved interrupted M4 work.

Implemented the real 380-village choropleth, waterways, rainfall presets, API-driven village detail, factor contributions, modeled population, accessibility context, SAR village-summary toggle, methodology dialog and responsive layout. Requests are aborted when selections change. Historical summaries are explicitly not flood-extent boundaries. Priority allocation remains the required M5 placeholder.

Verification: Vite environment declaration fixed the TypeScript build. `npm run build`, `npm run lint`, and `npm test` pass (4 tests). Real Edge browser verification (`scripts/verify-m4.cjs`) passed: 380 rendered polygons, rainfall recoloring, live village details, loading, injected HTTP failure/retry, mobile layout without horizontal overflow, and zero page errors. Desktop/mobile/error screenshots and `m4-browser.json` are under `docs/evidence/`; screenshots were visually inspected.

The declined `.env.example` and `vite-env.d.ts` changes were confirmed absent before applying them. Both localhost and 127.0.0.1 frontend origins are supported. No completed M1–M3 processing was repeated.

Next: M5's exact two-term priority engine and synchronized map/list.
