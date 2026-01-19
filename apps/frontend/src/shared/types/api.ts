/**
 * API 공통 타입 (spec: 000-foundation)
 */

export interface ApiError {
  code: string
  message: string
  details?: Array<{ field?: string; message: string }>
}

export interface ApiResponse<T> {
  success: true
  data: T
}
