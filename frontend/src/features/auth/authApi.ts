import { api } from '../../lib/api'
import type { User } from '../../stores/auth'

export type TokenResponse = {
  access_token: string
  token_type: 'bearer' | string
  user: User
}

export async function getMe(): Promise<User> {
  const { data } = await api.get<User>('/api/auth/me')
  return data
}

// Note: backend login endpoints are social-login based (/api/auth/kakao, /api/auth/google)
// Admin panel assumes you already have a valid access token to store.
