# Current limitations

- M0 passed with reduced scope: Docker/PostGIS and Earth Engine now work. 2019 event-window SAR coverage is absent at four sample points; unknown observations must never become dry labels. M1 will audit full masks before Gate B.
- The selected population input is constrained 2020 WorldPop from GEE (`pop_age_sex_cons_unadj`, population band), UN-adjusted per its catalog. Nine source polygons lack settlement names; Hatkanangale lacks an independent tehsil reference in the downloaded IITB archive.
- The current map is a study-area preview with no flood overlay, scores, population estimates or rankings.
- Dataset availability is being tested. A successful catalogue request does not establish raster usability or spatial coverage.
- No scientific validation, prediction accuracy or lives-saved claim is supported.

## Limitations to preserve in the finished product

SAR flood masks are remotely derived proxies for selected events, not official incident records. Reanalysis rainfall is not a gauge reading. Population exposure is modeled, not a census headcount. Village geometries may have gaps; fallback decisions must be recorded by tehsil. Priority weights are prototype choices. The application is not validated for operational evacuation decisions.
