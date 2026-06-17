import { describe, it, expect } from 'vitest'
import { validateParams, capitalize, getRoi } from './index'

describe('capitalize', () => {
  it('uppercases the first letter', () => {
    expect(capitalize('hello')).toBe('Hello')
    expect(capitalize('a')).toBe('A')
  })
})

describe('getRoi', () => {
  it('computes a long-position return', () => {
    // +10% move, long, 1x leverage
    expect(getRoi(100, 110, 1, 1)).toBeCloseTo(0.1, 5)
  })

  it('scales with leverage', () => {
    expect(getRoi(100, 110, 1, 3)).toBeCloseTo(0.3, 5)
  })

  it('inverts for a short position', () => {
    // a price rise is a loss when short
    expect(getRoi(100, 110, -1, 1)).toBeLessThan(0)
  })
})

describe('validateParams', () => {
  const numericStrategy = (selectedParams: Record<string, any>) => ({
    selectedParams,
    paramsOrder: ['ma'],
    params: { ma: { type: { func: 'Number', type: 'number' } } },
    optionalParamsOrder: [],
    optionalParams: {},
  })

  it('accepts and type-converts a valid required param', () => {
    const result = validateParams(numericStrategy({ ma: '30' }))
    expect(result.success).toBe(true)
    expect(result.updatedParams.ma).toBe(30)
  })

  it('rejects a missing required param', () => {
    expect(validateParams(numericStrategy({})).success).toBe(false)
  })

  it('rejects an empty required param', () => {
    expect(validateParams(numericStrategy({ ma: '' })).success).toBe(false)
  })

  it('rejects a non-numeric value for a numeric param', () => {
    expect(validateParams(numericStrategy({ ma: 'abc' })).success).toBe(false)
  })

  it('type-converts an optional string param via the whitelist (no eval)', () => {
    // String/Number/... are resolved from a fixed whitelist, not eval'd - the
    // optional path keeps non-numeric values (the required path is numeric-only)
    const strategy = {
      selectedParams: { ma: '30', mode: 'fast' },
      paramsOrder: ['ma'],
      params: { ma: { type: { func: 'Number', type: 'number' } } },
      optionalParamsOrder: ['mode'],
      optionalParams: { mode: { type: { func: 'String', type: 'string' } } },
    }
    const result = validateParams(strategy)
    expect(result.success).toBe(true)
    expect(result.updatedParams.ma).toBe(30)
    expect(result.updatedParams.mode).toBe('fast')
  })
})
