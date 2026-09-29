# M2 — Risk methodology

Status: complete. **Gate B: GO WITH REDUCED SCOPE — susceptibility index.**

M1 (`1376120`, `b17bcd8`) supplies weak temporal SAR evidence: 2019 coverage 5.933%, 2021 single scene before documented peak response. Plausible detections do not supply independent training truth. Applied the approved fallback automatically.

Implemented configurable five-factor index, documented formula/weight rationale and missing-data behavior. `data_pipeline/score.py` computes from real PostGIS features alone, storing metadata with null ML metrics.

Verification: `pytest backend/tests/test_risk_model.py -q`: **14 passed**. Ruff/Black passed. Repeated real-data scoring was identical for 38,083 cells × three scenarios; 114,249 rows persisted. Evidence: `docs/evidence/m2-scoring.json`.

Limitations: uncalibrated prototype weights, coarse uniform rainfall, absolute elevation, weak event evidence and neutral unknown-history assumption. No scientific accuracy claim. No APIs or priority logic added prematurely.

Next: M3 migrations and PostGIS-backed API.
