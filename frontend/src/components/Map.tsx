import { useEffect, useRef } from 'react'
import { GeoJSON, MapContainer, TileLayer, useMap } from 'react-leaflet'
import type { FeatureCollection } from 'geojson'
import L from 'leaflet'
import type { Category, VillageCollection } from '../api/client'
export const colors: Record<Category, string> = { Low: '#69a58a', Medium: '#e9c561', High: '#e5944e', Critical: '#c35550' }
function InitialBounds({ data }: { data: VillageCollection }) {
  const map = useMap(); const fitted = useRef(false)
  useEffect(() => { if (!fitted.current) { map.fitBounds(L.geoJSON(data).getBounds(), { padding: [24, 24] }); fitted.current = true } }, [map, data])
  return null
}
export default function StudyMap({ data, rivers, selected, onSelect, history, priorities = [] }: { data: VillageCollection; rivers: FeatureCollection | null; selected: string | null; onSelect: (id: string) => void; history: boolean; priorities?: string[] }) {
  return <MapContainer center={[16.72, 74.3]} zoom={10} scrollWheelZoom className="study-map">
    <TileLayer attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors' url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
    <InitialBounds data={data} />
    <GeoJSON key={`${data.features[0]?.properties.scenario_id}-${selected}-${history}-${priorities.join(',')}`} data={data} style={feature => {
      const p = feature!.properties
      return { color: p.id === selected ? '#102e2c' : priorities.includes(p.id) ? '#245ec1' : '#627d73', weight: p.id === selected ? 3 : priorities.includes(p.id) ? 2.5 : 0.8, fillColor: colors[p.risk_category as Category], fillOpacity: 0.65, dashArray: history && (p.historical_evidence.mean_detected_fraction ?? 0) > 0.01 ? '4 3' : undefined }
    }} onEachFeature={(feature, layer) => {
      const text = document.createElement('span'); text.textContent = `${feature.properties.name} · ${feature.properties.risk_category}`
      layer.bindTooltip(text); layer.on('click', () => onSelect(feature.properties.id))
    }} />
    {rivers && <GeoJSON data={rivers} style={{ color: '#2b7fab', weight: 1.5, opacity: 0.8 }} />}
  </MapContainer>
}
