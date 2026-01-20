/**
 * formatToKST 테스트
 * spec: 000-foundation
 */
import { describe, expect, it } from 'vitest'
import { formatToKST } from './date'

describe('formatToKST', () => {
  it('formatToKST("2025-01-19T15:30:00Z") → KST "2025. 01. 20. 00:30" 형식', () => {
    // 2025-01-19 15:30 UTC = 2025-01-20 00:30 KST
    expect(formatToKST('2025-01-19T15:30:00Z')).toBe('2025. 01. 20. 00:30')
  })

  it('formatToKST("2025-01-19T15:30:00.000Z") → 동일', () => {
    expect(formatToKST('2025-01-19T15:30:00.000Z')).toBe('2025. 01. 20. 00:30')
  })
})
