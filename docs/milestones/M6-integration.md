# M6 — Full integration

Status: complete. Gate C passed at M5 (`abffb0d`).

Hardened response handling so aborted scenario/detail requests cannot publish stale results. Existing priority requests are debounced and aborted. Ran `scripts/verify-integration.cjs` against the real local stack, deliberately delaying Heavy requests while changing to Extreme and changing teams 5→2→3. Final map outlines, priority IDs and selected detail score all matched the latest Extreme/3 API response after delayed requests settled. Zero page errors. Evidence: `docs/evidence/m6-integration.json`.

Frontend regression tests: 6 passed. M5 already verified the full ordinary demo and deterministic API behavior; M6 adds overlapping-request coverage. No new features or placeholders remain in the runtime workflow. Next: M7 full tests, production configuration review and literal fresh clone.
