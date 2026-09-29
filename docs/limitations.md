# Current limitations

M1 now has real processed features and a verified PostGIS seed. SAR 2019 coverage is 5.933%; 2021's 22 July scene predates documented 25 July rescue operations. Sparse detected change is not an estimate of complete historical inundation. Nine villages have unknown WorldPop totals; other totals sum observed constrained pixels only. Nine unnamed source boundary pieces are omitted and preserved for review. The current frontend remains the M0 preview until M4. Older M0 access findings below are historical context.

- M0 passed with reduced scope: Docker/PostGIS and Earth Engine now work. 2019 event-window SAR coverage is absent at four sample points; unknown observations must never become dry labels. M1 will audit full masks before Gate B.
- The selected population input is constrained 2020 WorldPop from GEE (`pop_age_sex_cons_unadj`, population band), UN-adjusted per its catalog. Nine source polygons lack settlement names; Hatkanangale lacks an independent tehsil reference in the downloaded IITB archive.
- The current map is a study-area preview with no flood overlay, scores, population estimates or rankings.
- Dataset availability is being tested. A successful catalogue request does not establish raster usability or spatial coverage.
- No scientific validation, prediction accuracy or lives-saved claim is supported.

## Limitations to preserve in the finished product

SAR flood masks are remotely derived proxies for selected events, not official incident records. Reanalysis rainfall is not a gauge reading. Population exposure is modeled, not a census headcount. Village geometries may have gaps; fallback decisions must be recorded by tehsil. Priority weights are prototype choices. The application is not validated for operational evacuation decisions.
