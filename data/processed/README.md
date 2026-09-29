# Processed data artifact

`seed.json.gz` contains source-derived PostGIS rows. It supports a fresh clone without satellite processing: `python -m data_pipeline.seed` after configuring `DATABASE_URL` and starting PostGIS.

DataMeet village boundaries and OpenStreetMap waterways require ODbL attribution. WorldPop population is CC BY 4.0; terrain is SRTM, and flood evidence is a self-derived Sentinel-1 proxy subject to the Copernicus data terms. See `docs/data-sources.md` for exact products and URLs. The software license does not replace upstream data terms.

Population is a modeled estimate. Missing values remain null. Flood evidence is not an official disaster inventory, and these artifacts must not be used as operational evacuation guidance.
