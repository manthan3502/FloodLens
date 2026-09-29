# Methodology status

No model has been trained and no risk scores have been generated. Gate A passed with reduced scope; M1 is complete and Gate B is next.

M1 uses 38,083 full 250 m cells in EPSG:32643 and 47,843 exact village intersections for later area-weighted aggregation. Raster cell means use pixel centres. WorldPop counts are assigned once on their native grid; missing pixels remain unknown. SAR change uses matched descending orbit 136, linear-power 30 m focal means and before/during median VV composites. Otsu's change threshold is capped at −1.5 dB; detections also require slope below 5°, during VV below −15 dB and pre-event VV at least −15 dB. These heuristic screens reduce some false positives but can miss vegetation/urban flooding. Cells with coverage below 80% have unknown binary evidence; fractional change and coverage are retained separately.

The planned method follows PRD §§15–20: 250 m grid features, area-weighted village aggregation, historical Sentinel-1 flood evidence, and observed-source provenance. Rainfall is modeled reanalysis; WorldPop is modeled population.

The priority formula is exactly `w_risk × normalized risk + w_pop × normalized population exposure`, with initial configuration weights 0.65 and 0.35. These are transparent prototype choices, not scientifically fitted values. Accessibility will never be subtracted, and historical severity will not be added again outside the risk term.

Normalization, missing-data behavior, category thresholds and any index weights must be specified and tested when actual input distributions are available. They are not silently invented during foundation work.
