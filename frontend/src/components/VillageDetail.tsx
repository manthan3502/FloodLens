import type { Village } from '../api/client'
import { people } from '../api/client'
export default function VillageDetail({ village, close }: { village: Village; close: () => void }) {
  return <section className="detail" aria-label="Village detail">
    <div className="section-heading"><p className="eyebrow">VILLAGE INSIGHT</p><button className="text-button" onClick={close} aria-label="Close village detail">Close ×</button></div>
    <h2>{village.name}</h2><p>{village.tehsil} tehsil</p>
    <div className="risk-line"><span className={`badge ${village.risk_category.toLowerCase()}`}>{village.risk_category}</span><strong>{village.risk_score.toFixed(3)}<small> / 1 index</small></strong></div>
    <p className="explanation">{village.explanation}</p>
    <dl className="facts"><div><dt>Estimated village population</dt><dd>{people(village.population_estimate)}</dd></div><div><dt>Mean elevation</dt><dd>{village.raw_factors.elevation.toFixed(0)} m</dd></div><div><dt>Mean slope</dt><dd>{village.raw_factors.slope.toFixed(1)}°</dd></div><div><dt>Mean river distance</dt><dd>{(village.raw_factors.dist_to_river / 1000).toFixed(2)} km</dd></div></dl>
    <h3>What contributes to this score</h3>
    {Object.entries(village.factor_contributions).sort((a,b) => b[1]-a[1]).map(([name, value]) => <div className="factor" key={name}><span>{name.replaceAll('_', ' ')}</span><meter min="0" max="0.3" value={value} /><b>{value.toFixed(3)}</b></div>)}
    <div className="context"><h3>Accessibility · {village.accessibility.category}</h3><p>{(village.accessibility.distance_to_major_road_m / 1000).toFixed(2)} km mean distance to a major road. Context only; never a ranking penalty.</p></div>
    <h3>Historical evidence</h3><p>{village.historical_evidence.mean_detected_fraction === null ? 'No usable historical evidence for this village.' : `${(village.historical_evidence.mean_detected_fraction * 100).toFixed(1)}% mean detected change in sufficiently observed cells.`} Mean event coverage: {(village.historical_evidence.mean_event_coverage * 100).toFixed(0)}%. SAR proxies are incomplete and do not show peak inundation.</p>
    <p className="fineprint">Population: modeled WorldPop 2020 village total, not people predicted to flood. Source boundaries may have gaps.</p>
  </section>
}
