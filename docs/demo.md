# Two-minute demonstration

1. Open the dashboard and identify the four-tehsil study area and 380 source settlements.
2. Say: “This is a relative susceptibility index, not a flood forecast. Weak SAR coverage led us to use the approved transparent index instead of claiming ML accuracy.”
3. Switch Normal to Extreme. Explain rainfall's 20% index contribution and show the legend counts changing.
4. Click a village. Read elevation, slope, river distance, factor contributions and modeled population. Explain unknown values honestly.
5. Set five response teams, then three. Show blue outlines, list/detail synchronization and the 65/35 formula. Explain stable ties and the missing-population rule.
6. Open methodology and point out SAR dates, prototype weights and the non-operational limitation.

[Open the live dashboard](https://floodlens-lilac.vercel.app). Production assets: [desktop](evidence/production-dashboard.png), [mobile](evidence/production-mobile.png), [methodology](evidence/production-methodology.png), and [recorded production walkthrough](evidence/floodlens-production-demo.webm). `scripts/verify-production.cjs` repeats the live checks. Allow extra time for a sleeping free API; use the recording as a backup. Screenshots and video use real API responses.

## Interview description (matching the implemented fallback)

Built a FastAPI/PostGIS/React geospatial prototype for 380 Kolhapur settlements, processing real terrain, OSM, rainfall, population and satellite-change evidence into an explainable susceptibility index. Implemented and tested a configurable, deterministic response-priority engine with explicit missing-data behavior, spatial aggregation and an independently verified fresh-clone setup.

Do not claim the PRD's illustrative spatial/temporal ML accuracy bullet: supervised ML was not selected at Gate B.
