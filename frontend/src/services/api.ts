import type {
  Job,
  Role,
  SavedFilter,
  SearchFilters,
  SearchHistory,
  SearchProfile,
  SearchResult,
  Skill,
  Source,
  Stack,
  DashboardData,
  LinkAccess,
  LinkAccessPage,
} from '../types'

const BASE = 'http://localhost:8000/api'

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (!res.ok) {
    const text = await res.text()
    throw new Error(`API ${res.status}: ${text}`)
  }
  if (res.status === 204) return undefined as T
  return res.json() as Promise<T>
}

export const api = {
  // Search
  search: (filters: SearchFilters) =>
    request<SearchResult>('/search', { method: 'POST', body: JSON.stringify(filters) }),

  // Jobs
  getJobs: (params?: {
    source?: string
    min_score?: number
    is_favorite?: boolean
    is_hidden?: boolean
    status?: string
    search?: string
    limit?: number
  }) => {
    const qs = new URLSearchParams()
    if (params?.source) qs.set('source', params.source)
    if (params?.min_score != null) qs.set('min_score', String(params.min_score))
    if (params?.is_favorite != null) qs.set('is_favorite', String(params.is_favorite))
    if (params?.is_hidden != null) qs.set('is_hidden', String(params.is_hidden))
    if (params?.status) qs.set('status', params.status)
    if (params?.search) qs.set('search', params.search)
    if (params?.limit != null) qs.set('limit', String(params.limit))
    return request<Job[]>(`/jobs?${qs}`)
  },

  getJob: (id: number) => request<Job>(`/jobs/${id}`),

  updateJob: (
    id: number,
    data: Partial<Pick<Job, 'is_favorite' | 'is_hidden' | 'applied' | 'notes' | 'status' | 'applied_at' | 'tags'>>
  ) => request<Job>(`/jobs/${id}`, { method: 'PATCH', body: JSON.stringify(data) }),
  deleteJob: (id: number) => request<void>(`/jobs/${id}`, { method: 'DELETE' }),
  accessJob: (id: number) =>
    request<LinkAccess>(`/jobs/${id}/access`, { method: 'POST' }),
  recordLinkAccess: (data: {
    url: string; job_id?: number; search_id?: number; link_type?: string
    title?: string; company?: string; source?: string; origin?: string
  }) => request<LinkAccess>('/link-accesses', { method: 'POST', body: JSON.stringify(data) }),
  getLinkAccesses: (params?: { search?: string; link_type?: string; source?: string; page?: number; page_size?: number }) => {
    const qs = new URLSearchParams()
    if (params?.search) qs.set('search', params.search)
    if (params?.link_type) qs.set('link_type', params.link_type)
    if (params?.source) qs.set('source', params.source)
    if (params?.page) qs.set('page', String(params.page))
    if (params?.page_size) qs.set('page_size', String(params.page_size))
    return request<LinkAccessPage>(`/link-accesses?${qs}`)
  },
  deleteLinkAccess: (id: number) => request<void>(`/link-accesses/${id}`, { method: 'DELETE' }),
  clearLinkAccesses: () => request<void>('/link-accesses', { method: 'DELETE' }),

  // Search history
  getSearchHistory: (limit = 50) =>
    request<SearchHistory[]>(`/searches?limit=${limit}`),

  // Saved filters
  getSavedFilters: () => request<SavedFilter[]>('/saved-filters'),
  createSavedFilter: (name: string, filters: SearchFilters) =>
    request<SavedFilter>('/saved-filters', {
      method: 'POST',
      body: JSON.stringify({ name, filters }),
    }),
  deleteSavedFilter: (id: number) =>
    request<void>(`/saved-filters/${id}`, { method: 'DELETE' }),

  // Health
  health: () =>
    request<{ status: string; sources: string[]; manual_sources: string[] }>('/health'),

  // Dashboard
  getDashboard: () => request<DashboardData>('/dashboard'),

  // Roles
  getRoles: (params?: { active?: boolean; category?: string; search?: string }) => {
    const qs = new URLSearchParams()
    if (params?.active != null) qs.set('active', String(params.active))
    if (params?.category) qs.set('category', params.category)
    if (params?.search) qs.set('search', params.search)
    return request<Role[]>(`/roles?${qs}`)
  },
  getRole: (id: number) => request<Role>(`/roles/${id}`),
  createRole: (data: Omit<Role, 'id' | 'created_at' | 'updated_at'>) =>
    request<Role>('/roles', { method: 'POST', body: JSON.stringify(data) }),
  updateRole: (id: number, data: Partial<Omit<Role, 'id' | 'created_at' | 'updated_at'>>) =>
    request<Role>(`/roles/${id}`, { method: 'PATCH', body: JSON.stringify(data) }),
  deleteRole: (id: number) =>
    request<void>(`/roles/${id}`, { method: 'DELETE' }),

  // Skills
  getSkills: (params?: { active?: boolean; category?: string; search?: string }) => {
    const qs = new URLSearchParams()
    if (params?.active != null) qs.set('active', String(params.active))
    if (params?.category) qs.set('category', params.category)
    if (params?.search) qs.set('search', params.search)
    return request<Skill[]>(`/skills?${qs}`)
  },
  getSkill: (id: number) => request<Skill>(`/skills/${id}`),
  createSkill: (data: Omit<Skill, 'id' | 'created_at' | 'updated_at'>) =>
    request<Skill>('/skills', { method: 'POST', body: JSON.stringify(data) }),
  updateSkill: (id: number, data: Partial<Omit<Skill, 'id' | 'created_at' | 'updated_at'>>) =>
    request<Skill>(`/skills/${id}`, { method: 'PATCH', body: JSON.stringify(data) }),
  deleteSkill: (id: number) =>
    request<void>(`/skills/${id}`, { method: 'DELETE' }),

  // Stacks
  getStacks: () => request<Stack[]>('/stacks'),
  createStack: (data: Omit<Stack, 'id' | 'created_at' | 'updated_at'>) =>
    request<Stack>('/stacks', { method: 'POST', body: JSON.stringify(data) }),
  updateStack: (id: number, data: Partial<Omit<Stack, 'id' | 'created_at' | 'updated_at'>>) =>
    request<Stack>(`/stacks/${id}`, { method: 'PATCH', body: JSON.stringify(data) }),
  deleteStack: (id: number) =>
    request<void>(`/stacks/${id}`, { method: 'DELETE' }),

  // Search Profiles
  getProfiles: () => request<SearchProfile[]>('/search-profiles'),
  getProfile: (id: number) => request<SearchProfile>(`/search-profiles/${id}`),
  createProfile: (data: Omit<SearchProfile, 'id' | 'created_at' | 'updated_at'>) =>
    request<SearchProfile>('/search-profiles', { method: 'POST', body: JSON.stringify(data) }),
  updateProfile: (id: number, data: Partial<Omit<SearchProfile, 'id' | 'created_at' | 'updated_at'>>) =>
    request<SearchProfile>(`/search-profiles/${id}`, { method: 'PATCH', body: JSON.stringify(data) }),
  deleteProfile: (id: number) =>
    request<void>(`/search-profiles/${id}`, { method: 'DELETE' }),
  executeProfile: (id: number) =>
    request<SearchResult>(`/search-profiles/${id}/execute`, { method: 'POST' }),

  // Sources
  getSources: (params?: { active?: boolean }) => {
    const qs = new URLSearchParams()
    if (params?.active != null) qs.set('active', String(params.active))
    return request<Source[]>(`/sources?${qs}`)
  },
  createSource: (data: Omit<Source, 'id' | 'created_at' | 'updated_at' | 'last_run' | 'last_error'>) =>
    request<Source>('/sources', { method: 'POST', body: JSON.stringify(data) }),
  updateSource: (id: number, data: Partial<Omit<Source, 'id' | 'created_at' | 'updated_at'>>) =>
    request<Source>(`/sources/${id}`, { method: 'PATCH', body: JSON.stringify(data) }),
  deleteSource: (id: number) =>
    request<void>(`/sources/${id}`, { method: 'DELETE' }),
}
