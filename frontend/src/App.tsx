import { useEffect, useState } from 'react'
import type { FeatureCollection } from 'geojson'
import { api, type Metadata, type Scenario, type Village, type VillageCollection } from './api/client'
import StudyMap, { colors } from './components/Map'
import VillageDetail from './components/VillageDetail'

export default function App() {
  const [scenario, setScenario] = useState<Scenario>('normal')
  const [data, setData] = useState<VillageCollection | null>(null)
  const [rivers, setRivers] = useState<FeatureCollection | null>(null)
  const [metadata, setMetadata] = useState<Metadata | null>(null)
  const [selected, setSelected] = useState<string | null>(null)
  const [detail, setDetail] = useState<Village | null>(null)
  const [detailError, setDetailError] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [retry, setRetry] = useState(0)
  const [history, setHistory] = useState(false)
  const [about, setAbout] = useState(false)
  useEffect(() => {
    const controller = new AbortController()
    api<FeatureCollection>('/rivers', undefined, controller.signal).then(setRivers).catch(() => {})
    api<Metadata>('/model/metadata', undefined, controller.signal).then(setMetadata).catch(() => {})
    return () => controller.abort()
  }, [retry])
  useEffect(() => {
    const controller = new AbortController()
    setLoading(true); setError('')
    api<VillageCollection>('/scenarios/evaluate', { scenario_id: scenario }, controller.signal).then(result => { setData(result); setLoading(false) }).catch(e => { if (!controller.signal.aborted) { setError(e.message); setLoading(false) } })
    return () => controller.abort()
  }, [scenario, retry])
  useEffect(() => {
    setDetail(null); setDetailError('')
    if (!selected) return
    const controller = new AbortController()
    api<Village>(`/villages/${selected}?scenario_id=${scenario}`, undefined, controller.signal).then(setDetail).catch(() => { if (!controller.signal.aborted) setDetailError('Village details unavailable. Select again or retry.') })
    return () => controller.abort()
  }, [selected, scenario, retry])
  const preset = metadata?.rainfall_scenarios.find(p => p.id === scenario)
  const counts = Object.keys(colors).map(name => [name, data?.features.filter(f => f.properties.risk_category === name).length ?? 0] as const)
  return <main>
    <header><div className="brand"><span className="brand-mark" aria-hidden="true">≋</span><div><h1>FloodLens</h1><p>Geospatial flood susceptibility & response planning</p></div></div><span className="status"><i /> KOLHAPUR · RESEARCH PROTOTYPE</span></header>
    <section className="intro"><div><p className="eyebrow">TERRAIN. EVIDENCE. INFORMED PRIORITIES.</p><h2>A clearer view of flood susceptibility.</h2><p>Explore 380 named settlements across Karvir, Panhala, Hatkanangale and Shirol.</p></div><button className="outline-button" onClick={() => setAbout(true)}>Understand the methodology ↗</button></section>
    <section className="toolbar" aria-label="Scenario controls"><div><label htmlFor="rainfall">Rainfall scenario</label><select id="rainfall" value={scenario} onChange={e => setScenario(e.target.value as Scenario)}><option value="normal">Normal rainfall</option><option value="heavy">Heavy rainfall</option><option value="extreme">Extreme rainfall</option></select></div><p className="rainfall-summary">{preset ? <><strong>{preset.rainfall_24h_mm.toFixed(1)} mm</strong> / 24h <span>·</span> <strong>{preset.rainfall_72h_mm.toFixed(1)} mm</strong> / 72h</> : 'Scenario context unavailable or loading…'}<small>Modeled reanalysis presets · not a weather forecast</small></p><label className="toggle"><input type="checkbox" checked={history} onChange={e => setHistory(e.target.checked)} /> Highlight SAR change zones</label></section>
    <div className="workspace"><section className="map-card" aria-label="Village susceptibility map">
      <div className="map-heading"><div><h3>Study-area susceptibility</h3><p>Click a village to inspect its contributing factors</p></div><span className="count">{data?.features.length ?? '—'} settlements</span></div>
      <div className="map-frame">{data && data.features.length > 0 && <StudyMap data={data} rivers={rivers} selected={selected} onSelect={setSelected} history={history} />}
        {loading && <div className="map-state" role="status">Loading real study data…</div>}
        {error && <div className="map-state error" role="alert"><strong>Study data unavailable</strong><p>{error}</p><button onClick={() => setRetry(v => v+1)}>Retry data</button></div>}
        {!loading && !error && data?.features.length === 0 && <div className="map-state">No villages available for this scenario.</div>}
      </div>
      <div className="legend" aria-label="Susceptibility legend">{counts.map(([name, count]) => <span key={name}><i style={{ background: colors[name as keyof typeof colors] }} />{name}<b>{count}</b></span>)}</div>
      {history && <p className="map-note">Dashed borders: villages with &gt;1% mean SAR change in observed cells. Village summaries, not flood-extent boundaries. 2019 coverage is sparse; 2021 imagery predates peak response.</p>}
      {!rivers && <p className="map-note">Waterway layer unavailable or still loading.</p>}
    </section><aside>
      <section className="priority-panel"><p className="eyebrow">RESPONSE PLANNING</p><h2>Where to assess first</h2><p>A transparent ranking combines susceptibility and estimated population exposure.</p><div className="empty-state">Priority allocation is being connected in M5.</div></section>
      {selected ? detail ? <VillageDetail village={detail} close={() => setSelected(null)} /> : <section className="detail" role="status">{detailError || 'Loading village details…'}</section> : <section className="selection-hint"><span aria-hidden="true">⌖</span><h3>Explore a village</h3><p>Select a polygon on the map to see terrain, population estimates and historical evidence.</p></section>}
    </aside></div>
    <footer><span>Data processed {data?.last_processed ?? '—'} · SRTM · Sentinel-1 · WorldPop · Open-Meteo · DataMeet / OSM</span><strong>Academic decision support. Not an operational flood warning system.</strong></footer>
    {about && <div className="modal-backdrop"><section className="methodology" role="dialog" aria-modal="true" aria-label="Methodology"><button className="text-button close" onClick={() => setAbout(false)}>Close ×</button><p className="eyebrow">HOW TO READ FLOODLENS</p><h2>A relative index, with visible limits.</h2><p>The score combines low elevation (25%), river proximity (30%), flat terrain (10%), historical SAR evidence (15%) and rainfall (20%). These prototype weights are assumptions, not fitted or scientifically validated probabilities.</p><p>Scores are area-weighted from 250 m cells into source village boundaries. Low, Medium, High and Critical are index bands at 0.25, 0.50 and 0.75, not official warnings.</p><p>2019 SAR covers 5.9% of the area. The 2021 scene is from 22 July, before documented 25 July rescue operations. Unknown history uses a flagged neutral value. No supervised ML accuracy is claimed.</p><p>WorldPop is a modeled 2020 estimate; nine villages have unknown population. Rainfall is coarse reanalysis. Accessibility is context only. This prototype cannot determine safe evacuation routes or forecast flood depth.</p>{!metadata && <p>Live methodology metadata is unavailable; these are the documented index-v1 defaults.</p>}</section></div>}
  </main>
}
