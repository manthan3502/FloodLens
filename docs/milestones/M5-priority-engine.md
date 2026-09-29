# M5 — Emergency response priority engine

Status: complete. Gate C: **GO**. M4 commit: `d32be23`.

Implemented the exact two-term formula using weights read from PostGIS. Susceptibility already lies in [0,1]; population uses log1p(population)/log1p(study maximum), reducing dominance by very large settlements without changing population order. Unknown population uses the median of known study values for ranking while the response stays null; if all are unknown, normalized population is 0.5. All-known zero population normalizes to zero. Ties use village ID ascending. Accessibility is context only and history is not added again.

Verification: 40 backend tests passed (11 priority tests), 6 frontend tests passed, lint and production build passed. Real Edge workflow passed: 5→3 teams, zero, oversized request→380, rainfall map/list update, five blue map outlines, priority click→detail, repeated API output identical, no page errors. Evidence: `m5-gate-c.json`, `m5-priorities.png` (visually inspected).

Gate C covers real data→scoring→API→map→scenario→detail→priority. No ML or calibrated emergency action claim. One team per village is a greedy prototype allocation, not travel-time optimization.

Next: M6 integration, particularly rapid scenario/team changes.
