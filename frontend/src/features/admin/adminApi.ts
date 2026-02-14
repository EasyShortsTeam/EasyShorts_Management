import { api } from '../../lib/api'

export type Page<T> = {
  items: T[]
  total: number
  limit: number
  offset: number
}

export type AdminUser = {
  user_id: string
  email: string
  username: string
  is_active: number
  created_at?: string
  plan?: string | null
  credit?: number | null
  oauth_provider?: string | null
}

export type AdminEpisode = {
  episode_id: string
  user_id?: string | null
  title?: string | null
  series_layout?: string | null
  error?: string | null
  created_at?: string
  video_url?: string | null
  preview_video_url?: string | null
}

export type AdminJob = {
  job_id: string
  job_type: string
  status: string
  created_at?: string
  updated_at?: string
  result?: any
  error?: string | null
}

export type CreditPatch = {
  mode: 'set' | 'add'
  amount: number
  reason?: string
}

export type AssetItem = {
  key: string
  size?: number | null
  last_modified?: string | null
  url?: string | null
}

export type StatusAgg = {
  status: string
  count: number
  amount_sum?: number | null
}

export type DailyAgg = {
  date: string
  count: number
  amount_sum?: number | null
}

export type AdminOverviewMetrics = {
  users_total: number
  users_active: number
  episodes_total: number
  jobs_total: number
  jobs_by_status: StatusAgg[]
  orders_by_status: StatusAgg[]
  orders_daily: DailyAgg[]
  credit_logs_daily: DailyAgg[]
}

export type EpisodeDeleteResult = {
  episode_id: string
  deleted_db: boolean
  deleted_objects: string[]
  failed_objects: string[]
}

export async function listUsers(params: { q?: string; is_active?: number; limit?: number; offset?: number }): Promise<Page<AdminUser>> {
  const { data } = await api.get<Page<AdminUser>>('/api/admin/users', { params })
  return data
}

export async function patchUserCredit(user_id: string, payload: CreditPatch): Promise<AdminUser> {
  const { data } = await api.patch<AdminUser>(`/api/admin/users/${user_id}/credit`, payload)
  return data
}

export async function patchUserActive(user_id: string, is_active: number): Promise<AdminUser> {
  const { data } = await api.patch<AdminUser>(`/api/admin/users/${user_id}/active`, { is_active })
  return data
}

export async function listEpisodes(params: { q?: string; user_id?: string; limit?: number; offset?: number }): Promise<Page<AdminEpisode>> {
  const { data } = await api.get<Page<AdminEpisode>>('/api/admin/episodes', { params })
  return data
}

export async function deleteEpisode(episode_id: string, params?: { delete_objects?: boolean }): Promise<EpisodeDeleteResult> {
  const { data } = await api.delete<EpisodeDeleteResult>(`/api/admin/episodes/${episode_id}`, { params })
  return data
}

export async function listJobs(params: { status?: string; job_type?: string; limit?: number; offset?: number }): Promise<Page<AdminJob>> {
  const { data } = await api.get<Page<AdminJob>>('/api/admin/jobs', { params })
  return data
}

export async function getOverviewMetrics(params?: { days?: number }): Promise<AdminOverviewMetrics> {
  const { data } = await api.get<AdminOverviewMetrics>('/api/admin/metrics/overview', { params })
  return data
}

export async function getJob(job_id: string): Promise<AdminJob> {
  const { data } = await api.get<AdminJob>(`/api/admin/jobs/${job_id}`)
  return data
}

export async function listAssets(kind: 'fonts' | 'soundeffects' | 'userassets', params?: { prefix?: string }): Promise<AssetItem[]> {
  const { data } = await api.get<AssetItem[]>(`/api/admin/assets/${kind}`, { params })
  return data
}

export async function uploadAsset(kind: 'fonts' | 'soundeffects' | 'userassets', key: string, file: File): Promise<AssetItem> {
  const form = new FormData()
  form.append('file', file)
  const { data } = await api.post<AssetItem>(`/api/admin/assets/${kind}/upload`, form, {
    params: { key },
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return data
}
