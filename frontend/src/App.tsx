import { MapContainer, TileLayer } from 'react-leaflet'

export default function App() {
  return <main>
    <header><div><p className="eyebrow">RURAL KOLHAPUR · MAHARASHTRA</p><h1>FloodLens</h1><p>Flood susceptibility & emergency response prioritization</p></div><span className="status">Foundation · M0</span></header>
    <section className="notice" aria-label="Data status"><strong>Study area preview</strong><span>Dataset verification is in progress. Susceptibility and response rankings are not available yet.</span></section>
    <section aria-label="Kolhapur study area map" className="map">
      <MapContainer center={[16.75, 74.35]} zoom={10} scrollWheelZoom={true}>
        <TileLayer attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors' url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
      </MapContainer>
    </section>
    <footer>Karvir · Panhala · Hatkanangale · Shirol <span>Academic decision-support prototype. Not an operational flood warning system.</span></footer>
  </main>
}
