/**
 * toApiError 테스트 (TDD RED)
 * spec: 000-foundation
 */
import { describe, expect, it } from 'vitest'
import { toApiError } from './errors'

describe('toApiError', () => {
  it('response.data.error가 있으면 { code, message }를 반환한다', () => {
    const axiosError = {
      response: {
        data: { error: { code: 'EMAIL_ALREADY_EXISTS', message: '이미 사용 중인 이메일입니다.' } },
      },
    }
    const result = toApiError(axiosError as any)
    expect(result).toMatchObject({ code: 'EMAIL_ALREADY_EXISTS', message: '이미 사용 중인 이메일입니다.' })
  })

  it('response.data.error에 details가 있으면 포함한다', () => {
    const axiosError = {
      response: {
        data: {
          error: {
            code: 'VALIDATION_ERROR',
            message: '오류',
            details: [{ field: 'email', message: '형식 오류' }],
          },
        },
      },
    }
    const result = toApiError(axiosError as any)
    expect(result.details).toEqual([{ field: 'email', message: '형식 오류' }])
  })

  it('response가 없으면 UNKNOWN_ERROR를 반환한다', () => {
    const result = toApiError({ response: undefined } as any)
    expect(result.code).toBe('UNKNOWN_ERROR')
    expect(result.message).toContain('알 수 없는 오류')
  })
})
