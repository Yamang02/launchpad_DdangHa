/**
 * API 에러 변환 (spec: 000-foundation)
 */
import type { ApiError } from '../types/api'

/** Axios 등 HTTP 에러 객체에서 ApiError로 변환 */
export function toApiError(err: { response?: { data?: { error?: ApiError } } }): ApiError {
  const e = err?.response?.data?.error
  if (e && typeof e.code === 'string' && typeof e.message === 'string') {
    const out: ApiError = { code: e.code, message: e.message }
    if (e.details && Array.isArray(e.details)) out.details = e.details
    return out
  }
  return { code: 'UNKNOWN_ERROR', message: '알 수 없는 오류' }
}
