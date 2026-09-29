# Two-minute demonstration

1. Open the dashboard and identify the four-tehsil study area and 380 source settlements.
2. Say: “This is a relative susceptibility index, not a flood forecast. Weak SAR coverage led us to use the approved transparent index instead of claiming ML accuracy.”
3. Switch Normal to Extreme. Explain rainfall's 20% index contribution and show the legend counts changing.
4. Click a village. Read elevation, slope, river distance, factor contributions and modeled population. Explain unknown values honestly.
5. Set five response teams, then three. Show blue outlines, list/detail synchronization and the 65/35 formula. Explain stable ties and the missing-population rule.
6. Open methodology and point out SAR dates, prototype weights and the non-operational limitation.

Screenshots: `docs/evidence/m4-dashboard.png`, `m4-mobile.png`, `m5-priorities.png`. Automated walkthroughs: `scripts/verify-workflow.cjs` and `verify-integration.cjs`. They use the real API. [Recorded local demo](evidence/floodlens-local-demo.webm). A live URL and production verification are pending cloud access.

## Interview description (matching the implemented fallback)

Built a FastAPI/PostGIS/React geospatial prototype for 380 Kolhapur settlements, processing real terrain, OSM, rainfall, population and satellite-change evidence into an explainable susceptibility index. Implemented and tested a configurable, deterministic response-priority engine with explicit missing-data behavior, spatial aggregation and an independently verified fresh-clone setup.

Do not claim the PRD's illustrative spatial/temporal ML accuracy bullet: supervised ML was not selected at Gate B.
