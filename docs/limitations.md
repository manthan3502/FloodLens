# Limitations

- This is an academic decision-support prototype. No official warning, safe route, flood depth, event probability, lives-saved claim or operational validation is supported.
- Historical SAR is a change proxy: 2019 covers 5.933% of the study area; 2021 uses 22 July imagery before documented 25 July response. Missing observations are never dry labels. No ML metrics exist.
- Index weights, river decay, slope cap and category bands are reasoned prototype assumptions. Absolute elevation is not height above the nearest drainage. A neutral historical value is used where coverage is inadequate.
- Rainfall presets are pooled reanalysis quantiles from four sample points, applied uniformly. They are not live gauges, forecasts or return periods. Uniform rainfall can change category/score without changing relative priority order.
- WorldPop constrained 2020 population is modeled and older than the processing date. Nine villages have no valid pixels and remain null. Other totals sum observed pixels; population is whole-village context, not a modeled count of people who will flood. Grid/village observed sums conserve exactly.
- DataMeet boundaries have mixed vintage. Nine unnamed pieces are omitted and quarantined; Hatkanangale lacks an independent tehsil reference. Named multipart pieces were dissolved. The 380 units include municipal/town polygons, so this is a rural-focused study area rather than a rural-only census inventory. Larger towns can dominate population-aware rankings; no specialized urban flood model is implemented.
- OSM rural streams/roads may be incomplete. Straight-line mean distance is not road travel time, passability, bridge condition or an evacuation route.
- One team per ranked village is a deterministic greedy demonstration. Actual capacity, logistics and multiple resource types are outside scope. Accessibility never penalizes the score.
- Offline feature snapshots are cached per API worker; restart after data refresh. Map simplification trades small boundary detail for responsiveness. Source-derived artifacts retain upstream licenses.
- Basemap tiles require internet access. The app explicitly reports failed data requests; a tile-provider outage can leave polygons without a basemap.
- Planned free deployment has cold starts and quotas. Public deployment and Gate D remain pending until cloud authentication and actual production verification succeed.
