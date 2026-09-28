import { render, screen } from '@testing-library/react'
import { expect, test } from 'vitest'
import App from '../src/App'

test('renders a real Leaflet foundation with honest data status', () => {
  render(<App />)
  expect(screen.getByRole('heading', { name: 'FloodLens' })).toBeTruthy()
  expect(screen.getByText(/Dataset verification is in progress/)).toBeTruthy()
  expect(document.querySelector('.leaflet-container')).toBeTruthy()
})
