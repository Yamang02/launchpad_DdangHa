import axios, { AxiosError, AxiosInstance } from 'axios'
import type { ApiError } from '../types/api'

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'

export const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError<{ success?: false; error?: ApiError }>) => {
    if (error.response?.data?.error) {
      return Promise.reject(error.response.data.error as ApiError)
    }
    return Promise.reject({
      code: 'UNKNOWN_ERROR',
      message: '알 수 없는 오류가 발생했습니다.',
    } as ApiError)
  }
)
