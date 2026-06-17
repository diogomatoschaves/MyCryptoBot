import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { getTrades, startBot, getMe, logout } from './index'

const mockFetch = (status: number, json: any) =>
  vi.fn().mockResolvedValue({ status, json: async () => json })

describe('api request helper (exercised via wrappers)', () => {
  beforeEach(() => {
    // clear any csrf cookie carried over between tests (jsdom persists them)
    document.cookie = 'csrf_access_token=; max-age=0'
    vi.stubGlobal('fetch', mockFetch(200, { ok: true }))
  })

  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('calls the API same-origin under /api with credentials', async () => {
    await getTrades()
    const [url, opts] = (fetch as any).mock.calls[0]
    expect(url).toBe('/api/trades')
    expect(opts.method).toBe('GET')
    expect(opts.credentials).toBe('include')
  })

  it('omits the CSRF header on GETs', async () => {
    document.cookie = 'csrf_access_token=tok123'
    await getTrades()
    const [, opts] = (fetch as any).mock.calls[0]
    expect(opts.headers['X-CSRF-TOKEN']).toBeUndefined()
  })

  it('sends the CSRF header (from cookie) + JSON body on state-changing calls', async () => {
    document.cookie = 'csrf_access_token=tok123'
    await startBot({ pipelineId: 1 })
    const [url, opts] = (fetch as any).mock.calls[0]
    expect(url).toBe('/api/start_bot')
    expect(opts.method).toBe('PUT')
    expect(opts.headers['X-CSRF-TOKEN']).toBe('tok123')
    expect(opts.headers['Content-Type']).toBe('application/json')
    expect(JSON.parse(opts.body)).toEqual({ pipelineId: 1 })
  })

  it('throws "401" on an unauthorized authed request (drives logout)', async () => {
    vi.stubGlobal('fetch', mockFetch(401, {}))
    await expect(getTrades()).rejects.toThrow('401')
  })

  it('does not throw on 401 for unauthenticated calls (logout)', async () => {
    vi.stubGlobal('fetch', mockFetch(401, { logout: true }))
    await expect(logout()).resolves.toEqual({ logout: true })
  })

  it('getMe hits /api/me', async () => {
    await getMe()
    expect((fetch as any).mock.calls[0][0]).toBe('/api/me')
  })
})
