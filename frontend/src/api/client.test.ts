import { afterEach, expect, test, vi } from 'vitest'
import { api } from './client'

afterEach(() => { vi.unstubAllGlobals(); vi.useRealTimers() })

test('recovers from initialization and a connection handoff', async () => {
  vi.useFakeTimers()
  const fetch = vi.fn().mockResolvedValueOnce(new Response('', { status: 503 }))
    .mockRejectedValueOnce(new TypeError('Failed to fetch'))
    .mockResolvedValueOnce(new Response('{"ready":true}'))
  vi.stubGlobal('fetch', fetch)
  const result = api('/scenarios/evaluate', { scenario_id: 'normal' })
  await vi.runAllTimersAsync()
  expect(await result).toEqual({ ready: true })
  expect(fetch).toHaveBeenCalledTimes(3)
})

test('does not retry invalid requests', async () => {
  const fetch = vi.fn().mockResolvedValue(new Response('', { status: 422 }))
  vi.stubGlobal('fetch', fetch)
  await expect(api('/scenarios/evaluate', {})).rejects.toThrow('(422)')
  expect(fetch).toHaveBeenCalledTimes(1)
})

test('persistent unavailability is bounded', async () => {
  vi.useFakeTimers()
  const fetch = vi.fn().mockResolvedValue(new Response('', { status: 503 }))
  vi.stubGlobal('fetch', fetch)
  const result = expect(api('/villages')).rejects.toThrow('(503)')
  await vi.runAllTimersAsync()
  await result
  expect(fetch).toHaveBeenCalledTimes(13)
})

test('aborting a superseded scenario cancels its pending retry', async () => {
  vi.useFakeTimers()
  const fetch = vi.fn().mockResolvedValue(new Response('', { status: 503 }))
  vi.stubGlobal('fetch', fetch)
  const controller = new AbortController()
  const result = expect(api('/villages', undefined, controller.signal)).rejects.toMatchObject({ name: 'AbortError' })
  await vi.advanceTimersByTimeAsync(0)
  controller.abort()
  await result
  await vi.runAllTimersAsync()
  expect(fetch).toHaveBeenCalledTimes(1)
})
