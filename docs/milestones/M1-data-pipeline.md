# M1 — Data pipeline

Status: complete with the PRD-approved weak-SAR-evidence exception; M0 completed and pushed as `12f4c86`.

## Implemented and verified so far

- Reused 51 hash-verified rasters from the interrupted turn; no repeat satellite downloads.
- 380 named source settlements, 38,083 regular 250 m cells in EPSG:32643 and 47,843 exact cell–village intersections.
- OSM: 57 bounded parent extracts, dense tiles subdivided on the provider's 50,000-node limit; 95 river/stream ways and 1,897 primary/secondary/tertiary road ways. Cached IDs deduplicated.
- WorldPop: constrained 2020 UN-adjusted population band preserved on its native grid; native pixels assigned once by centre, stable village-ID ownership in overlaps. Sum is 2,470,371.0796 across observed village pixels and exactly the same across grid assignments.
- Nine villages have no valid population pixels (2.37%); these remain null. Validation allows at most 5% missing village values as a documented prototype completeness threshold, not a scientific guarantee. API/priority behavior must expose these missing values.
- Reanalysis scenarios: pooled June–September 2015–2024 values at four tehsil sample points; 4,880 daily observations. Normal 3.70/13.50 mm, Heavy 29.70/78.51 mm, Extreme 53.34/140.52 mm (24h/72h).
- SAR: matched descending relative orbit 136, linear-power speckle mean, before/during median composites, Otsu change threshold with explicit water/slope screens. 2019: 5.933% coverage, 8,058 proxy pixels. 2021: 100% rasterized study coverage, 14,383 proxy pixels. Missing cells stay unknown. The 2021 acquisition is 22 July, before the documented 25 July rescue operations; neither mask is claimed as peak or complete inundation.

## Verification

Linux Docker verification: `pytest data_pipeline/tests -q`: **10 passed**; `python data_pipeline/validation.py --stage all`: **passed**; Ruff passed and Black formatted all pipeline modules. The single Rasterio warning concerns future affine multiplication syntax, not a failed check.

PostGIS contains 380 villages, 38,083 grid cells (zero invalid geometries), 47,843 grid–village intersections, two historical events, 76,166 evidence rows, three rainfall scenarios and 95 waterways. See `m1-postgis.json`. The 3.9 MB processed seed restored into a separate empty local database, and the real PostGIS integration test passed against that restore.

Visually inspected `docs/evidence/m1-sar-inspection.png`: the 2019 northern strip contains river-adjacent detections in Shirol; most of the study area is explicitly grey/unobserved. The 2021 mask has sparse detections along waterways, including Shirol. Official NDRF/PIB reports establish affected tehsils, not pixel-level truth. This is a plausibility check, not validation of peak extent. M1 proceeds under its explicit weak-label fallback; Gate B must assess whether supervised training is defensible.

## Engineering decisions

Windows Application Control blocked the psycopg binary driver and Matplotlib extension. PostgreSQL uses pure-Python pg8000. Scientific plotting runs in an isolated Linux Python container. No Windows policy was disabled. The PostGIS loader uses bounded 500-row inserts in a transaction; interrupted loads roll back. Large rasters and intermediates remain gitignored; a compact processed seed supports future fresh clones.

## Next milestone

M2: execute Gate B and implement the approved susceptibility index if the evidence cannot support supervised validation. No ML metrics exist.
