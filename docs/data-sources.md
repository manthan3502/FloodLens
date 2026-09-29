# Data sources and provenance

Gate A: GO WITH REDUCED SCOPE. M1 processed real inputs; Gate B chose the index fallback because SAR evidence cannot support defensible supervised validation. Earlier access failures and source alternatives remain recorded under `docs/evidence/gate-a-*.json` and M0's milestone record.

| Source | Exact product/access | Actual use and limits |
|---|---|---|
| DataMeet | [Maharashtra village files](https://github.com/datameet/indian_village_boundaries/tree/master/mh), `mh1.geojson` and `mh2.geojson` | 397 valid pieces in four tehsils; dissolve named Census-code pieces to 380 units; quarantine nine unnamed pieces. `Hatkalangale` spelling normalized. Mixed vintage, includes towns. ODbL attribution required. |
| IIT Bombay | [Census-linked Maharashtra GIS portal](https://www.cse.iitb.ac.in/~pocra/MahaCensus_shapefile_data1.2/MaharashtraCensus.html) | Candidate reference only. Available tehsil comparisons exceed 99% coverage; Hatkanangale omitted in reference archive. Partly derives from DataMeet, so not independent certification. |
| SRTM | GEE [`USGS/SRTMGL1_003`](https://developers.google.com/earth-engine/datasets/catalog/USGS_SRTMGL1_003) | 30 m elevation/slope; EPSG:32643 processing. SRTM public-domain source terrain is not current drainage/bathymetry. |
| Sentinel-1 | GEE [`COPERNICUS/S1_GRD`](https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_S1_GRD) | VV, descending orbit 136, before/during composites, linear-power filtering and Otsu change with slope/water screens. Copernicus terms. 2019 coverage 5.933%; 2021 single 22 July scene. Not official or peak flood extents. |
| WorldPop | GEE [`WorldPop/GP/100m/pop_age_sex_cons_unadj`](https://developers.google.com/earth-engine/datasets/catalog/WorldPop_GP_100m_pop_age_sex_cons_unadj), India 2020, `population` band | Catalog describes constrained, UN-adjusted estimates. Native pixel counts preserved; no count-multiplying resampling. CC BY 4.0. Nine village totals unknown. |
| OSM | [Map API](https://api.openstreetmap.org/api/0.6/map), fallback after Overpass failures | 57 bounded parent extracts, with dense tiles subdivided at 50,000-node limit; 95 river/stream ways and 1,897 primary/secondary/tertiary road ways, deduplicated by OSM ID. © OpenStreetMap contributors, ODbL. Rural completeness varies. |
| Open-Meteo | [Historical Archive API](https://open-meteo.com/en/docs/historical-weather-api), `archive-api.open-meteo.com/v1/archive` | Reanalysis point samples for four tehsils, 2019/2021 event windows plus June–September 2015–2024 climatology. Attribution/provider terms apply. Modeled coarse rainfall, not gauges or forecasts. |

## Processed outputs

51 GeoTIFF downloads passed SHA-256 verification (`m1-raster-downloads.json`). Source scene IDs/dates are in `m1-sentinel-2019-sources.json` and `m1-sentinel-2021-sources.json`. Raw/intermediate files remain ignored. Native WorldPop pixel ownership is assigned once in village overlaps by stable ID; observed village and grid sums conserve at 2,470,371.0796. Zero conservation error is a processing check, not confirmation of population accuracy.

The 250 m grid has 38,083 cells and 47,843 exact village intersections. Distances/areas are metres in EPSG:32643; web GeoJSON is EPSG:4326. All named source polygons passed validation. Nine unnamed pieces remain outside displayed coverage; no names were invented and no project-wide grid-cluster fallback was needed.

Presets use pooled daily and rolling-three-day 50th/95th/99th percentiles from 4,880 monsoon daily values: Normal 3.70/13.50 mm, Heavy 29.70/78.51, Extreme 53.34/140.52 (24h/72h). They are comparative inputs, not return periods. Event-window context remains in `rainfall-tehsil-probes.json`.

## SAR plausibility and limitations

[PIB's 25 July 2021 response report](https://www.pib.gov.in/Pressreleaseshare.aspx?PRID=1738743&lang=2&reg=48) and [NDRF reporting](https://www.ndrf.gov.in/en/pressrelease/rescue-releif-work-ndrf-maharashtra) identify affected areas, not pixel-level ground truth. The visual check shows river-adjacent changes in Shirol. Missing 2019 coverage and 2021 acquisition timing prevent claiming complete historical extent. See `m1-sar-inspection.png`, `m1-feature-summary.json`, `m1-validation.json` and the methodology.

## Redistribution

`data/processed/seed.json.gz` is a compact source-derived database artifact. Retain source attribution and applicable ODbL/CC BY terms when redistributing data; the MIT software license does not override them. No OAuth tokens, database credentials or large raw imagery belong in the repository.
