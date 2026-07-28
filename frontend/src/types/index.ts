export interface SearchFilters {
  roles: string[]
  role?: string | null
  levels: string[]
  technologies: string[]
  location: string | null
  location_mode: string
  remote: boolean
  days_ago: number | null
  required_words: string[]
  excluded_words: string[]
  include_unlevel: boolean
  accept_international: boolean
  sources: string[]
  max_results: number
  strategy?: string
}

export interface Job {
  id: number
  title: string
  company: string
  location: string | null
  modality: string | null
  level: string | null
  description: string | null
  technologies: string[]
  source: string
  url: string
  apply_url: string
  published_at: string | null
  collected_at: string
  match_score: number
  match_reasons: string[]
  match_penalties: string[]
  match_summary: string | null
  is_manual: boolean
  external_id: string | null
  first_seen_at: string
  last_seen_at: string
  is_favorite: boolean
  is_hidden: boolean
  applied: boolean
  notes: string | null
  status: string
  applied_at: string | null
  tags: string[]
  summary: string | null
  source_type: string
  result_type: string
  query_origin: string | null
  related_sources: string[]
  has_been_accessed: boolean
  first_accessed_at: string | null
  last_accessed_at: string | null
  access_count: number
}

export interface LinkAccess {
  id: number
  normalized_url: string
  original_url: string
  job_id: number | null
  search_id: number | null
  link_type: string
  title: string | null
  company: string | null
  source: string | null
  origin: string
  first_accessed_at: string
  last_accessed_at: string
  access_count: number
}

export interface LinkAccessPage {
  items: LinkAccess[]
  total: number
  page: number
  page_size: number
}

export interface SearchResult {
  search_id: number
  total_raw: number
  total_deduplicated: number
  sources_searched: string[]
  sources_failed: string[]
  duration_seconds: number
  jobs: Job[]
}

export interface SavedFilter {
  id: number
  name: string
  filters: SearchFilters
  created_at: string
  updated_at: string
}

export interface SearchHistory {
  id: number
  filters: Record<string, unknown>
  searched_at: string
  total_found: number
  sources_searched: string[]
  sources_failed: string[]
  duration_seconds: number
}

export type SortKey = 'match_score' | 'published_at' | 'company' | 'title' | 'source'

// New entity types
export interface Role {
  id: number
  name: string
  category: string | null
  description: string | null
  aliases: string[]
  excluded_words: string[]
  active: boolean
  created_at: string
  updated_at: string
}

export interface Skill {
  id: number
  name: string
  category: string | null
  description: string | null
  aliases: string[]
  active: boolean
  created_at: string
  updated_at: string
}

export interface Stack {
  id: number
  name: string
  description: string | null
  active: boolean
  skill_ids: number[]
  created_at: string
  updated_at: string
}

export interface SearchProfile {
  id: number
  name: string
  description: string | null
  roles: string[]
  levels: string[]
  skills_required: string[]
  skills_desired: string[]
  stacks: string[]
  location: string | null
  location_mode: string
  days_ago: number | null
  required_words: string[]
  excluded_words: string[]
  sources: string[]
  max_results: number
  include_unlevel: boolean
  strategy: string
  active: boolean
  created_at: string
  updated_at: string
}

export interface Source {
  id: number
  name: string
  display_name: string
  source_type: string
  is_manual: boolean
  active: boolean
  priority: number
  description: string | null
  last_run: string | null
  last_error: string | null
  created_at: string
  updated_at: string
}

export interface DashboardData {
  total_jobs: number
  new_jobs: number
  favorite_jobs: number
  hidden_jobs: number
  applied_jobs: number
  searches_count: number
  profiles_count: number
  sources_count: number
  recent_jobs: Job[]
  top_jobs: Job[]
  recent_searches: SearchHistory[]
  by_source: Record<string, number>
  by_level: Record<string, number>
}
