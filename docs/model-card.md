# Scoring card — index-v1

**Type:** deterministic weighted susceptibility index. No supervised ML model is trained. PR-AUC, temporal-holdout metrics and training date are intentionally null.

**Intended use:** academic comparison of source settlements in the four selected Kolhapur tehsils. Not operational warnings, flood-depth estimates or evacuation decisions.

**Inputs:** SRTM elevation/slope, OSM river distance, self-derived 2019/2021 SAR change, fixed reanalysis rainfall presets. Population is excluded from this score and enters the separate response ranking.

**Output:** [0,1] relative index and communication bands. Formula, weights, clipping bounds, neutral unknown-history handling and source rationale are fully specified in `methodology.md` and versioned config. Exact grid intersection areas aggregate to villages.

**Gate B evidence:** 2019 coverage 5.933%; 2021 acquisition 22 July before documented 25 July response. Visual detections are plausible around rivers but not independently validated. A supervised comparison and spatial/temporal validation would not be defensible from this evidence, so the approved fallback was applied.

**Verification:** deterministic repeated scoring of 38,083 cells across three scenarios; required-feature rejection, bounded output and monotonic rainfall tests. This checks implementation correctness, not predictive accuracy.

**Known weaknesses:** absolute elevation is not height above drainage; SAR water/slope screens can miss vegetation and urban floods; coarse uniform rainfall cannot represent local storms; weights/decay scales/categories are prototype assumptions. Unknown H=0.5 can raise cells relative to observed zero and contributes uncertainty up to 0.15 across the full H range. See `limitations.md`.

**Version/data date:** index-v1 / 2026-09-29. Reprocessing requires provenance review and API restart. Future validation should use independent flood extents, weight sensitivity, spatial blocks and event holdouts before any stronger claim.
