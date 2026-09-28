# Methodology status

No model has been trained and no risk scores have been generated. Gate A is open; Gate B has not run.

The planned method follows PRD §§15–20: 250 m grid features, area-weighted village aggregation, historical Sentinel-1 flood evidence, and observed-source provenance. Rainfall is modeled reanalysis; WorldPop is modeled population.

The priority formula is exactly `w_risk × normalized risk + w_pop × normalized population exposure`, with initial configuration weights 0.65 and 0.35. These are transparent prototype choices, not scientifically fitted values. Accessibility will never be subtracted, and historical severity will not be added again outside the risk term.

Normalization, missing-data behavior, category thresholds and any index weights must be specified and tested when actual input distributions are available. They are not silently invented during foundation work.
