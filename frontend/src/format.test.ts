import { describe, expect, it } from 'vitest'
import { formatValue, statusLabel } from './format'

describe('format helpers', () => {
  it('formats BRL prices', () => {
    expect(formatValue('2199.90', 'price')).toContain('2.199,90')
  })

  it('translates run status', () => {
    expect(statusLabel('changed')).toBe('Alteração')
  })
})
