import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { afterEach, beforeEach, expect, test, vi } from 'vitest'
import App from '../src/App'
import fixture from './village-fixture.json'
vi.mock('../src/components/Map', () => ({ colors: { Low: '#69a58a', Medium: '#e9c561', High: '#e5944e', Critical: '#c35550' }, default: ({ onSelect }: { onSelect: (id: string) => void }) => <button onClick={() => onSelect(fixture.features[0].properties.id)}>Select test village</button> }))
const fetchMock = vi.fn()
beforeEach(() => {
  vi.stubGlobal('fetch', fetchMock)
  fetchMock.mockImplementation(async (url: string) => ({ ok: true, json: async () => url.endsWith('/rivers') ? { type: 'FeatureCollection', features: [] } : url.endsWith('/model/metadata') ? { rainfall_scenarios: [] } : url.includes('/villages/') ? fixture.features[0].properties : fixture }))
})
afterEach(() => { cleanup(); vi.unstubAllGlobals(); vi.clearAllMocks() })
test('loads map data, changes scenario and loads village detail', async () => {
  render(<App />)
  expect(screen.getByText('Loading real study data…')).toBeTruthy()
  await screen.findByRole('button', { name: 'Select test village' })
  fireEvent.change(screen.getByLabelText('Rainfall scenario'), { target: { value: 'extreme' } })
  await waitFor(() => expect(fetchMock).toHaveBeenCalledWith(expect.stringContaining('/scenarios/evaluate'), expect.objectContaining({ body: JSON.stringify({ scenario_id: 'extreme' }) })))
  fireEvent.click(screen.getByRole('button', { name: 'Select test village' }))
  await screen.findByRole('heading', { name: fixture.features[0].properties.name.replace(/\s+/g, ' ') })
  expect(screen.getByText('Estimated village population')).toBeTruthy()
})
test('failed API displays an explicit error and retry', async () => {
  fetchMock.mockRejectedValue(new Error('Network unavailable'))
  render(<App />)
  await screen.findByRole('alert')
  expect(screen.getByRole('button', { name: 'Retry data' })).toBeTruthy()
})
test('empty collection is explicit', async () => {
  fetchMock.mockResolvedValue({ ok: true, json: async () => ({ type: 'FeatureCollection', features: [], rainfall_scenarios: [] }) })
  render(<App />)
  await screen.findByText('No villages available for this scenario.')
})
test('methodology and historical limitations are accessible', async () => {
  render(<App />)
  fireEvent.click(screen.getByRole('button', { name: /Understand the methodology/ }))
  expect(screen.getByRole('dialog', { name: 'Methodology' })).toBeTruthy()
  fireEvent.click(screen.getByLabelText('Highlight SAR change zones'))
  expect(screen.getByText(/Dashed borders:/)).toBeTruthy()
  await screen.findByRole('button', { name: 'Select test village' })
})

