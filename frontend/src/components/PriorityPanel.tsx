import { useEffect, useState } from 'react'
import { api, people, type Scenario, type Village } from '../api/client'
export type Priority = Village & { rank: number; priority_score: number; population_ranking_rule: string }
export default function PriorityPanel({ scenario, onSelect, onRanked }: { scenario: Scenario; onSelect: (id: string) => void; onRanked: (ids: string[]) => void }) {
  const [teams, setTeams] = useState('')
  const [items, setItems] = useState<Priority[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const valid = teams !== '' && /^\d+$/.test(teams) && Number(teams) <= 100000
  useEffect(() => {
    setItems([]); onRanked([]); setError(''); setLoading(false)
    if (!valid) return
    const controller = new AbortController(); setLoading(true)
    const timer = setTimeout(() => {
      api<Priority[]>('/priorities/calculate', { scenario_id: scenario, available_teams: Number(teams) }, controller.signal).then(result => { if (!controller.signal.aborted) { setItems(result); onRanked(result.map(v => v.id)); setLoading(false) } }).catch(() => { if (!controller.signal.aborted) { setError('Priority data unavailable. Change the team count to retry.'); setLoading(false) } })
    }, 200)
    return () => { clearTimeout(timer); controller.abort() }
  }, [scenario, teams, valid, onRanked])
  return <section className="priority-panel"><p className="eyebrow">RESPONSE PLANNING</p><h2>Where to assess first</h2><p>Susceptibility + modeled population. One assessment team per listed village.</p><label className="teams-label" htmlFor="teams">Available response teams<input id="teams" type="number" min="0" max="100000" step="1" value={teams} onChange={e => setTeams(e.target.value)} placeholder="e.g. 5" /></label>
    {teams === '' && <div className="empty-state">Set available teams to see a priority ranking.</div>}
    {teams !== '' && !valid && <p role="alert">Enter a whole number from 0 to 100,000.</p>}
    {loading && <p role="status">Calculating priorities…</p>}{error && <p role="alert">{error}</p>}
    {valid && !loading && !error && items.length === 0 && <p>No teams allocated. Increase the count to see priorities.</p>}
    <ol className="priorities">{items.map(v => <li key={v.id}><button onClick={() => onSelect(v.id)} data-village-id={v.id}><span className="rank">{v.rank.toString().padStart(2,'0')}</span><span><strong>{v.name}</strong><small>{v.tehsil} · {v.risk_category} · index {v.risk_score.toFixed(3)}</small><small>Population {people(v.population_estimate)}</small><small>Priority {v.priority_score.toFixed(3)} · {v.accessibility.category} access</small><small>{(v.accessibility.distance_to_major_road_m/1000).toFixed(2)} km to major road · context only</small><small>{v.top_factors.join(', ').replaceAll('_',' ')}</small>{v.population_estimate === null && <em>Unknown population; median used for ranking</em>}</span></button></li>)}</ol>
    {items.length > 0 && <p className="fineprint">Blue outlines mark these {items.length} villages. Prioritize field assessment and verify local conditions.</p>}
  </section>
}
