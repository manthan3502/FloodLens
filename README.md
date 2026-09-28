# FloodLens

Geospatial flood susceptibility and emergency-response prioritization for rural Kolhapur, Maharashtra.

**Status: M0 in progress. Not deployed. No risk results or flood labels have been produced.**

The approved [final PRD](docs/floodlens_final_prd.md) is the implementation specification. The study area is Karvir, Panhala, Hatkanangale and Shirol. Milestones proceed only when their acceptance checks pass.

## Current foundation

- FastAPI liveness endpoint at `/health`.
- React, TypeScript, Vite and Leaflet map centered on Kolhapur.
- Local PostGIS Docker Compose configuration.
- Repeatable Gate A source probes with recorded HTTP results and download hashes.
- Backend and frontend tests, lint and build commands.

## Development

See [local development](docs/local-development.md), [M0 evidence](docs/milestones/M0-foundation.md), [data sources](docs/data-sources.md) and [learning notes](docs/learning-notes.md).

## Intended methodology

A 250 m grid will combine terrain, rivers, historical satellite evidence, rainfall scenarios and population estimates. Gate B will choose supervised ML only if actual Sentinel-1 labels support it; otherwise the approved susceptibility index applies.

Priority will be `0.65 × normalized risk + 0.35 × normalized population exposure`, with configurable weights. Accessibility is context only. These are prototype decision-support weights, not validated operational policy.

## Responsible use

This academic prototype estimates relative susceptibility. It does not predict exact flood timing, depth or location, and must not be the sole basis for evacuation or resource deployment.
