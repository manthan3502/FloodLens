import type { FeatureCollection, MultiPolygon } from 'geojson'
export type Scenario = 'normal' | 'heavy' | 'extreme'
export type Category = 'Low' | 'Medium' | 'High' | 'Critical'
export interface Village {
  id: string; name: string; tehsil: string; risk_score: number; risk_category: Category
  population_estimate: number | null; scenario_id: Scenario; explanation: string
  top_factors: string[]; factor_contributions: Record<string, number>
  raw_factors: { elevation: number; slope: number; dist_to_river: number; dist_to_road: number }
  accessibility: { category: string; distance_to_major_road_m: number }
  historical_evidence: { mean_detected_fraction: number | null; mean_event_coverage: number; unknown_area_fraction: number; label: string }
}
export type VillageCollection = FeatureCollection<MultiPolygon, Village> & { last_processed: string }
export interface Metadata { model_type: string; notes: { limitations: string; data_processed: string; config: { weights: Record<string, number> } }; rainfall_scenarios: { id: Scenario; name: string; rainfall_24h_mm: number; rainfall_72h_mm: number }[] }
const base = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
function retryDelay(milliseconds: number, signal?: AbortSignal) {
  return new Promise<void>((resolve, reject) => {
    signal?.throwIfAborted()
    const abort = () => { clearTimeout(timer); reject(signal?.reason) }
    const timer = setTimeout(() => { signal?.removeEventListener('abort', abort); resolve() }, milliseconds)
    signal?.addEventListener('abort', abort, { once: true })
  })
}
export async function api<T>(path: string, body?: unknown, signal?: AbortSignal): Promise<T> {
  // These endpoints only read/evaluate data. Recover from free-tier wake-up and
  // the short listener-to-Uvicorn handoff without retrying validation errors.
  for (let attempt = 0; ; attempt++) {
    signal?.throwIfAborted()
    let response: Response
    try {
      response = await fetch(`${base}${path}`, { method: body ? 'POST' : 'GET', headers: body ? { 'Content-Type': 'application/json' } : undefined, body: body ? JSON.stringify(body) : undefined, signal })
    } catch (error) {
      if (signal?.aborted || !(error instanceof TypeError) || attempt >= 12) throw error
      await retryDelay(Math.min(1000 * 2 ** attempt, 5000), signal)
      continue
    }
    if (response.ok) return response.json() as Promise<T>
    if (![502, 503, 504].includes(response.status) || attempt >= 12) {
      throw new Error(`Study data unavailable (${response.status}). Please retry.`)
    }
    await retryDelay(Math.min(1000 * 2 ** attempt, 5000), signal)
  }
}
export const people = (value: number | null) => value === null ? 'Data unavailable' : `~${Math.round(value).toLocaleString('en-IN')}`
