import { create } from 'zustand'

export type User = {
  user_id: string
  email: string
  username: string
  is_active?: number
  plan?: string
  credit?: number
  oauth_provider?: string | null
}

type AuthState = {
  token: string | null
  user: User | null
  setToken: (token: string | null) => void
  setUser: (user: User | null) => void
  logout: () => void
}

export const useAuthStore = create<AuthState>((set) => ({
  token: localStorage.getItem('access_token'),
  user: null,
  setToken: (token) => {
    if (token) localStorage.setItem('access_token', token)
    else localStorage.removeItem('access_token')
    set({ token })
  },
  setUser: (user) => set({ user }),
  logout: () => {
    localStorage.removeItem('access_token')
    set({ token: null, user: null })
  },
}))
