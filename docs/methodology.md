# Methodology status

Gate A and Gate B passed with reduced scope. The implemented method is a weighted susceptibility index, not a trained model or flood probability. M1 commits: `1376120`, `b17bcd8`.

M1 uses 38,083 full 250 m cells in EPSG:32643 and 47,843 exact village intersections for later area-weighted aggregation. Raster cell means use pixel centres. WorldPop counts are assigned once on their native grid; missing pixels remain unknown. SAR change uses matched descending orbit 136, linear-power 30 m focal means and before/during median VV composites. Otsu's change threshold is capped at −1.5 dB; detections also require slope below 5°, during VV below −15 dB and pre-event VV at least −15 dB. These heuristic screens reduce some false positives but can miss vegetation/urban flooding. Cells with coverage below 80% have unknown binary evidence; fractional change and coverage are retained separately.

The implemented method follows PRD §§15–20: 250 m grid features, area-weighted village aggregation, historical Sentinel-1 flood evidence, and observed-source provenance. Rainfall is modeled reanalysis; WorldPop is modeled population.

The priority formula is exactly `w_risk × normalized risk + w_pop × normalized population exposure`, with initial configuration weights 0.65 and 0.35. These are transparent prototype choices, not scientifically fitted values. Accessibility is never subtracted, and historical severity is not added again outside the risk term.

## Gate B decision

**GO WITH REDUCED SCOPE.** 2019 covers 5.933% of the study mask and no Karvir cells. The 2021 scene is 22 July, before documented 25 July response operations. Visual inspection finds plausible river-adjacent change without independent pixel-level validation. A temporal holdout would largely evaluate coverage/timing differences. The approved index fallback avoids claiming validated ML. PR-AUC and training date remain SQL null.

## Implemented formula

`score = 0.25 E + 0.30 R + 0.10 S + 0.15 H + 0.20 P`.

Exact configuration: `backend/app/ml/susceptibility.json`, also stored in `model_metadata.notes`. All terms are in [0,1]; `clip` limits to that interval.

| Term | Normalization | Prototype weight rationale |
|---|---|---|
| E, low elevation | `1 − clip((metres − 539.265625)/(759.1750122070315 − 539.265625))` | 0.25: physical terrain factor; bounds are real grid 5th/95th percentiles |
| R, river proximity | `exp(−distance_metres/1500)` | 0.30: largest contribution for this river-overflow setting; smooth decay |
| S, flat terrain | `1 − clip(slope_degrees/10)` | 0.10: limited weight because terrain factors overlap |
| H, historical change | mean event flood fraction where cell coverage ≥80% | 0.15: limited influence for temporally weak SAR proxies |
| P, rainfall | mean of `clip(24h/53.34)` and `clip(72h/140.52)` | 0.20: scenario influence without overriding terrain |

[Magnini et al., 2022](https://nhess.copernicus.org/articles/22/1469/2022/) supports combining geomorphic descriptors while examining their limitations. [The 2024 Ebro multi-hazard study](https://nhess.copernicus.org/articles/24/3703/2024/) demonstrates transparent indicator weighting. These sources motivate factor families and weighting, **not these numerical weights for Kolhapur**. The allocation is a reasoned prototype choice, not an AHP expert elicitation or fitted coefficients. Decay scales and bands also require future calibration.

Population and accessibility do not enter susceptibility. Unknown history uses H=0.5 (1,515 cells), explicitly flagged; it is never treated as dry. This can raise a cell relative to observed zero; changing H from 0 to 1 changes score by 0.15. Missing/nonfinite required elevation, slope or river distance fails loudly. Missing population remains null.

Categories: Low [0,.25), Medium [.25,.50), High [.50,.75), Critical [.75,1]. These are communication bands, not probabilities or official warnings. Village scores use exact grid-intersection areas. Uniform reanalysis presets shift levels and categories but do not imply local forecasts or necessarily reorder villages.

## M2 verification

14 risk tests passed. Repeated scoring matched for all 38,083 cells and three scenarios. `docs/evidence/m2-scoring.json` records categories, bounds and deterministic hashes. 114,249 grid/scenario rows persisted. Normal spans 0.01899–0.74013; Extreme 0.20244–0.92359. These are output checks, not accuracy metrics.

## Implemented priority normalization (M5)

Risk is the existing [0,1] index. Population is `log1p(p)/log1p(max_known_study_population)`; the log transform limits domination by large settlements but preserves order. The study-wide denominator stays fixed across scenarios and team counts. Unknown p uses the known study median solely inside ranking, with the reported estimate still null and the rule returned explicitly. If all are unknown, use 0.5; if all known values are zero, use zero. Default weights 0.65/0.35 are read from `priority_weights_config`, never fit claims. Ties use ascending village ID. Top N is capped at the number of villages. Accessibility and historical evidence cannot add independent terms.

## Arithmetic example (illustrative inputs, not an observed village)

For a cell with elevation 550 m, slope 2°, river distance 200 m and historical fraction 0.2, under Normal rainfall (3.7/13.5 mm), the normalized terms are E=0.95118728, R=0.87517332, S=0.8, H=0.2, P=0.08271903. Weighted contributions are 0.23779682 + 0.26255200 + 0.08 + 0.03 + 0.01654381 = **0.62689262 (High)**. This worked example demonstrates the arithmetic using actual normalization bounds; it is not extra data or a validation result. For a village, multiply each intersecting cell score by its intersection area, sum, and divide by total intersection area before applying the category bands.
