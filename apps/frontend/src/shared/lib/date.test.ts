/**
 * formatToKST 테스트 (TDD RED)
 * spec: 000-foundation
 */
import { describe, expect, it } from 'vitest'
import { formatToKST } from './date'

describe('formatToKST', () => {
  it('UTC ISO 8601을 KST "YYYY. MM. DD. HH:mm" 형식으로 변환한다', () => {
    // 2025-01-19 15:30 UTC = 2025-01-20 00:30 KST
    expect(formatToKST('2025-01-19T15:30:00Z')).toMatch(/2025\.\s*01\.\s*20\.\s*00:30/)
  })

  it('밀리초 포함 ISO 8601도 동일하게 변환한다', () => {
    expect(formatToKST('2025-01-19T15:30:00.000Z')).toMatch(/2025\.\s*01\.\s*20\.\s*00:30/)
  })
})
