import { useState, useEffect, useCallback } from 'react'
import { useSearchParams } from 'react-router-dom'
import {
  Search as SearchIcon, ExternalLink, Star, EyeOff, ChevronDown, ChevronUp,
  X, RefreshCw, Eye,
} from 'lucide-react'
import { api } from '../services/api'
import type { Job, SearchFilters, SearchResult, Role, Skill, Source } from '../types'
import { Button } from '../components/ui/Button'
import { MultiSelect } from '../components/ui/MultiSelect'
import { Select } from '../components/ui/Select'
import { Input } from '../components/ui/Input'
import { Badge } from '../components/ui/Badge'
import { TagInput } from '../components/ui/TagInput'
import { PageHeader } from '../components/ui/PageHeader'
import { EmptyState } from '../components/ui/EmptyState'
import { DEFAULT_FILTERS, LEVEL_OPTIONS, LOCATION_MODE_OPTIONS, DAYS_OPTIONS, SOURCE_LABELS } from '../utils/constants'

type SortKey = 'match_score' | 'published_at' | 'company'

function scoreVariant(score: number): 'success' | 'warning' | 'secondary' {
  if (score >= 70) return 'success'
  if (score >= 40) return 'warning'
  return 'secondary'
}

function formatDate(iso: string | null): string {
  if (!iso) return '—'
  const d = new Date(iso)
  return d.toLocaleDateString('pt-BR', { day: '2-digit', month: 'short' })
}

function JobRow({ job, onFavorite, onHide, onAccess }: {
  job: Job
  onFavorite: (id: number, current: boolean) => void
  onHide: (id: number) => void
  onAccess: (job: Job) => void
}) {
  return (
    <div className="flex flex-col gap-2 px-4 py-3 hover:bg-zinc-800/30 transition-colors border-b border-zinc-800 last:border-0">
      <div className="flex items-start gap-3">
        {!job.is_manual && (
          <Badge variant={scoreVariant(job.match_score)} className="shrink-0 mt-0.5">
            {Math.round(job.match_score)}
          </Badge>
        )}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="text-sm font-medium text-zinc-100 truncate">{job.title}</span>
            {job.level && <Badge variant="outline" className="text-xs">{job.level}</Badge>}
            {job.modality === 'remote' && <Badge variant="secondary" className="text-xs">Remoto</Badge>}
            {job.has_been_accessed && <span className="inline-flex items-center gap-1 text-xs text-sky-400"><Eye size={11}/>Acessado</span>}
          </div>
          <div className="flex items-center gap-2 mt-0.5 text-xs text-zinc-400">
            <span className="font-medium">{job.company}</span>
            {job.location && <span className="text-zinc-600">·</span>}
            {job.location && <span className="truncate max-w-[180px]">{job.location}</span>}
            <span className="text-zinc-600">·</span>
            <span>{SOURCE_LABELS[job.source] ?? job.source}</span>
            <span className="text-zinc-600">·</span>
            <span>{formatDate(job.published_at)}</span>
          </div>
          {job.technologies.length > 0 && (
            <div className="flex flex-wrap gap-1 mt-1.5">
              {job.technologies.slice(0, 6).map((t) => (
                <span key={t} className="text-xs px-1.5 py-0.5 bg-zinc-800 text-zinc-400 rounded border border-zinc-700">{t}</span>
              ))}
              {job.technologies.length > 6 && (
                <span className="text-xs text-zinc-600">+{job.technologies.length - 6}</span>
              )}
            </div>
          )}
          {(job.summary || job.match_summary) && !job.is_manual && (
            <p className="text-xs text-zinc-500 mt-1 line-clamp-2">{job.summary || job.match_summary}</p>
          )}
          {job.is_manual && job.description && (
            <p className="text-xs text-zinc-500 mt-1">{job.description}</p>
          )}
        </div>
        <div className="flex items-center gap-1 shrink-0">
          {!job.is_manual && (
            <>
              <button
                onClick={() => onFavorite(job.id, job.is_favorite)}
                className={`p-1.5 rounded hover:bg-zinc-700 transition-colors ${job.is_favorite ? 'text-yellow-400' : 'text-zinc-600 hover:text-zinc-300'}`}
                title={job.is_favorite ? 'Remover favorito' : 'Favoritar'}
              >
                <Star size={14} fill={job.is_favorite ? 'currentColor' : 'none'} />
              </button>
              <button
                onClick={() => onHide(job.id)}
                className="p-1.5 rounded hover:bg-zinc-700 text-zinc-600 hover:text-zinc-300 transition-colors"
                title="Ocultar"
              >
                <EyeOff size={14} />
              </button>
            </>
          )}
          <a
            href={job.apply_url}
            target="_blank"
            rel="noopener noreferrer"
            onClick={() => onAccess(job)}
            className="inline-flex items-center gap-1 h-7 px-2 rounded text-xs text-indigo-400 hover:text-indigo-300 border border-indigo-800/50 hover:bg-indigo-900/20 transition-colors"
          >
            <ExternalLink size={12} />
            {job.is_manual ? 'Abrir' : SOURCE_LABELS[job.source] ?? 'Ver'}
          </a>
        </div>
      </div>
    </div>
  )
}

function SectionToggle({ label, open, onToggle }: { label: string; open: boolean; onToggle: () => void }) {
  return (
    <button
      type="button"
      onClick={onToggle}
      className="flex items-center gap-2 w-full text-xs font-semibold text-zinc-400 uppercase tracking-wider py-2 hover:text-zinc-200 transition-colors"
    >
      {open ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
      {label}
    </button>
  )
}

export default function SearchPage() {
  const [searchParams] = useSearchParams()
  const [filters, setFilters] = useState<SearchFilters>({ ...DEFAULT_FILTERS, roles: DEFAULT_FILTERS.roles ?? [] })
  const [result, setResult] = useState<SearchResult | null>(null)
  const [jobs, setJobs] = useState<Job[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [sortKey, setSortKey] = useState<SortKey>('match_score')
  const [minScore, setMinScore] = useState(0)
  const [showRefinement, setShowRefinement] = useState(false)
  const [showStrategy, setShowStrategy] = useState(false)
  const [resultType, setResultType] = useState<'all' | 'job' | 'hiring_post' | 'career_page'>('all')
  const [accessFilter, setAccessFilter] = useState<'all' | 'new' | 'accessed'>('all')
  const [visibleCount, setVisibleCount] = useState(25)

  const [roles, setRoles] = useState<Role[]>([])
  const [skills, setSkills] = useState<Skill[]>([])
  const [sources, setSources] = useState<Source[]>([])

  useEffect(() => {
    api.getRoles({ active: true }).then(setRoles).catch(() => {})
    api.getSkills({ active: true }).then(setSkills).catch(() => {})
    api.getSources({ active: true }).then(setSources).catch(() => {})
  }, [])

  // If navigated from a profile
  useEffect(() => {
    const profileRoles = searchParams.get('roles')
    if (profileRoles) {
      try {
        const parsed = JSON.parse(decodeURIComponent(profileRoles)) as string[]
        setFilters((f) => ({ ...f, roles: parsed }))
      } catch { /* ignore */ }
    }
  }, [searchParams])

  const roleOptions = roles.map((r) => ({ value: r.name, label: r.name }))
  const levelOptions = LEVEL_OPTIONS.map((l) => ({ value: l, label: l }))
  const skillOptions = skills.map((s) => ({ value: s.name, label: s.name }))
  const sourceOptions = sources.map((s) => ({ value: s.name, label: s.display_name }))

  const setFilter = <K extends keyof SearchFilters>(key: K, value: SearchFilters[K]) => {
    setFilters((f) => ({ ...f, [key]: value }))
  }

  const setLocationMode = (mode: string) => {
    setFilters((current) => ({
      ...current,
      location_mode: mode,
      location: ['brasil', 'brasil_internacional'].includes(mode) ? 'Brasil' : ['estado', 'cidade'].includes(mode) ? null : current.location,
    }))
  }

  const handleSearch = useCallback(async () => {
    if (filters.roles.length === 0) {
      setError('Selecione ao menos um cargo')
      return
    }
    setLoading(true)
    setError(null)
    try {
      const res = await api.search({ ...filters, role: filters.roles[0] ?? null })
      setResult(res)
      setJobs(res.jobs)
      setVisibleCount(25)
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e))
    } finally {
      setLoading(false)
    }
  }, [filters])

  const handleFavorite = useCallback(async (id: number, current: boolean) => {
    try {
      const updated = await api.updateJob(id, { is_favorite: !current })
      setJobs((prev) => prev.map((j) => (j.id === id ? { ...j, is_favorite: updated.is_favorite } : j)))
    } catch { /* non-critical */ }
  }, [])

  const handleHide = useCallback(async (id: number) => {
    try {
      await api.updateJob(id, { is_hidden: true })
      setJobs((prev) => prev.filter((j) => j.id !== id))
    } catch { /* non-critical */ }
  }, [])

  const handleAccess = useCallback((job: Job) => {
    const now = new Date().toISOString()
    setJobs((prev) => prev.map((item) => item.id === job.id ? {
      ...item, has_been_accessed: true, last_accessed_at: now,
      first_accessed_at: item.first_accessed_at ?? now, access_count: item.access_count + 1,
    } : item))
    void api.accessJob(job.id).catch(() => {
      setError('O link foi aberto, mas não foi possível registrar o acesso.')
    })
  }, [])

  const autoJobs = jobs.filter((j) => {
    if (j.is_manual || j.match_score < minScore) return false
    if (resultType !== 'all' && j.result_type !== resultType) return false
    if (accessFilter === 'new' && j.has_been_accessed) return false
    if (accessFilter === 'accessed' && !j.has_been_accessed) return false
    return true
  })
  const manualJobs = jobs.filter((j) => j.is_manual)
  const sortedAuto = [...autoJobs].sort((a, b) => {
    if (sortKey === 'match_score') return b.match_score - a.match_score
    if (sortKey === 'published_at') {
      return (new Date(b.published_at ?? 0).getTime()) - (new Date(a.published_at ?? 0).getTime())
    }
    return a.company.localeCompare(b.company, 'pt-BR')
  })
  const visibleJobs = sortedAuto.slice(0, visibleCount)

  // Active filters for the summary bar
  const activeFilters: Array<{ key: string; label: string; onRemove: () => void }> = []
  filters.roles.forEach((r) => activeFilters.push({ key: `role_${r}`, label: r, onRemove: () => setFilter('roles', filters.roles.filter((x) => x !== r)) }))
  filters.levels.forEach((l) => activeFilters.push({ key: `level_${l}`, label: l, onRemove: () => setFilter('levels', filters.levels.filter((x) => x !== l)) }))
  filters.technologies.forEach((t) => activeFilters.push({ key: `tech_${t}`, label: t, onRemove: () => setFilter('technologies', filters.technologies.filter((x) => x !== t)) }))

  const needsLocation = ['estado', 'cidade'].includes(filters.location_mode)

  return (
    <div className="space-y-6 max-w-7xl">
      <PageHeader title="Pesquisar vagas" description="Configure os filtros e execute a busca" />

      <div className="grid grid-cols-1 gap-8 lg:grid-cols-[320px,1fr]">
        {/* Filter panel */}
        <div className="space-y-4">
          <div className="border-y border-zinc-800 bg-zinc-950 p-5 space-y-5">
            {/* Section 1: Objetivo */}
            <div className="space-y-3">
              <p className="text-xs font-semibold text-zinc-400 uppercase tracking-wider">Objetivo</p>
              <MultiSelect
                label="Cargos"
                options={roleOptions}
                value={filters.roles}
                onChange={(v) => setFilter('roles', v)}
                placeholder="Selecionar cargos..."
              />
              <MultiSelect
                label="Níveis"
                options={levelOptions}
                value={filters.levels}
                onChange={(v) => setFilter('levels', v)}
                placeholder="Todos os níveis"
              />
              <Select
                label="Localização"
                value={filters.location_mode}
                onChange={(e) => setLocationMode(e.target.value)}
                options={LOCATION_MODE_OPTIONS}
              />
              {needsLocation && (
                <Input
                  label={filters.location_mode === 'estado' ? 'Estado (ex: SP)' : 'Cidade (ex: São Paulo)'}
                  value={filters.location ?? ''}
                  onChange={(e) => setFilter('location', e.target.value || null)}
                  placeholder={filters.location_mode === 'estado' ? 'São Paulo' : 'São Paulo, SP'}
                />
              )}
              <Select
                label="Período"
                value={filters.days_ago ?? ''}
                onChange={(e) => setFilter('days_ago', e.target.value ? Number(e.target.value) : null)}
                options={DAYS_OPTIONS.filter((d) => d.value !== null).map((d) => ({ value: d.value!, label: d.label }))}
                placeholder="Qualquer período"
              />
            </div>

            {/* Section 2: Habilidades */}
            <div className="pt-2 border-t border-zinc-800 space-y-3">
              <p className="text-xs font-semibold text-zinc-400 uppercase tracking-wider">Habilidades</p>
              <MultiSelect
                label="Tecnologias"
                options={skillOptions}
                value={filters.technologies}
                onChange={(v) => setFilter('technologies', v)}
                placeholder="Selecionar habilidades..."
              />
              {filters.technologies.length > 0 && <label className="flex flex-col gap-1 text-xs font-medium text-zinc-400">Mínimo de habilidades
                <select value={filters.min_skill_matches} onChange={(e) => setFilter('min_skill_matches', Number(e.target.value))} className="h-9 rounded-md border border-zinc-700 bg-zinc-900 px-3 text-sm text-zinc-100">
                  <option value={0}>Sem mínimo</option>
                  {filters.technologies.map((_, index) => <option key={index + 1} value={index + 1}>Pelo menos {index + 1}</option>)}
                </select>
              </label>}
            </div>

            {/* Section 3: Refinamento */}
            <div className="pt-2 border-t border-zinc-800">
              <SectionToggle label="Refinamento" open={showRefinement} onToggle={() => setShowRefinement((v) => !v)} />
              {showRefinement && (
                <div className="space-y-3 mt-2">
                  <TagInput
                    label="Palavras obrigatórias"
                    value={filters.required_words}
                    onChange={(v) => setFilter('required_words', v)}
                    placeholder="Adicionar..."
                  />
                  <TagInput
                    label="Palavras excluídas"
                    value={filters.excluded_words}
                    onChange={(v) => setFilter('excluded_words', v)}
                    placeholder="Adicionar..."
                  />
                  <label className="flex items-center gap-2 text-xs text-zinc-400 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={filters.include_unlevel}
                      onChange={(e) => setFilter('include_unlevel', e.target.checked)}
                      className="rounded border-zinc-600 bg-zinc-800 text-indigo-600"
                    />
                    Incluir vagas sem nível detectado
                  </label>
                  <MultiSelect
                    label="Fontes"
                    options={sourceOptions}
                    value={filters.sources}
                    onChange={(v) => setFilter('sources', v)}
                    placeholder="Todas as fontes"
                  />
                  <div className="flex flex-col gap-1">
                    <label className="text-xs font-medium text-zinc-400">Máximo de resultados</label>
                    <input
                      type="number"
                      min={10}
                      max={500}
                      value={filters.max_results}
                      onChange={(e) => setFilter('max_results', Number(e.target.value))}
                      className="h-9 w-full rounded-md border border-zinc-700 bg-zinc-900 px-3 text-sm text-zinc-100 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    />
                  </div>
                </div>
              )}
            </div>

            {/* Section 4: Estratégia */}
            <div className="border-t border-zinc-800">
              <SectionToggle label="Estratégia" open={showStrategy} onToggle={() => setShowStrategy((v) => !v)} />
              {showStrategy && (
                <div className="space-y-1.5 mt-2">
                  {(['exact', 'balanced', 'broad'] as const).map((s) => (
                    <label key={s} className="flex items-center gap-2 text-xs text-zinc-400 cursor-pointer">
                      <input
                        type="radio"
                        name="strategy"
                        value={s}
                        checked={filters.strategy === s}
                        onChange={() => setFilter('strategy', s)}
                        className="text-indigo-600"
                      />
                      <span>{s === 'exact' ? 'Exato' : s === 'balanced' ? 'Equilibrado' : 'Amplo'}</span>
                    </label>
                  ))}
                </div>
              )}
            </div>

            <Button onClick={handleSearch} loading={loading} className="w-full">
              <SearchIcon size={14} />
              {loading ? 'Pesquisando...' : 'Pesquisar vagas'}
            </Button>
          </div>
        </div>

        {/* Results */}
        <div className="space-y-3">
          {/* Active filters bar */}
          {activeFilters.length > 0 && (
            <div className="flex flex-wrap items-center gap-1.5">
              <span className="text-xs text-zinc-500">Filtros:</span>
              {activeFilters.map((af) => (
                <span
                  key={af.key}
                  className="inline-flex items-center gap-1 rounded border border-zinc-700 bg-zinc-800 px-2 py-0.5 text-xs text-zinc-300"
                >
                  {af.label}
                  <button onClick={af.onRemove} className="text-zinc-500 hover:text-zinc-200">
                    <X size={10} />
                  </button>
                </span>
              ))}
              <button
                onClick={() => setFilters({ ...DEFAULT_FILTERS, roles: [] })}
                className="text-xs text-zinc-500 hover:text-zinc-300"
              >
                Limpar todos
              </button>
            </div>
          )}

          {error && (
            <div className="p-3 rounded-lg border border-red-800/50 bg-red-950/30 text-red-400 text-sm">
              {error}
            </div>
          )}

          {loading && (
            <div className="space-y-2">
              {[...Array(5)].map((_, i) => (
                <div key={i} className="h-20 rounded-lg bg-zinc-800/50 animate-pulse" />
              ))}
            </div>
          )}

          {result && !loading && (
            <>
              <div className="flex items-center justify-between">
                <p className="text-xs text-zinc-400">
                  {autoJobs.length} vagas encontradas{manualJobs.length > 0 ? ` · ${manualJobs.length} pesquisas externas de apoio` : ''} · {result.duration_seconds.toFixed(1)}s
                  {result.sources_failed.length > 0 && (
                    <span className="text-yellow-500 ml-2">· {result.sources_failed.length} fonte(s) falharam</span>
                  )}
                </p>
                <div className="flex items-center gap-2">
                  <label className="text-xs text-zinc-400">Score mín:</label>
                  <input
                    type="range" min={0} max={100} step={5}
                    value={minScore}
                    onChange={(e) => setMinScore(Number(e.target.value))}
                    className="w-20"
                  />
                  <span className="text-xs text-zinc-400 w-6">{minScore}</span>
                  <Select
                    value={sortKey}
                    onChange={(e) => setSortKey(e.target.value as SortKey)}
                    options={[
                      { value: 'match_score', label: 'Score' },
                      { value: 'published_at', label: 'Data' },
                      { value: 'company', label: 'Empresa' },
                    ]}
                    className="h-7 text-xs"
                  />
                </div>
              </div>

              <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
                {result.source_progress.map((source) => (
                  <div key={source.source} className="flex items-center justify-between border-b border-zinc-800 px-1 py-3 text-xs">
                    <span className="text-zinc-300">{SOURCE_LABELS[source.source] ?? source.source}</span>
                    <span className={source.status === 'error' ? 'text-red-400' : source.status === 'empty' ? 'text-zinc-600' : source.status === 'manual' ? 'text-amber-400' : 'text-emerald-400'}>
                      {source.status === 'error' ? 'Erro' : source.status === 'manual' ? 'Manual' : `${source.result_count} resultado(s)`}
                    </span>
                  </div>
                ))}
              </div>

              <div className="flex flex-wrap gap-2">
                {([
                  ['all', 'Todas'], ['job', 'Vagas'], ['hiring_post', 'Posts'], ['career_page', 'Carreiras'],
                ] as const).map(([value, label]) => <button key={value} onClick={() => { setResultType(value); setVisibleCount(25) }} className={`rounded-md border px-2.5 py-1 text-xs ${resultType === value ? 'border-indigo-700 bg-indigo-950/50 text-indigo-300' : 'border-zinc-800 text-zinc-500'}`}>{label}</button>)}
                <select aria-label="Filtrar acessos" value={accessFilter} onChange={(e) => { setAccessFilter(e.target.value as typeof accessFilter); setVisibleCount(25) }} className="h-7 rounded-md border border-zinc-800 bg-zinc-900 px-2 text-xs text-zinc-400"><option value="all">Todos os acessos</option><option value="new">Ainda não acessadas</option><option value="accessed">Já acessadas</option></select>
              </div>

              {/* Auto jobs */}
              {sortedAuto.length > 0 && (
                <div className="border-y border-zinc-800 overflow-hidden">
                  <div className="flex items-center justify-between px-4 py-3 border-b border-zinc-800">
                    <span className="text-xs font-semibold text-zinc-300">Automático ({sortedAuto.length})</span>
                  </div>
                  {visibleJobs.map((job) => (
                    <JobRow key={job.id} job={job} onFavorite={handleFavorite} onHide={handleHide} onAccess={handleAccess} />
                  ))}
                </div>
              )}
              {visibleCount < sortedAuto.length && <div className="flex justify-center"><Button variant="outline" onClick={() => setVisibleCount((count) => count + 25)}>Carregar mais ({sortedAuto.length - visibleCount})</Button></div>}

              {/* Manual links */}
              {manualJobs.length > 0 && (
                <div className="rounded-lg border border-zinc-800 overflow-hidden">
                  <div className="px-4 py-2 bg-zinc-800/50 border-b border-zinc-800">
                    <div><span className="text-xs font-semibold text-zinc-300">Links de busca externa ({manualJobs.length})</span><p className="mt-0.5 text-xs text-zinc-600">Estes itens são atalhos de pesquisa, não vagas encontradas. Eles aparecem quando nenhuma vaga automática passa pelos filtros.</p></div>
                  </div>
                  <div className="divide-y divide-zinc-800/50">
                    {manualJobs.map((job) => (
                      <div key={job.id} className="flex items-center gap-3 px-4 py-2.5 hover:bg-zinc-800/20">
                        <div className="flex-1 min-w-0">
                           <p className="flex items-center gap-2 text-xs font-medium text-zinc-300 truncate">{job.title}{job.has_been_accessed && <span className="inline-flex items-center gap-1 text-sky-400"><Eye size={10}/>Acessado</span>}</p>
                          <p className="text-xs text-zinc-600 truncate">{job.description}</p>
                        </div>
                        <div className="flex gap-1">
                          <a
                            href={job.url}
                            target="_blank"
                             rel="noopener noreferrer"
                             onClick={() => handleAccess(job)}
                            className="inline-flex items-center gap-1 h-6 px-2 rounded text-xs text-indigo-400 border border-indigo-800/50 hover:bg-indigo-900/20"
                          >
                            <ExternalLink size={10} /> Abrir
                          </a>
                          <button
                            onClick={() => navigator.clipboard.writeText(job.url)}
                            className="h-6 px-2 rounded text-xs text-zinc-500 border border-zinc-800 hover:bg-zinc-800"
                          >
                            Copiar
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {sortedAuto.length === 0 && manualJobs.length === 0 && (
                <EmptyState
                  icon={<SearchIcon size={40} />}
                  title="Nenhuma vaga encontrada"
                  description="Tente ampliar os filtros, reduzir o score mínimo ou selecionar mais fontes."
                />
              )}
            </>
          )}

          {!result && !loading && !error && (
            <EmptyState
              icon={<RefreshCw size={40} />}
              title="Pronto para pesquisar"
              description="Configure os filtros no painel e clique em Pesquisar vagas."
            />
          )}
        </div>
      </div>
    </div>
  )
}
