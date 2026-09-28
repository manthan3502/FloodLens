# FloodLens — Final Implementation-Ready PRD (Codex Autonomous Build Version)
## Geospatial Flood Risk & Emergency Response Prioritization for Rural Kolhapur, Maharashtra

*This document is the single source of truth for an autonomous, milestone-by-milestone Codex build. Execution is completion-driven, not calendar-driven. Outer deadline: project should be working, tested, deployed, documented, and portfolio-ready before October 4–5, 2026 — earlier is better; nothing should be intentionally paced to fill time.*

---

## 1. Executive Summary

FloodLens is a geospatial decision-support prototype that estimates **relative flood susceptibility** across flood-prone tehsils of **Kolhapur district, Maharashtra**, using terrain, self-derived satellite flood evidence, rainfall, waterway proximity, and population exposure — then converts that susceptibility into a transparent, resource-constrained **emergency-response priority ranking**. Codex builds this milestone-by-milestone, running its own tests and gates, committing and pushing continuously, and proceeding automatically through each milestone the moment its acceptance criteria pass — stopping only for the specific conditions in §36.

---

## 2. Final Problem Statement

During monsoon season, several rural tehsils of Kolhapur district flood repeatedly (2005, 2019, 2021) due to Panchganga/Krishna river overflow, yet district disaster-response teams allocate inspection and relief resources without a systematic, data-driven view of which villages are relatively more exposed and where limited response capacity should go first. FloodLens builds that view from open/derivable geospatial evidence and turns it into an actionable, explainable priority list.

---

## 3. Why Rural Maharashtra

Maharashtra has the clearest, best-documented recurring rural flood pattern of any Indian state readily researchable with open data: three major flood years in the last two decades (2005, 2019, 2021) concentrated in a well-defined geography (Konkan coast + Krishna basin western Maharashtra), with English-language disaster reports and published remote-sensing studies of the exact region — a rare combination of real stakes and traceable evidence for a one-student project.

---

## 4. Maharashtra District Feasibility Analysis

| District | Flood Relevance | Data Situation | Verdict |
|---|---|---|---|
| **Kolhapur** | Recurring severe floods (2005, 2019, 2021); Panchganga river forms a documented "inverted-U" around Kolhapur city and floods surrounding rural tehsils (Karvir, Panhala, Hatkanangale, Shirol, Radhanagari, Bhudargad, Gadhinglaj, Ajra) | An existing published study already performed Sentinel-1 SAR flood mapping for exactly these Kolhapur tehsils; clear river geometry; moderate terrain (manageable SAR shadow/layover risk vs. steeper Konkan ghats) | **Selected** |
| **Sangli** | Equally severe, adjoining Kolhapur, Krishna river overflow, 2019/2021 evacuations among the largest in the state | Very similar data profile; less directly-precedented remote-sensing literature found | **Backup** |
| **Ratnagiri (Chiplun)** | Very severe (2021 Chiplun flood) | Steep Western Ghats/Konkan terrain — higher SAR shadow/layover risk, flashier localized flooding | Rejected for MVP |
| **Raigad (Mahad)** | Very severe, landslide-dominated as much as flood-dominated | Mixed hazard signal complicates a clean flood-susceptibility label | Rejected — different hazard type |
| **Satara** | Upstream of Koyna dam releases that amplify Kolhapur/Sangli flooding | Weaker direct village-level flood evidence found | Rejected for MVP |

---

## 5. Selected MVP Geography

**Primary MVP District:** Kolhapur. **Study-area tehsils:** Karvir, Panhala, Hatkanangale, Shirol — the tehsils along the Panchganga/Krishna confluence belt with the strongest historical inundation record and the tightest, most manageable geography. Radhanagari, Bhudargad, Gadhinglaj, Ajra are Phase-2 expansion, not MVP.

**Backup MVP District:** Sangli (Miraj, Palus, Walwa tehsils) if Gate A returns NO-GO for Kolhapur.

---

## 6. Target Users

Primary: a district/tehsil-level disaster-management officer or NGO relief coordinator deciding where to send limited inspection/response teams before or during a flood event. Secondary: panchayat officials and researchers wanting a comparative view of village flood exposure.

---

## 7. Product Goals

1. Show, per village/zone, a defensible relative flood-susceptibility category (Low/Medium/High/Critical).
2. Let a user change a rainfall scenario and see susceptibility update.
3. Let a user set "available response teams = N" and get a ranked, explainable priority list.
4. Make every number traceable to its source and methodology.
5. Ship a deployed, tested, documented, portfolio-ready system as early as possible, no later than Oct 4–5.

---

## 8. Explicit Non-Goals

All Maharashtra districts/state-wide coverage; all Indian states; live IoT sensors; SMS/WhatsApp alerts; mobile app; complex auth/roles; citizen reporting; Kafka/Redis/Airflow/Kubernetes/microservices; LLM chatbot or generative-AI assistant; real municipal system integration; drone/hardware data; automatic evacuation routing; multi-resource-type optimization; real-time streaming.

---

## 9. User Journey

1. Officer opens FloodLens → sees Kolhapur study-area map with villages colored by baseline susceptibility.
2. Selects a rainfall scenario (Normal / Heavy / Extreme) → map recolors.
3. Clicks a village → detail drawer shows risk category, score, contributing factors, historical evidence, population exposure.
4. Sets "Available response teams" → priority panel produces a ranked Top-N list, synced with map highlighting.
5. Reduces/increases team count → list re-ranks live.
6. Reads the methodology/limitations panel to understand what the system is (and isn't) claiming.

---

## 10. Core MVP Features

Map of study-area villages/zones with susceptibility categories · historical-flood evidence layer (self-derived) · rivers/waterways layer · rainfall-scenario control (presets) · village/zone detail panel with plain-language explanation · population-exposure display · response-team-count control · Top-N priority engine synced to map · backend REST/GeoJSON API · PostGIS spatial database · offline data-processing pipeline · documented risk methodology · automated tests · deployment · professional documentation.

---

## 11. Killer Feature — Emergency Response Prioritization

Given `available_teams = N`, FloodLens returns a ranked list such as:

> **Priority 1 — Village X** · Risk: Critical · Estimated population in priority zone: ~[value] · Main factors: low elevation, close to Panchganga river, high historical inundation, extreme rainfall scenario · Accessibility (context only): Moderate · Distance to major road: X km · Recommended action: immediate assessment.

Changing N from 5 → 3 recomputes the list deterministically using the formula in §20. Accessibility is shown as **operational context**, not folded into the score (see §20 for the correction from the earlier draft).

---

## 12. Exact Screens / UI

**Screen 1 — Main Dashboard (the only screen that matters for the demo):** header/title bar → rainfall-scenario preset selector + response-team-count input → large Leaflet map (villages as colored polygons, rivers as blue lines, historical-flood overlay togglable) → right-side priority panel (ranked list, synced highlighting) → legend + "last processed" + methodology link footer.

**Screen 2 — Village/Zone Detail Drawer:** village name → risk category + numeric score → list of contributing factors with raw values → accessibility context (separate, not part of score) → one-paragraph plain-language explanation → close button.

**Screen 3 (only if time remains) — Methodology/About page.** No login screen, no multi-page navigation.

---

## 13. Dataset Feasibility Report

- **Historical flood evidence:** NRSC/Bhuvan's official Flood Hazard Atlas is WMS-only with no simple bulk-download endpoint, making it a poor primary dependency for an autonomous build. FloodLens instead **derives its own historical flood-extent evidence** using **Sentinel-1 SAR + Otsu-threshold change detection in Google Earth Engine** — a well-established, peer-reviewed, UN-SPIDER-documented technique already applied to Kolhapur's tehsils in published research. NRSC/Bhuvan layers are an optional cross-check only.
- **DEM:** SRTM 30m — globally available, easy to fetch programmatically — low risk.
- **Village boundaries:** Quality is **unverified until Gate A actually checks it during implementation** — it must not be assumed unusable in advance. Candidate sources are the DataMeet "Indian Village Boundaries" project and Census-linked village shapefiles (via academic GIS portals). **If Gate A finds usable Kolhapur polygons, they are used as the primary spatial-aggregation unit.** If geometry quality or coverage is genuinely poor for some or all study tehsils, the grid-cluster fallback in §15 applies — documented per-tehsil, not project-wide.
- **Rainfall:** Open-Meteo's Historical Weather Archive (ERA5/ERA5-Land reanalysis, free, no key, daily precipitation back to 1940) — low risk, used to calibrate scenario presets against real 2019/2021 event totals.
- **Population:** WorldPop's 100m constrained population raster for India (free, CC-BY) — low risk, standard for exposure estimation.
- **Rivers/roads:** OpenStreetMap via the Overpass API — reliable and low-risk for this region.

---

## 14. Final Dataset Table

| Dataset | Provider | Source | Coverage | Time Coverage | Resolution | Format | License | Used For | Preprocessing | Mandatory? | Reliability Concern | Fallback |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Sentinel-1 GRD (SAR) | ESA Copernicus | Google Earth Engine `COPERNICUS/S1_GRD` | Global | 2014–present | 10m | Raster (via GEE) | Free/open | Deriving self-labeled historical flood-extent masks (2019, 2021 events) | Speckle filtering, VV band selection, pre/during-flood composite, Otsu threshold, slope/DEM mask | **Mandatory** | Shadow/layover on steep slopes → false positives; mitigated via slope masking | Manually digitized flood extent from published news/photo evidence |
| SRTM DEM | USGS/NASA | OpenTopography or GEE `USGS/SRTMGL1_003` | Global | 2000 (static) | 30m | GeoTIFF | Public domain | Elevation, slope features | Reproject, clip, derive slope | **Mandatory** | Vertical error ~±16m — acceptable for relative risk | Copernicus GLO-30 DEM |
| OSM waterways | OpenStreetMap contributors | Overpass API | Global | Continuously updated | Vector | GeoJSON | ODbL | Distance-to-river feature; map layer | Filter `waterway=river/stream`, clip | **Mandatory** | Rural stream completeness varies | HydroRIVERS (WWF) |
| OSM roads | OpenStreetMap contributors | Overpass API | Global | Continuously updated | Vector | GeoJSON | ODbL | Accessibility context (distance to nearest road) | Filter primary/secondary/tertiary tags | **Mandatory** | Rural road tagging density varies | Approximate via distance-to-town-center |
| Open-Meteo Historical Archive | Open-Meteo (ERA5/ERA5-Land) | `archive-api.open-meteo.com/v1/archive` | Global | 1940–present | ~9–25km grid | JSON/CSV via REST | Free, no key | Historical rainfall context; scenario-preset calibration | Aggregate to daily/event totals, interpolate | **Mandatory** | Reanalysis is modeled, coarser than a gauge | IMD gridded rainfall if accessible |
| WorldPop India 100m population | WorldPop | `hub.worldpop.org` / GEE `WorldPop/GP/100m/pop` | India | ~2020 | 100m | GeoTIFF | CC-BY 4.0 | Population-exposure estimates | Clip, zonal-sum into grid/villages | **Mandatory** | Modeled estimate — framed as "estimated exposure," never a census count | Census 2011 town/village tables as sanity check |
| Village boundaries — DataMeet / Census-linked shapefile | Data{Meet} community / Census of India via academic GIS portals | GitHub `datameet/indian_village_boundaries` (or forks); university geo-portals | Partial, verify per-tehsil at Gate A | Mixed vintage | Vector | GeoJSON/Shapefile | ODbL / portal-dependent | Village polygons for aggregation and labeling — **primary spatial unit if usable** | Clip, validate geometry, join to Census codes | **Mandatory — verified live at Gate A, not assumed** | Coverage/quality unverified until checked; historically inconsistent in parts of India | Grid-cluster fallback (§15), applied per-tehsil only where actually needed |
| NRSC/Bhuvan flood hazard & NDEM flood-inundation layers | ISRO/NRSC | `bhuvan.nrsc.gov.in`, `ndem.nrsc.gov.in` (WMS); community GitHub mirror | India, event-specific | Varies | Vector/raster | WMS / GeoTIFF | Government/public | Optional cross-validation of self-derived SAR flood extent | Requires WMS-extraction workaround | Optional | Awkward programmatic access | Skip — self-derived SAR labels remain primary |
| OSM critical infrastructure (hospitals, schools) | OpenStreetMap contributors | Overpass API | Global | Continuously updated | Vector (points) | GeoJSON | ODbL | Optional context layer | Filter `amenity=hospital/school` | Optional | Sparse rural tagging | Omit from MVP |

---

## 15. Spatial Analysis Unit Decision

**Compared:** A — village-level only (best explainability, weakest ML validity/robust to boundary gaps); B — regular grid cells only (best ML validity, poor human communication); C — hybrid (grid for computation, village/zone for presentation).

**Decision: Option C.** A ~250m grid is used for feature engineering, SAR-label extraction, and (if Gate B passes) model training/validation. Grid-cell risk scores are area-weighted-averaged into **real village polygons where Gate A confirms usable coverage**, and into named grid-clusters (keyed to the nearest OSM settlement point) only for tehsils where village-polygon coverage is genuinely insufficient — a per-tehsil decision made from evidence gathered during Gate A, not a project-wide assumption.

---

## 16. Data Pipeline

```
Raw sources (SRTM, OSM, WorldPop, Open-Meteo, Sentinel-1)
   → download/fetch scripts (data_pipeline/ingestion/)
   → reprojection to EPSG:32643 (UTM 43N)
   → clip to study-area bounding box (Karvir/Panhala/Hatkanangale/Shirol)
   → build the 250m analysis grid (GeoPandas + Shapely)
   → per-grid-cell feature extraction (elevation, slope, distance-to-river, distance-to-road,
      rainfall aggregates, population sum, historical-flood-evidence flag from SAR)
   → village/zone aggregation (real polygons where Gate A confirms them; grid-clusters otherwise)
   → data-quality validation suite (§28) — pipeline fails loudly on violations
   → write final feature table + geometries to PostGIS
```
Runs offline, once (plus scenario re-runs) — the web app only reads precomputed PostGIS tables and applies the (cheap) rainfall-scenario adjustment and priority ranking at request time.

---

## 17. Feature Engineering

Per grid cell: elevation, slope, distance to nearest river/stream, distance to nearest road (accessibility context), historical-flood-evidence flag/count (from SAR masks for 2019 and 2021), rainfall features per scenario preset (24h/72h totals calibrated against 2019/2021 event totals), estimated population (WorldPop zonal sum). Per village/zone: area-weighted mean risk score, total estimated population, dominant contributing factors, accessibility summary.

---

## 18. ML / Risk Methodology

Decided by evidence at **Gate B**, not assumed:

- **If SAR labels (2019/2021) are usable** (plausible, slope-filtered positive-class count; visual sanity-check passes at known-flooded locations) → **supervised ML**: binary classification per grid cell ("was this cell part of an observed flood-extent mask") producing a susceptibility probability. **Baseline:** Logistic Regression. **Comparison:** Random Forest (XGBoost only if it meaningfully outperforms Random Forest on the spatially-validated metric — never chosen by default). **Evaluation:** Precision-Recall AUC + calibration check (flood cells are a minority class).
- **If SAR labels are too sparse/noisy** → documented **weighted multi-factor susceptibility index** (normalized elevation, river proximity, historical evidence, rainfall intensity, drainage-adjacent slope), weights justified from published flood-susceptibility-index literature, labeled clearly as "susceptibility scoring," never "trained flood-prediction AI."

The architecture (feature table → risk score → bucket) is identical either way.

---

## 19. Validation & Spatial Leakage Strategy

A random cell-level train/test split would leak information (adjacent 250m cells are spatially autocorrelated). FloodLens uses: **spatial block cross-validation** (contiguous geographic blocks held out together, e.g. by tehsil) and **temporal holdout** (train on the 2019-event SAR mask, evaluate on the 2021-event mask, and vice versa). Both results are reported side-by-side with an honest discussion of failure modes.

---

## 20. Priority Engine Methodology *(revised — replaces the earlier accessibility-penalty formula)*

Deliberately **not ML** — a transparent, deterministic, configurable scoring function:

```
priority_score(zone) = w_risk * normalized_flood_risk(zone)
                      + w_pop  * normalized_population_exposure(zone)
```
**Default starting weights: `w_risk = 0.65`, `w_pop = 0.35`.** These are explicitly documented in `docs/methodology.md` as **prototype decision-support weights chosen for transparency, not scientifically validated or empirically fit values**, and are exposed as a configuration, not hard-coded magic numbers.

Two corrections from the earlier draft, both important:
1. **Accessibility is not subtracted from the score.** It is displayed as operational context only (`Accessibility: Easy/Moderate/Difficult`, `Distance to major road: X km`) next to each priority-list entry, so a human decision-maker sees it without the system silently down-ranking hard-to-reach — often the most vulnerable — zones.
2. **Historical flood severity is not double-counted.** It already contributes to `normalized_flood_risk` (via the SAR-derived labels or the susceptibility index in §18) and is therefore not added a second time as an independent term.

Given `available_teams = N`, zones are sorted by `priority_score` descending and the **top N are returned** — a documented, deterministic greedy ranking, explainable and trivially testable.

---

## 21. System Architecture

```
User (District Officer)
   → React + Leaflet Dashboard
      → FastAPI Backend (REST + GeoJSON API)
         → PostGIS (villages/zones, grid features, risk_results, priority config, model_metadata)
         → Risk Scoring Service (reads precomputed features; applies rainfall-scenario adjustment)
         → Priority Engine (deterministic scoring function from §20)
      → Responses as GeoJSON (map) + JSON (priority list, detail panel)
   → Map recolors + priority panel updates
```
Offline side: **Data Pipeline** (§16) → PostGIS, run once per data refresh.

---

## 22. Database Schema

- **districts** (`id` PK, `name`, `geom` MultiPolygon)
- **villages** (`id` PK, `district_id` FK, `name`, `tehsil`, `geom` MultiPolygon, `source` [village_polygon | grid_cluster], `population_estimate`) — GiST index on `geom`
- **grid_cells** (`id` PK, `village_id` FK nullable, `geom` Polygon, `elevation`, `slope`, `dist_to_river`, `dist_to_road`, `population`) — GiST index on `geom`
- **historical_flood_events** (`id` PK, `event_name`, `event_date`, `source_method`, `mask_reference`)
- **grid_flood_evidence** (`grid_cell_id` FK, `event_id` FK, `flooded` boolean) — the ML label table
- **rainfall_scenarios** (`id` PK, `name` [Normal/Heavy/Extreme], `rainfall_24h_mm`, `rainfall_72h_mm`)
- **risk_results** (`grid_cell_id` FK, `scenario_id` FK, `risk_score`, `risk_category`, `computed_at`)
- **priority_weights_config** (`id` PK, `w_risk` default 0.65, `w_pop` default 0.35, `updated_at`) — makes the §20 weights explicitly a stored, documented config, not a code constant
- **model_metadata** (`id` PK, `model_type`, `trained_at`, `pr_auc_spatial_cv`, `pr_auc_temporal_holdout`, `feature_list`, `notes`)

`priority_results` is intentionally not persisted — computed on demand to avoid a stale-cache bug class.

**Why PostGIS:** spatial joins (`ST_Intersects`, `ST_DWithin`), native geometry types, and direct GeoJSON export (`ST_AsGeoJSON`) that would otherwise be reimplemented slowly in application code.

---

## 23. API Specification

| Method | Path | Purpose | Request | Response | Notes |
|---|---|---|---|---|---|
| GET | `/health` | Liveness check | — | `{"status": "ok"}` | Deployment monitoring |
| GET | `/villages` | List study-area villages/zones with baseline risk | Query: `scenario_id` (optional, default Normal) | GeoJSON `FeatureCollection` | Primary map data endpoint |
| GET | `/villages/{id}` | Village/zone detail | Path: `id` | JSON: risk, contributing factors, historical evidence, population, accessibility context | Powers detail drawer |
| POST | `/scenarios/evaluate` | Recompute risk for a rainfall scenario | `{"scenario_id": "normal\|heavy\|extreme"}` (preset-driven for MVP) | Same shape as `/villages` | Custom numeric rainfall input is **not** part of MVP scope (see §38) — presets only unless Gate C passes with time remaining |
| POST | `/priorities/calculate` | Emergency-response priority ranking | `{"scenario_id": ..., "available_teams": N}` | JSON list, ranked, each with village id/name, risk, population, top factors, accessibility context, rank | `available_teams > village count` returns all, ranked, not an error |
| GET | `/model/metadata` | Model/methodology transparency | — | JSON: model type used, validation metrics if ML, feature list, priority weights in use, last-processed date | Powers the "why should I trust this" footer link |
| GET | `/rivers` | River/waterway layer | — | GeoJSON | Static map layer |

All map-facing endpoints return GeoJSON; validation errors return HTTP 422 with a field-level message; not-found lookups return HTTP 404; missing population returns `population_estimate: null` explicitly.

---

## 24. Frontend Architecture

`src/components/Map/` · `src/components/Controls/` (rainfall preset selector, team-count input) · `src/components/PriorityPanel/` · `src/components/VillageDetail/` (includes accessibility context, separate from risk/priority) · `src/components/Legend/` · `src/api/` · `src/state/` (React state/context — no external state library needed at this scale).

---

## 25. Backend Architecture

`app/api/` (routers: villages, scenarios, priorities, model) · `app/services/risk_service.py` · `app/services/priority_service.py` (implements §20's exact two-term formula, reads weights from `priority_weights_config`) · `app/models/` (SQLAlchemy/GeoAlchemy2) · `app/core/` (config, CORS, DB session) · `app/ml/` (ML inference wrapper, or susceptibility-index calculation — same interface either way, decided by Gate B).

---

## 26. Error / Loading / Empty States

Map: skeleton/spinner while loading; explicit "data unavailable" state on API failure (never a blank map); explicit "no historical evidence for this zone" rather than hiding the toggle. Priority panel: "Set available teams to see a priority ranking" before first input; friendly message on invalid input. Detail drawer: per-field "data unavailable" rather than failing the whole drawer if one feature is missing.

---

## 27. Testing Strategy

**Data pipeline:** missing/null handling · invalid/out-of-bounds coordinates rejected · duplicate geometry deduplicated · CRS round-trip verified · raster-to-grid extraction spot-checked · population zonal-sum sanity-checked.

**Risk/susceptibility model:** deterministic output for fixed inputs · missing-feature handling defined and tested · output within correct bounds · (if ML) reproducible from a fixed seed · naive-random-split vs. spatial-block score gap logged, not hidden.

**Priority engine (most heavily tested, matching its role as the killer feature):** `available_teams = 0` → empty list · `= 1` → exactly the single highest `priority_score` zone · normal N → exactly N zones, correctly sorted, deterministic on repeat calls · `N > total zones` → all zones ranked, no crash · tied `priority_score` → documented, tested tie-break (stable sort by village id) · missing population → does not silently rank as "safest," explicit rule tested · verify accessibility is **never** subtracted from `priority_score` (a regression test against the §20 correction) · verify historical severity is not double-counted (a regression test checking the formula only has two terms).

**Backend:** happy paths for every §23 endpoint · malformed-request 422s · not-found 404s · GeoJSON spec validation · DB-integration test against a test PostGIS instance.

**Frontend:** map renders with mocked data · scenario-preset control triggers re-fetch · team-count control triggers re-fetch and panel update · loading/error/empty states render correctly.

**End-to-end:** rainfall preset change → backend recomputes risk → priority engine reruns → map recolors → ranked list updates — scripted against a real test backend.

---

## 28. Data Quality Testing

Coordinate bounds checked against the Kolhapur study-area bounding box · null-value thresholds per feature column · duplicate village/zone detection · invalid geometry detection (`is_valid`) · unexpected CRS detection · impossible elevation values flagged · negative population rejected · rainfall preset values outside a defensible physical range rejected. Runs as part of the pipeline (`data_pipeline/validation.py`), not a manual checklist.

---

## 29. Deployment Architecture

**Frontend:** Vercel (free tier). **Backend:** Render or Railway (free/hobby tier), FastAPI in a container. **Database:** Supabase Postgres with PostGIS enabled (free tier). Large geospatial processing (SRTM clipping, SAR extraction, grid feature engineering) happens **offline before deployment** — only small precomputed PostGIS tables are deployed, sidestepping free-tier memory/CPU limits. CORS locked to the deployed frontend origin (+ localhost for dev). Migrations via a single versioned Alembic script run at deploy time.

---

## 30. Security Considerations

Read-mostly, public-data, no-PII prototype: input validation on every endpoint; no user authentication for MVP (explicit non-goal); credentials/tokens in environment variables only (`.env.example` provided, `.env` gitignored); CORS locked to known origins; rate-limiting deferred as documented future scope.

---

## 31. Logging & Error Handling

Backend: structured logging (path, status, latency) via FastAPI middleware. Pipeline scripts log each stage's row counts and validation-check results to a run log. All API errors return a consistent JSON error shape.

---

## 32. Repository Structure

```
floodlens/
├── README.md
├── docker-compose.yml
├── .env.example
├── LICENSE
├── backend/
│   ├── app/{api,models,services,ml,core}/
│   ├── tests/
│   └── requirements.txt
├── frontend/
│   ├── src/{components,api,state}/
│   └── package.json
├── data_pipeline/
│   ├── ingestion/         # SRTM, OSM, WorldPop, Open-Meteo, Sentinel-1/GEE scripts
│   ├── processing/        # grid construction, feature engineering, aggregation
│   ├── validation.py
│   └── notebooks/
├── docs/
│   ├── architecture.md
│   ├── data-sources.md
│   ├── methodology.md     # risk methodology + priority-engine formula, in full
│   ├── model-card.md      # if Gate B → ML
│   ├── limitations.md
│   ├── learning-notes.md  # cumulative, plain-language, vibe-coder-facing
│   └── milestones/
│       ├── M0-foundation.md
│       ├── M1-data-pipeline.md
│       ├── M2-risk-methodology.md
│       ├── M3-backend.md
│       ├── M4-frontend.md
│       ├── M5-priority-engine.md
│       ├── M6-integration.md
│       ├── M7-testing-hardening.md
│       └── M8-deployment.md
└── scripts/
    └── deploy/
```

---

## 33. Environment Variables

Backend: `DATABASE_URL`, `CORS_ALLOWED_ORIGINS`, `ENV`. Frontend: `VITE_API_BASE_URL`. Data pipeline (local/offline only): `GEE_SERVICE_ACCOUNT_KEY` if scripting Earth Engine programmatically, otherwise none. All documented in `.env.example` with placeholder values only.

---

## 34. Local Development Setup

`docker-compose up` brings up local PostGIS; `backend/` runs via `uvicorn app.main:app --reload`; `frontend/` runs via `npm run dev`; `data_pipeline/` scripts run manually/once, with a small already-processed feature artifact checked into the repo so a fresh clone can seed the database without re-running the full pipeline.

---

## 35. Git / GitHub Development Process *(revised — continuous, not one-time upload)*

Git is initialized in M0, not at the end. Development and version control happen together:

- Initialize Git and (where authentication is available) the remote GitHub repository during M0.
- Maintain `.gitignore` from the first commit; never commit secrets, `.env`, model artifacts over a reasonable size, or raw multi-GB rasters.
- Every milestone produces one or more **meaningful** commits tied to real completed work (see each milestone's Git Commit/Push Requirement in §47) — not one giant commit per milestone, and never fabricated/padding commits purely to show activity.
- After a milestone's acceptance criteria pass: commit → push (if authenticated) → verify `git status` is clean → proceed to the next milestone.
- **If GitHub authentication is unavailable:** continue implementation locally without stopping the build, and clearly flag in the milestone record (§47) that a manual `git push`/authentication step is pending — this is not a stop condition (§36) by itself.
- Example commit progression (illustrative, not mandatory exact wording): `M0: initialize FloodLens monorepo and local PostGIS environment`, `M0: add FastAPI health endpoint and React map foundation`, `M1: add terrain and waterway ingestion pipeline`, `M1: add Sentinel-1 flood evidence extraction`, `M2: add flood susceptibility methodology and validation`, `M3: implement PostGIS-backed FloodLens API`, `M4: build interactive flood-risk map dashboard`, `M5: add emergency response priority engine`, `M6: integrate scenario-to-priority workflow`, `M7: harden application and complete automated tests`, `M8: deploy FloodLens and finalize portfolio documentation`.

---

## 36. Autonomous Execution Model

**Default mode: completion-driven, not date-driven.** The instant a milestone's acceptance criteria and tests pass, Codex commits, pushes, records the milestone, updates learning notes, and **immediately begins the next milestone** — with no pause to ask "should I continue?" Successful completion is itself the permission to proceed. If a milestone finishes in an hour, the next one starts within the hour; nothing is deliberately stretched to fill calendar time (§49).

### Stop Conditions — the ONLY situations where Codex halts for a human
- **A. Authentication/Permission** — GitHub login, Google Earth Engine authorization, cloud deployment login, or any API permission requiring manual approval.
- **B. Gate failure with multiple materially different, reasonable alternatives** — e.g., a mandatory Kolhapur dataset fails and both "shrink to one tehsil" and "switch to Sangli" are realistic but change the project differently.
- **C. Destructive action** — anything that could delete or overwrite important remote data.
- **D. Paid service** — anything requiring payment or a cloud-plan upgrade.
- **E. Major scope change** — anything that would change the project's core purpose.

### Everything else is Codex's own responsibility
Dependency errors, lint failures, TypeScript/Python errors, failed unit tests, minor library incompatibilities, Docker configuration problems, API serialization bugs, frontend bugs — Codex diagnoses and fixes these itself and does not ask the human how to resolve them.

### Failure Policy Hierarchy
1. Diagnose the problem.
2. Fix it directly.
3. Re-run the relevant test.
4. If still failing, apply the milestone's documented fallback (§47's "Approved Fallback" field).
5. If still blocked, reduce optional complexity (§38's scope-cut order) before touching core scope.
6. Only if genuinely unavoidable — and it matches a Stop Condition above — request human intervention.

Codex does not spend hours stuck on one non-critical dependency; protecting overall project completion outranks perfecting any single component.

### Test-Driven Completion
A milestone is not "done" because Codex says "implementation complete." Completion requires: code exists → code runs → the milestone's required tests run and pass → any failures are fixed, not skipped → acceptance criteria are explicitly verified against real output → documentation is updated where required → a Git commit is made. Every milestone in §47 lists the exact commands to run to verify this.

---

## 37. Gate System

Each gate resolves to one of three outcomes: **GO**, **GO WITH REDUCED SCOPE**, or **NO-GO**.

### Gate A — Dataset Feasibility (during M0/M1)
Actually validate, in the running implementation (not just trust this PRD): Kolhapur/study-tehsil village-boundary availability and quality, SRTM/DEM access, OSM waterways, OSM roads, WorldPop, rainfall data, and Sentinel-1/Earth Engine access.
- **GO:** all mandatory datasets usable → continue automatically into M1/M2.
- **GO WITH REDUCED SCOPE:** a dataset needs its **already-approved-in-this-PRD** fallback (e.g., grid-cluster instead of village polygons for a specific tehsil, per §14/§15) → apply automatically, document it in the milestone record, and continue.
- **NO-GO / ambiguous:** the needed fallback is not already pre-approved in this PRD, or multiple materially different fallbacks are reasonable (e.g., shrink to one tehsil vs. switch to Sangli) → this is Stop Condition B — halt and ask.

### Gate B — ML Feasibility (during M2)
Attempt the supervised-ML path (§18) only if the Sentinel-1-derived flood evidence is genuinely usable.
- **GO:** labels are usable → proceed with supervised ML, run the full validation strategy (§19).
- **GO WITH REDUCED SCOPE:** labels are weak/noisy → **automatically** fall back to the documented weighted susceptibility index (§18) — this fallback is pre-approved in this PRD and does not require stopping. Document what was attempted, why it passed/failed, the evidence, and the resulting methodology, then continue.
- Do not spend excessive implementation time forcing ML for resume appeal once evidence says otherwise.

### Gate C — Functional MVP (after M5)
Before any visual polish or optional features: real data → risk calculation → backend → map → rainfall scenario → village/zone detail → priority ranking must work end-to-end. If it doesn't, fix the MVP — do not proceed to polish.

### Gate D — Portfolio Ready (after M8)
Production deployment works, tests pass, README is complete, documentation exists, screenshots/demo assets exist, repository is clean, GitHub reflects real development history.

---

## 38. Scope-Cutting Order

**Must NOT be cut under any circumstance** (these define what FloodLens *is*): real geospatial data; flood risk/susceptibility methodology; the interactive map; rainfall scenario presets; village/zone explanation panel; population exposure; the emergency-response priority engine; backend API; PostGIS database; automated testing; deployment; core documentation (README, methodology, data sources, limitations).

**May be cut automatically, in this order, if the overall deadline is genuinely threatened** (cut from the top down, stopping as soon as enough time is recovered):
1. Optional critical-infrastructure POI layer.
2. Extra chart types beyond the essential risk/priority views.
3. Custom numeric rainfall input (presets alone satisfy the MVP per §23).
4. Additional non-essential map controls/toggles.
5. Advanced styling/animation polish beyond a clean, functional UI.
6. Secondary pages (fold the Methodology/About page into a footer link instead of a separate screen).
7. Extra ML model comparisons beyond the required baseline + one comparison model (keep whichever trains first if forced to choose; document the untried one honestly).
8. Additional tehsils beyond the four selected in §5.
9. Temporal-holdout validation as a *second* validation view — cut only as an absolute last resort, since it is one of the strongest interview talking points; spatial-block validation alone still satisfies Gate B's core requirement if this must go.

Every cut is recorded in the relevant milestone record (§47) with the reason, never applied silently.

---

## 39. README Specification

Title + one-line pitch · hero screenshot/GIF · why this project exists · problem statement · live demo link + short video walkthrough · core features · architecture diagram · data sources (→ `docs/data-sources.md`) · geospatial methodology summary · risk methodology summary (ML or index, stated honestly per Gate B's actual outcome) · priority-engine methodology summary (the exact §20 formula and weights) · model evaluation / scoring rationale · responsible-use statement (§42) · known limitations (§41) · tech stack · local setup · running tests · deployment notes · future scope (§45) · license.

---

## 40. Documentation Requirements

`docs/methodology.md` must let a stranger reproduce the risk score and priority ranking by hand from raw feature values. `docs/data-sources.md` lists exact URLs/APIs used, matching §14. `docs/model-card.md` (if ML) reports both §19 validation results with an honest discussion of failure modes. `docs/limitations.md` states plainly what the system does not know. `docs/learning-notes.md` is the cumulative, plain-language explanation built up across milestones (§47's "What I Must Understand" field, consolidated). `docs/milestones/*.md` are the per-milestone audit records (§47).

---

## 41. Known Limitations

Self-derived SAR flood-extent labels are a proxy for two historical events, not a comprehensive or officially validated flood-incident record. Village-boundary data quality varies by tehsil and may fall back to grid-clusters in some areas (documented per-tehsil, per Gate A's actual findings). Rainfall inputs are reanalysis-based (modeled), not live gauge measurements. Population figures are modeled estimates (WorldPop), not census headcounts. The priority-engine weights (65/35) are transparent prototype defaults, not empirically validated. The system is a decision-support prototype for portfolio/academic purposes and is not validated for real operational evacuation decisions.

---

## 42. Responsible-Use Statement

FloodLens estimates *relative* flood susceptibility and response priority for a demonstration study area using publicly derivable evidence; it does not predict the exact location, timing, or severity of a specific future flood, and its outputs should never be the sole basis for a real evacuation or resource-deployment decision. It is presented as an academic/portfolio decision-support prototype, not an operational early-warning system.

---

## 43. Resume Description

**Project title:** FloodLens — Geospatial Flood-Risk & Emergency-Response Prioritization System.

**Two-line description:** A geospatial decision-support prototype that estimates relative flood susceptibility across flood-prone villages of Kolhapur, Maharashtra, using self-derived satellite flood evidence, terrain, rainfall, and population data, and generates a transparent, resource-constrained emergency-response priority ranking.

**Three technical bullets:**
- Derived historical flood-extent evidence from Sentinel-1 SAR imagery (Google Earth Engine, Otsu thresholding) for two independent flood events, and validated a risk model using spatial-block and temporal-holdout cross-validation to avoid spatial data leakage.
- Built a full-stack geospatial system (FastAPI, PostGIS, React/Leaflet) processing DEM, waterway, rainfall, and WorldPop population data into a queryable, GeoJSON-serving risk API.
- Designed and tested a deterministic, explainable resource-allocation engine that ranks flood-prone zones for emergency response under a configurable team-capacity constraint.

---

## 44. Interview Concepts I Must Understand

Why Kolhapur/these tehsils; where the flood labels actually came from and their limitations; what the model is and isn't predicting; why the validation strategy prevents spatial leakage; why PostGIS; what GeoJSON is; how raster and vector data are combined; why these specific risk factors; how population exposure is estimated and what it isn't; the exact priority-engine formula and why it's rule-based, not ML, and why accessibility/historical-severity are handled the way they are (§20); why this shouldn't be trusted for a real evacuation; the biggest limitations; how it would scale. Answers live in `docs/methodology.md`, `docs/data-sources.md`, the model card, and the cumulative `docs/learning-notes.md`.

---

## 45. Future Scope

**Phase 2:** extend to Radhanagari, Bhudargad, Gadhinglaj, Ajra tehsils. **Phase 3:** full Kolhapur district (or Kolhapur+Sangli together). **Phase 4:** an urban-flood module for Kolhapur city itself. **Phase 5:** other Krishna-basin districts / other states. **Phase 6:** live rainfall-forecast integration, and custom numeric rainfall input, instead of presets only. **Phase 7:** real river-gauge/CWC data integration. **Phase 8:** multi-resource-type allocation via proper constrained optimization. **Phase 9:** accessibility-aware routing to priority zones. **Phase 10:** engagement with an actual district disaster-management authority for feedback.

---

## 46. Milestone-Driven Critical Path *(replaces the earlier date-wise plan)*

```
M0 (Foundation)
   ↓  [Gate A runs inside M0/M1]
M1 (Data Pipeline)
   ↓
Gate B (ML feasibility decision)
   ↓
M2 (Risk / ML Methodology)
   ↓
M3 (Backend)
   ↓
M4 (Frontend + Map)
   ↓
M5 (Emergency Response Priority Engine)
   ↓
Gate C (Functional MVP check)
   ↓
M6 (Full Integration)
   ↓
M7 (Testing + Hardening)
   ↓
M8 (Deployment + Documentation + Portfolio Polish)
   ↓
Gate D (Portfolio Ready check)
   ↓
FLOODLENS COMPLETE
```

There are no calendar-day assignments. Each arrow means "immediately upon the previous milestone's acceptance criteria and tests passing, with no waiting." Limited, safe overlap is allowed — documentation may update continuously throughout, and frontend scaffolding begun in M0 may continue lightly in parallel with M1's data work — but Codex must not create chaotic parallel feature work across milestones that would make debugging difficult; the milestone order above is otherwise sequential.

---

## 47. Revised M0–M8 Detailed Milestone Specification

Every milestone below follows the same template: **Objective, Why It Matters, Inputs, Implementation Tasks, Expected Files/Modules, Acceptance Criteria, Exact Verification Commands, Tests, Gate/Decision Point, Approved Fallback, Scope That Must NOT Be Added Yet, Git Commit/Push Requirement, Milestone Record Requirement, What I Must Understand, Automatic Next Step.**

### M0 — Feasibility + Foundation

**Objective:** Confirm Kolhapur is buildable and stand up the skeleton everything else plugs into.
**Why It Matters:** Every later milestone depends on the repo, local environment, and Gate A's dataset findings being correct from day one.
**Inputs:** This PRD only.
**Implementation Tasks:** Run Gate A checks for the four target tehsils (attempt real fetches/clips of SRTM, OSM waterways/roads, WorldPop, Open-Meteo, Sentinel-1/GEE access, and both candidate village-boundary sources); scaffold the `floodlens/` repo (§32); set up `docker-compose.yml` with local PostGIS; scaffold FastAPI (`/health` only) and React+Vite (blank map centered on Kolhapur); configure linting/formatting and a basic test harness with one placeholder passing test each; initialize Git and the GitHub remote (§35).
**Expected Files/Modules:** `docker-compose.yml`, `backend/app/main.py`, `frontend/src/App.tsx`, `data_pipeline/` scaffolding, `docs/architecture.md` (first draft), `docs/milestones/M0-foundation.md`.
**Acceptance Criteria:** `docker-compose up` brings up Postgres+PostGIS locally; `GET /health` returns 200; frontend renders a blank Leaflet map over Kolhapur; Gate A resolved to GO or GO WITH REDUCED SCOPE with findings written down (or Stop Condition B triggered if NO-GO with ambiguous fallback).
**Exact Verification Commands:** `docker-compose up -d && curl localhost:<port>/health`; `cd backend && pytest`; `cd frontend && npm run build && npm test`.
**Tests:** One placeholder backend test, one placeholder frontend test, both green.
**Gate/Decision Point:** Gate A.
**Approved Fallback:** Per §14/§15/§37 — grid-cluster fallback per affected tehsil if village polygons are poor there; Sangli switch or single-tehsil shrink only if Stop Condition B is triggered and a human decides.
**Scope That Must NOT Be Added Yet:** Any real data ingestion beyond feasibility checks, any risk logic, any priority logic.
**Git Commit/Push Requirement:** e.g. `M0: initialize FloodLens monorepo and local PostGIS environment`, `M0: add FastAPI health endpoint and React map foundation` — commit and push (if authenticated) once acceptance criteria pass.
**Milestone Record Requirement:** `docs/milestones/M0-foundation.md` — status, Gate A findings per dataset, what was implemented, tests run/results, fallback used if any, commit hash(es), known limitations, next milestone.
**What I Must Understand:** What PostGIS adds over plain Postgres; what Docker Compose is doing; why a monorepo is reasonable here; what CORS is; why Gate A exists (to find a bad data situation on day one, not late).
**Automatic Next Step:** Acceptance criteria passed → commit → push → record milestone → **immediately begin M1.**

### M1 — Data Pipeline

**Objective:** Turn raw open data into a clean, validated feature table in PostGIS, including self-derived flood-evidence labels.
**Why It Matters:** Every downstream milestone (risk methodology, backend, map, priority engine) reads from this table — its correctness gates everything else.
**Inputs:** M0's confirmed Gate A findings and repo skeleton.
**Implementation Tasks:** Write ingestion scripts for SRTM (clip+reproject+slope), OSM rivers/roads (Overpass+clip), WorldPop (clip+zonal-prep), Open-Meteo (2019/2021 event windows + scenario-preset climatology); build the 250m analysis grid; run Sentinel-1 SAR extraction (GEE) for 2019 and 2021, apply Otsu thresholding + slope-masking, visually sanity-check against known-flooded locations; join village-boundary data per Gate A's findings (real polygons where usable, grid-clusters where not, per tehsil); write `data_pipeline/validation.py` implementing all §28 checks; load the final feature table + geometries into PostGIS.
**Expected Files/Modules:** `data_pipeline/ingestion/{srtm,osm,worldpop,rainfall,sentinel1}.py`, `data_pipeline/processing/{grid,features,aggregation}.py`, `data_pipeline/validation.py`, GEE extraction script/notebook, `docs/data-sources.md` (filled in for real), `docs/milestones/M1-data-pipeline.md`.
**Acceptance Criteria:** PostGIS contains populated `grid_cells`, `historical_flood_events`, `grid_flood_evidence`, `villages` tables for the study area; all §28 checks pass or documented exceptions are logged; SAR mask visually overlaps known-flooded areas.
**Exact Verification Commands:** `python data_pipeline/validation.py --stage all`; `psql $DATABASE_URL -c "SELECT count(*) FROM grid_cells;"` (non-zero, plausible count); `pytest data_pipeline/tests/`.
**Tests:** All data-pipeline tests from §27.
**Gate/Decision Point:** None new here (Gate A was M0; Gate B is M2), but this milestone's SAR-mask quality is the direct input to Gate B.
**Approved Fallback:** If SAR labels are unusable → this is exactly what Gate B (in M2) exists to catch, so M1 proceeds and hands the (possibly weak) evidence forward rather than stalling here; if village-boundary joins fail broadly for a tehsil → commit to the grid-cluster fallback for that tehsil per §15/§37.
**Scope That Must NOT Be Added Yet:** Any ML training, any API endpoints, any frontend beyond M0's blank map.
**Git Commit/Push Requirement:** e.g. `M1: add terrain and waterway ingestion pipeline`, `M1: add population/rainfall feature extraction`, `M1: add Sentinel-1 flood evidence extraction` — several meaningful commits, pushed as each real chunk of work completes.
**Milestone Record Requirement:** `docs/milestones/M1-data-pipeline.md`.
**What I Must Understand:** What Sentinel-1 SAR is and why radar (not optical) is used for flood mapping; what Otsu thresholding does; why slope-masking is needed; what a CRS/reprojection is; what zonal statistics means; why the village-boundary situation is a real, known Indian open-data issue, not a project-specific mistake.
**Automatic Next Step:** Acceptance criteria passed → commit → push → record milestone → **immediately begin M2.**

### M2 — Risk / ML Methodology

**Objective:** Execute Gate B's decision and produce a validated risk-scoring service.
**Why It Matters:** This is the project's core analytical claim and its most interview-scrutinized component.
**Inputs:** M1's populated, validated feature table and SAR-derived labels.
**Implementation Tasks:** Evaluate SAR label quality against Gate B's criteria; **if GO:** train Logistic Regression baseline and Random Forest comparison model, implement spatial-block CV and temporal holdout (§19), select the final model by PR-AUC on both schemes, serialize it, write `docs/model-card.md`; **if GO WITH REDUCED SCOPE:** implement the documented weighted-sum susceptibility index (§18) with justified weights, write the equivalent methodology documentation labeled as scoring, not prediction — automatically, without stopping.
**Expected Files/Modules:** `data_pipeline/notebooks/model_comparison.ipynb` (or susceptibility-index derivation notebook), `backend/app/ml/`, `docs/model-card.md` or the risk section of `docs/methodology.md`, `docs/milestones/M2-risk-methodology.md`.
**Acceptance Criteria:** A risk score can be computed for every grid cell from the feature table alone; validation results (ML) or weight justification (index) are written down; `model_metadata` populated.
**Exact Verification Commands:** `pytest backend/tests/test_risk_model.py`; a scripted check that running the scoring function twice on the same input produces identical output (determinism).
**Tests:** Risk/susceptibility-model tests from §27.
**Gate/Decision Point:** **Gate B.**
**Approved Fallback:** Susceptibility index (§18) — pre-approved, applied automatically per Gate B's GO-WITH-REDUCED-SCOPE path.
**Scope That Must NOT Be Added Yet:** API endpoints exposing this (M3); priority ranking (M5).
**Git Commit/Push Requirement:** e.g. `M2: add flood susceptibility methodology and validation`.
**Milestone Record Requirement:** `docs/milestones/M2-risk-methodology.md` — must explicitly state Gate B's outcome and evidence.
**What I Must Understand:** The difference between a baseline and comparison model; what PR-AUC measures and why; what spatial data leakage is; what a temporal holdout adds; if the susceptibility-index path was taken, why that was the right call and how to state it in an interview.
**Automatic Next Step:** Acceptance criteria passed → commit → push → record milestone → **immediately begin M3.**

### M3 — Backend

**Objective:** Expose the risk methodology and study-area data as a working API.
**Why It Matters:** The frontend and priority engine both depend entirely on this layer.
**Inputs:** M1's PostGIS data, M2's risk methodology.
**Implementation Tasks:** Implement the §22 schema with Alembic migrations; implement each §23 endpoint; implement `risk_service.py` wired to M2's model/index; add backend tests.
**Expected Files/Modules:** `backend/app/api/*.py`, `backend/app/services/risk_service.py`, `backend/app/models/*.py`, `backend/tests/*`, `docs/milestones/M3-backend.md`.
**Acceptance Criteria:** Every §23 endpoint returns correct, schema-valid responses against real data; error cases return correct status codes.
**Exact Verification Commands:** `pytest backend/tests/`; `cd backend && ruff check . && black --check .`; a smoke-test script hitting every endpoint with `httpx`/`curl` and asserting 200s on valid input.
**Tests:** Backend tests from §27.
**Gate/Decision Point:** None.
**Approved Fallback:** N/A.
**Scope That Must NOT Be Added Yet:** The priority engine's real logic — `/priorities/calculate` may be stubbed to return an empty list, marked `TODO(M5)`.
**Git Commit/Push Requirement:** e.g. `M3: implement PostGIS-backed FloodLens API`.
**Milestone Record Requirement:** `docs/milestones/M3-backend.md`.
**What I Must Understand:** What GeoJSON is structurally; what REST status codes communicate; what a DB migration is and why versioned; the request flow from HTTP call to PostGIS query and back.
**Automatic Next Step:** Acceptance criteria passed → commit → push → record milestone → **immediately begin M4.**

### M4 — Frontend + Map

**Objective:** Build the polished, demo-ready dashboard.
**Why It Matters:** This is what an interviewer sees in the first 10 seconds.
**Inputs:** M3's working API.
**Implementation Tasks:** Build the map (choropleth by risk category), rivers layer, rainfall-**preset** control wired to `/scenarios/evaluate`, village/zone detail drawer (including accessibility context, separate from risk/priority) wired to `/villages/{id}`, loading/error/empty states, responsive layout, frontend tests.
**Expected Files/Modules:** `frontend/src/components/**`, `frontend/src/api/**`, `frontend/tests/**`, `docs/milestones/M4-frontend.md`.
**Acceptance Criteria:** Dashboard communicates the product within ~10 seconds of opening; preset control visibly changes the map; detail drawer shows real data; all states manually verified.
**Exact Verification Commands:** `cd frontend && npm run build`; `npm test`; `npm run lint`.
**Tests:** Frontend tests from §27.
**Gate/Decision Point:** None.
**Approved Fallback:** If large feature counts (from grid-cluster fallback) hurt map performance, simplify geometry server-side (`ST_SimplifyPreserveTopology`) rather than fighting it client-side.
**Scope That Must NOT Be Added Yet:** The priority panel's real data (M5) — may render against a stubbed/empty response.
**Git Commit/Push Requirement:** e.g. `M4: build interactive flood-risk map dashboard`.
**Milestone Record Requirement:** `docs/milestones/M4-frontend.md`.
**What I Must Understand:** How Leaflet renders GeoJSON layers; what a choropleth map is; why geometry simplification matters; basic React state flow.
**Automatic Next Step:** Acceptance criteria passed → commit → push → record milestone → **immediately begin M5.**

### M5 — Emergency Response Priority Engine

**Objective:** Build and exhaustively test the killer feature, using the corrected §20 formula.
**Why It Matters:** This is the single feature most likely to make an interviewer say "tell me more."
**Inputs:** M2's risk scores, M3's backend, M4's frontend shell.
**Implementation Tasks:** Implement `priority_service.py` per §20's **exact two-term formula** (`0.65 * risk + 0.35 * population`, weights read from `priority_weights_config`, accessibility and historical severity handled exactly as corrected in §20); wire `/priorities/calculate`; wire the frontend priority panel, synced with map highlighting; write the extensive deterministic test suite from §27, including the two explicit regression tests called out there (accessibility never subtracted; historical severity never double-counted).
**Expected Files/Modules:** `backend/app/services/priority_service.py`, `backend/tests/test_priority_service.py`, `frontend/src/components/PriorityPanel/**`, `docs/milestones/M5-priority-engine.md`.
**Acceptance Criteria:** Changing `available_teams` live-updates a correctly ranked, correctly-sized list; every §27 edge case is a passing test; list and map stay visually synchronized.
**Exact Verification Commands:** `pytest backend/tests/test_priority_service.py -v`; a scripted check confirming identical output across repeated calls with the same input (determinism).
**Tests:** Full priority-engine test list from §27.
**Gate/Decision Point:** None (Gate C follows this milestone).
**Approved Fallback:** N/A — the formula itself is the (already-corrected) approved design.
**Scope That Must NOT Be Added Yet:** Multi-resource-type allocation, constrained optimization (future scope, §45).
**Git Commit/Push Requirement:** e.g. `M5: add emergency response priority engine`.
**Milestone Record Requirement:** `docs/milestones/M5-priority-engine.md`.
**What I Must Understand:** The exact formula, recitable from memory; why it's deterministic and rule-based, not ML; why accessibility is context, not a penalty; why historical severity isn't double-counted; what a tie-break rule is and why one is needed.
**Automatic Next Step:** Acceptance criteria passed → commit → push → record milestone → **run Gate C**, then **immediately begin M6** if Gate C passes (fix the MVP first, per §37, if it does not).

### M6 — Full Integration

**Objective:** Connect every piece into the single primary demo scenario and squash integration bugs.
**Why It Matters:** A working demo, not just working parts, is what gets shown in an interview.
**Inputs:** M1–M5, all complete, Gate C passed.
**Implementation Tasks:** Run the full flow (rainfall preset change → risk recomputes → priority reruns → map + list update) against the real stack; fix state-sync, CORS, serialization, or performance issues; confirm no M0-era placeholder logic remains.
**Expected Files/Modules:** Fixes across existing files; `docs/milestones/M6-integration.md`.
**Acceptance Criteria:** The exact demo scenario (§9/§12) runs start to finish with no manual intervention or console errors.
**Exact Verification Commands:** The scripted end-to-end test from §27, run against a locally running full stack (`docker-compose up` + backend + frontend).
**Tests:** The end-to-end test from §27.
**Gate/Decision Point:** None new (Gate C already passed to enter this milestone).
**Approved Fallback:** If a race condition appears between near-simultaneous scenario-change and team-count-change requests, debounce/sequence frontend requests rather than a deeper architectural change this late.
**Scope That Must NOT Be Added Yet:** Any new feature of any kind.
**Git Commit/Push Requirement:** e.g. `M6: integrate scenario-to-priority workflow`.
**Milestone Record Requirement:** `docs/milestones/M6-integration.md`.
**What I Must Understand:** What integration testing means as distinct from unit testing; be able to narrate the full request path for the demo scenario end to end.
**Automatic Next Step:** Acceptance criteria passed → commit → push → record milestone → **immediately begin M7.**

### M7 — Complete Testing & Hardening

**Objective:** Make the whole system robustly correct, not just demo-correct.
**Why It Matters:** A recruiter or interviewer may clone and run this themselves.
**Inputs:** M6, fully integrated.
**Implementation Tasks:** Run the complete §27 test suite and fix any remaining failures; add edge-case tests discovered during M6; production-configuration review (CORS, env vars, debug flags off); verify a clean build from a fresh clone.
**Expected Files/Modules:** Test-file updates across the repo; `docs/milestones/M7-testing-hardening.md`.
**Acceptance Criteria:** Full test suite green; a documented, literal fresh-clone setup produces a working local instance with no undocumented manual steps.
**Exact Verification Commands:** `pytest backend/` · `npm test` (frontend) · `npm run build` (frontend) · `python data_pipeline/validation.py --stage all` · a literal fresh-clone-and-setup walkthrough following only `docs/local-development.md`/README instructions.
**Tests:** Every test in §27, run together.
**Gate/Decision Point:** None.
**Approved Fallback:** A genuinely low-value edge case that's too costly to fix in time is documented explicitly in `docs/limitations.md` rather than left as a silently-skipped test.
**Scope That Must NOT Be Added Yet:** New features, explicitly.
**Git Commit/Push Requirement:** e.g. `M7: harden application and complete automated tests`.
**Milestone Record Requirement:** `docs/milestones/M7-testing-hardening.md`.
**What I Must Understand:** Why "works on my machine" isn't the same as "ready to ship"; what a production-config review checks for and why.
**Automatic Next Step:** Acceptance criteria passed → commit → push → record milestone → **immediately begin M8.**

### M8 — Deployment + Documentation + Portfolio Polish

**Objective:** Ship it and make the repository recruiter-ready.
**Why It Matters:** This is the milestone a recruiter or interviewer actually sees.
**Inputs:** M7, fully hardened.
**Implementation Tasks:** Deploy frontend/backend/database (§29); run migrations against production; verify the live demo scenario end to end in production; write the final README (§39); finalize `docs/methodology.md`, `docs/data-sources.md`, `docs/model-card.md` (or equivalent), `docs/limitations.md`, `docs/learning-notes.md`; take screenshots/record a short demo GIF; final repo cleanup (dead code removed, `.env.example` accurate, `LICENSE` added).
**Expected Files/Modules:** `README.md` (final), all `docs/*`, deployment config, `LICENSE`, `docs/milestones/M8-deployment.md`.
**Acceptance Criteria:** All items in §48's Definition of Done are checked; the live URL works when opened cold; the repository reads clearly to someone who has never seen the project.
**Exact Verification Commands:** A cold-browser production smoke test hitting the live URL and running the demo scenario; `pytest`/`npm test` green in CI (or CI-equivalent) against the deployed configuration.
**Tests:** All existing tests, verified once more against the deployed configuration.
**Gate/Decision Point:** **Gate D.**
**Approved Fallback:** If a free-tier deployment cold start makes the first load slow, document this proactively as a known limitation (§41) and keep a backup demo recording rather than treating it as a blocker.
**Scope That Must NOT Be Added Yet:** N/A — final milestone.
**Git Commit/Push Requirement:** e.g. `M8: deploy FloodLens and finalize portfolio documentation`.
**Milestone Record Requirement:** `docs/milestones/M8-deployment.md`.
**What I Must Understand:** The full deployment topology and why each piece was chosen; be able to walk through the README/methodology docs as if presenting them; be ready for every question in §44.
**Automatic Next Step:** Acceptance criteria passed → commit → push → record milestone → **run Gate D** → if passed, mark **FLOODLENS COMPLETE** (§48).

---

## 48. Final Codex Definition of Done

Do not stop at "code generated," "frontend looks good," "API created," or "works locally." The project is complete **only** when all of the following are true:

1. Real datasets are processed.
2. Risk methodology is implemented (ML or susceptibility index, per Gate B's actual outcome).
3. Data-validation checks pass.
4. Backend works.
5. PostGIS works.
6. Interactive map works.
7. Rainfall scenarios (presets) work.
8. Village/zone details work.
9. Population exposure works.
10. Emergency-response priority engine works, using the corrected §20 formula.
11. Frontend/backend/database are fully integrated.
12. Automated tests pass.
13. Lint/build pass.
14. Deployment works.
15. Live production smoke test passes.
16. GitHub repository is updated and reflects real development history.
17. README is complete.
18. Methodology docs exist.
19. Data-source docs exist.
20. Limitations are documented.
21. Milestone records (`docs/milestones/`) exist for M0–M8.
22. Learning notes (`docs/learning-notes.md`) exist and are understandable to a student.
23. Screenshots/demo material exist.
24. No secrets are committed.
25. Repository is clean.
26. The production URL works from a fresh browser, cold.

Only then mark:

# FLOODLENS COMPLETE

---

## 49. Deadline Philosophy

October 4–5, 2026 is the **outer deadline**, not a target completion date. If milestones can be completed correctly and with full tests passing faster than that, Codex should do so — earlier completion is strictly better, since remaining time converts directly into bug-fixing, deeper testing, understanding the project, README polish, demo practice, and interview preparation. Codex must never intentionally pace or stretch implementation to fill calendar time.
