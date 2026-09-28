# Data-source audit — Gate A open

The final PRD defines candidates; the reports in `docs/evidence/` record actual requests, hashes and failures. Raw downloads are ignored. No production features have been derived.

| Source | Actual M0 result | Remaining work |
|---|---|---|
| [DataMeet Maharashtra](https://github.com/datameet/indian_village_boundaries/tree/master/mh) | Both files downloaded; 397 valid, nonempty, nonduplicate target polygons | Census-code reconciliation; Hatkanangale independent coverage reference |
| [IIT Bombay Census-linked maps](https://www.cse.iitb.ac.in/~pocra/MahaCensus_shapefile_data1.2/MaharashtraCensus.html) | Kolhapur village and district/tehsil archives downloaded | Coverage, geometry and reuse terms; candidate derives partly from DataMeet, so it is not independent validation |
| [Open-Meteo archive](https://open-meteo.com/en/docs/historical-weather-api) | 2019-08-01–15: 15 daily values, no nulls, 407.2 mm total; 2021-07-15–31: 17 daily values, no nulls, 267.8 mm total at requested 16.7°N, 74.25°E | Probe all tehsils and calibrate scenarios in M1; these totals describe different windows, not comparable event severity |
| [OpenTopography SRTM](https://portal.opentopography.org/API/globaldem) | Actual clip request returned HTTP 401 | Requires API key; GEE access pending. Approved Copernicus GLO-30 fallback returned 1,024 sample pixels (550.86–577.09 m) |
| [Earth Engine](https://developers.google.com/earth-engine/guides/auth) | Python initialization returned authorization-required error | User authentication and registered Cloud project; then actual SRTM and Sentinel-1 queries |
| [WorldPop constrained 2020 India](https://data.worldpop.org/GIS/Population/Global_2000_2020_Constrained/2020/BSGM/IND/) | Catalogue fetched; remote raster window failed because server did not support range access | Download/clip real raster; do not substitute GEE unconstrained population silently |
| [OSM Overpass](https://overpass-api.de/api/interpreter) / [OSM map API](https://api.openstreetmap.org/api/0.6/map) | Overpass GET 406 and POST timeouts. Direct map samples succeeded: Karvir 6 river/stream ways and 67 major-road ways; Panhala 0/11; Hatkanangale 0/10; Shirol 1/23 | Samples are small boxes, not full tehsils. Zero waterways in one sample does not establish source absence |

## Boundary findings

DataMeet spells Hatkanangale `Hatkalangale`. Counts: Karvir 136, Panhala 137, Hatkanangale 68, Shirol 56. All 397 shapes passed validity checks. Census 2001 identifiers are nonunique in three tehsils. The IITB reference archive omits Hatkanangale, so full coverage there is unverified. Coverage against available references exceeds 99% for the other three (`tehsil-coverage.json`). No fallback is justified by a spelling difference or missing reference alone.

After remote range reads failed, a full WorldPop download was attempted. The slow transfer was interrupted after about 57 MB; incomplete bytes are retained as `.partial` in ignored raw storage and never treated as a usable raster. A complete local download or authenticated approved source remains necessary.

## Source distinctions

DataMeet indicates ODbL. OSM attribution and ODbL obligations must be preserved. WorldPop's exact selected product and license must be documented with the processed artifact. IIT Bombay identifies tentative village boundaries, Census attributes and missing geometries; its download is not a certification of completeness.

The planned analysis uses metres in EPSG:32643. M0 probes use small samples or a provisional broad bounding box only; neither defines the final four-tehsil boundary.
