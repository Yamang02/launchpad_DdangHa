import { apiClient } from './client'

export interface SignupRequest {
  email: string
  password: string
  nickname: string
}

export interface SignupResponse {
  uid: string
  email: string
  nickname: string
}

export async function signup(data: SignupRequest): Promise<SignupResponse> {
  const { data: body } = await apiClient.post<{ success: true; data: SignupResponse }>(
    '/auth/signup',
    data
  )
  return body.data
}
