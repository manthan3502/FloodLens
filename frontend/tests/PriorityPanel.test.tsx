import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { afterEach, expect, test, vi } from 'vitest'
import PriorityPanel from '../src/components/PriorityPanel'
import fixture from './village-fixture.json'
afterEach(() => { cleanup(); vi.unstubAllGlobals() })
test('team and scenario changes refetch, render and synchronize selection', async () => {
  const village = fixture.features[0].properties
  const fetcher = vi.fn().mockResolvedValue({ ok: true, json: async () => [{ ...village, rank: 1, priority_score: .7 }] })
  vi.stubGlobal('fetch', fetcher)
  const onSelect = vi.fn(); const onRanked = vi.fn()
  const { rerender } = render(<PriorityPanel scenario="normal" onSelect={onSelect} onRanked={onRanked} />)
  fireEvent.change(screen.getByLabelText('Available response teams'), { target: { value: '1' } })
  await screen.findByRole('button', { name: new RegExp('Sawarde') })
  expect(onRanked).toHaveBeenLastCalledWith([village.id])
  fireEvent.click(screen.getByRole('button', { name: /Sawarde/ }))
  expect(onSelect).toHaveBeenCalledWith(village.id)
  rerender(<PriorityPanel scenario="extreme" onSelect={onSelect} onRanked={onRanked} />)
  await waitFor(() => expect(fetcher).toHaveBeenCalledWith(expect.any(String), expect.objectContaining({ body: JSON.stringify({ scenario_id: 'extreme', available_teams: 1 }) })))
})
test('zero and invalid teams have clear states', async () => {
  vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: true, json: async () => [] }))
  render(<PriorityPanel scenario="normal" onSelect={vi.fn()} onRanked={vi.fn()} />)
  fireEvent.change(screen.getByLabelText('Available response teams'), { target: { value: '-1' } })
  expect(screen.getByRole('alert')).toBeTruthy()
  fireEvent.change(screen.getByLabelText('Available response teams'), { target: { value: '0' } })
  await screen.findByText(/No teams allocated/)
})
