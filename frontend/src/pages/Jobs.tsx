import { useState, useEffect, useCallback } from 'react'
import { ExternalLink, Star, Eye, EyeOff, Search, ChevronDown, ChevronUp, ChevronLeft, ChevronRight, Trash2 } from 'lucide-react'
import { api } from '../services/api'
import type { Job } from '../types'
import { Button } from '../components/ui/Button'
import { Badge } from '../components/ui/Badge'
import { PageHeader } from '../components/ui/PageHeader'
import { EmptyState } from '../components/ui/EmptyState'
import { Dialog } from '../components/ui/Dialog'
import { SOURCE_LABELS } from '../utils/constants'

type StatusKey = 'new' | 'evaluating' | 'favorite' | 'applied' | 'interview' | 'rejected' | 'archived'

const STATUS_OPTIONS = [
  { value: '', label: 'Todos os status' },
  { value: 'new', label: 'Nova' },
  { value: 'evaluating', label: 'Avaliando' },
  { value: 'favorite', label: 'Favorita' },
  { value: 'applied', label: 'Candidatura enviada' },
  { value: 'interview', label: 'Entrevista' },
  { value: 'rejected', label: 'Rejeitado' },
  { value: 'archived', label: 'Arquivado' },
]

const PAGE_SIZE = 50

const STATUS_BADGE: Record<string, 'default' | 'secondary' | 'success' | 'warning' | 'destructive' | 'outline'> = {
  new: 'secondary',
  evaluating: 'default',
  favorite: 'warning',
  applied: 'success',
  interview: 'success',
  rejected: 'destructive',
  archived: 'outline',
}

const STATUS_LABELS: Record<string, string> = {
  new: 'Nova', evaluating: 'Avaliando', favorite: 'Favorita', applied: 'Candidatura',
  interview: 'Entrevista', rejected: 'Rejeitada', archived: 'Arquivada',
}

function scoreVariant(score: number): 'success' | 'warning' | 'secondary' {
  if (score >= 70) return 'success'
  if (score >= 40) return 'warning'
  return 'secondary'
}

function formatDate(iso: string | null): string {
  if (!iso) return '—'
  return new Date(iso).toLocaleDateString('pt-BR', { day: '2-digit', month: 'short', year: '2-digit' })
}

interface JobDetailDrawerProps {
  job: Job | null
  onClose: () => void
  onUpdate: (updated: Job) => void
  onAccess: (job: Job) => void
  onDelete: (job: Job) => void
}

function JobDetailDrawer({ job, onClose, onUpdate, onAccess, onDelete }: JobDetailDrawerProps) {
  const [notes, setNotes] = useState(job?.notes ?? '')
  const [status, setStatus] = useState(job?.status ?? 'new')
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    if (job) { setNotes(job.notes ?? ''); setStatus(job.status) }
  }, [job])

  const save = async () => {
    if (!job) return
    setSaving(true)
    try {
      const updated = await api.updateJob(job.id, { notes, status: status as StatusKey })
      onUpdate(updated)
      onClose()
    } finally {
      setSaving(false)
    }
  }

  if (!job) return null
  return (
    <Dialog open={!!job} onClose={onClose} title={job.title} size="lg">
      <div className="space-y-4">
        <div className="flex items-center gap-2 flex-wrap text-xs text-zinc-400">
          <span className="font-medium text-zinc-200">{job.company}</span>
          {job.location && <><span>·</span><span>{job.location}</span></>}
          {job.level && <><span>·</span><span>{job.level}</span></>}
          <span>·</span><span>{SOURCE_LABELS[job.source] ?? job.source}</span>
          {!job.is_manual && (
            <><span>·</span><Badge variant={scoreVariant(job.match_score)}>Score: {Math.round(job.match_score)}</Badge></>
          )}
        </div>

        {/* Status */}
        <div className="flex flex-col gap-1">
          <label className="text-xs font-medium text-zinc-400">Status</label>
          <select
            value={status}
            onChange={(e) => setStatus(e.target.value)}
            className="h-9 rounded-md border border-zinc-700 bg-zinc-900 px-3 text-sm text-zinc-100 focus:outline-none focus:ring-2 focus:ring-indigo-500"
          >
            {STATUS_OPTIONS.filter((s) => s.value).map((s) => (
              <option key={s.value} value={s.value}>{s.label}</option>
            ))}
          </select>
        </div>

        {/* Match breakdown */}
        {job.match_reasons.length > 0 && (
          <div>
            <p className="text-xs font-medium text-zinc-400 mb-1">Pontos positivos</p>
            <ul className="space-y-0.5">
              {job.match_reasons.map((r, i) => (
                <li key={i} className="text-xs text-green-400 flex items-center gap-1">
                  <span className="text-green-600">+</span>{r}
                </li>
              ))}
            </ul>
          </div>
        )}
        {job.match_penalties.length > 0 && (
          <div>
            <p className="text-xs font-medium text-zinc-400 mb-1">Penalidades</p>
            <ul className="space-y-0.5">
              {job.match_penalties.map((p, i) => (
                <li key={i} className="text-xs text-red-400 flex items-center gap-1">
                  <span className="text-red-600">−</span>{p}
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Description */}
        {job.description && (
          <div>
            <p className="text-xs font-medium text-zinc-400 mb-1">Descrição</p>
            <p className="text-xs text-zinc-400 whitespace-pre-wrap max-h-40 overflow-y-auto">{job.description}</p>
          </div>
        )}

        {/* Technologies */}
        {job.technologies.length > 0 && (
          <div>
            <p className="text-xs font-medium text-zinc-400 mb-1">Tecnologias</p>
            <div className="flex flex-wrap gap-1">
              {job.technologies.map((t) => (
                <span key={t} className="text-xs px-1.5 py-0.5 bg-zinc-800 text-zinc-400 rounded border border-zinc-700">{t}</span>
              ))}
            </div>
          </div>
        )}

        {/* Notes */}
        <div className="flex flex-col gap-1">
          <label className="text-xs font-medium text-zinc-400">Notas</label>
          <textarea
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            rows={3}
            placeholder="Suas anotações sobre esta vaga..."
            className="w-full rounded-md border border-zinc-700 bg-zinc-900 px-3 py-2 text-sm text-zinc-100 placeholder-zinc-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 resize-none"
          />
        </div>

        <div className="flex items-center gap-2 justify-between pt-2">
          <a
            href={job.apply_url}
            target="_blank"
            rel="noopener noreferrer"
            onClick={() => onAccess(job)}
            className="inline-flex items-center gap-1.5 text-sm text-indigo-400 hover:text-indigo-300"
          >
            <ExternalLink size={14} /> Abrir vaga
          </a>
          <div className="flex gap-2">
            <Button variant="outline" size="sm" onClick={() => onDelete(job)}><Trash2 size={13}/>Excluir</Button>
            <Button variant="outline" size="sm" onClick={onClose}>Cancelar</Button>
            <Button size="sm" onClick={save} loading={saving}>Salvar</Button>
          </div>
        </div>
      </div>
    </Dialog>
  )
}

export default function Jobs() {
  const [jobs, setJobs] = useState<Job[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const [minScore, setMinScore] = useState(0)
  const [showFavorites, setShowFavorites] = useState(false)
  const [selectedJob, setSelectedJob] = useState<Job | null>(null)
  const [showFilters, setShowFilters] = useState(false)
  const [currentPage, setCurrentPage] = useState(1)

  const fetchJobs = useCallback(async () => {
    setLoading(true)
    try {
      const data = await api.getJobs({ is_hidden: false, limit: 500 })
      setJobs(data)
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e))
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { fetchJobs() }, [fetchJobs])

  const handleUpdate = useCallback((updated: Job) => {
    setJobs((prev) => prev.map((j) => (j.id === updated.id ? updated : j)))
  }, [])

  const handleFavorite = useCallback(async (id: number, current: boolean) => {
    try {
      const updated = await api.updateJob(id, { is_favorite: !current })
      handleUpdate(updated)
    } catch { /* ignore */ }
  }, [handleUpdate])

  const handleHide = useCallback(async (id: number) => {
    try {
      await api.updateJob(id, { is_hidden: true })
      setJobs((prev) => prev.filter((j) => j.id !== id))
    } catch { /* ignore */ }
  }, [])

  const handleAccess = useCallback((job: Job) => {
    const now = new Date().toISOString()
    const updated = {
      ...job, has_been_accessed: true, last_accessed_at: now,
      first_accessed_at: job.first_accessed_at ?? now, access_count: job.access_count + 1,
    }
    handleUpdate(updated)
    setSelectedJob((current) => current?.id === job.id ? updated : current)
    void api.accessJob(job.id).catch(() => setError('O link abriu, mas o acesso não pôde ser salvo.'))
  }, [handleUpdate])

  const handleDelete = useCallback(async (job: Job) => {
    if (!confirm(`Excluir a vaga "${job.title}" do banco local?`)) return
    try {
      await api.deleteJob(job.id)
      setJobs((prev) => prev.filter((item) => item.id !== job.id))
      setSelectedJob(null)
    } catch (e) { setError(e instanceof Error ? e.message : String(e)) }
  }, [])

  const handleClearJobs = useCallback(async () => {
    if (!confirm(`Apagar todas as ${jobs.length} vagas armazenadas? Cargos, fontes, perfis e histórico de links serão preservados.`)) return
    try {
      await api.clearJobs()
      setJobs([])
      setSelectedJob(null)
    } catch (e) { setError(e instanceof Error ? e.message : String(e)) }
  }, [jobs.length])

  const displayed = jobs.filter((j) => {
    if (j.is_hidden) return false
    if (showFavorites && !j.is_favorite) return false
    if (statusFilter && j.status !== statusFilter) return false
    if (!j.is_manual && j.match_score < minScore) return false
    if (search) {
      const s = search.toLowerCase()
      return j.title.toLowerCase().includes(s) || j.company.toLowerCase().includes(s)
    }
    return true
  })
  const pageCount = Math.max(1, Math.ceil(displayed.length / PAGE_SIZE))
  const pageJobs = displayed.slice((currentPage - 1) * PAGE_SIZE, currentPage * PAGE_SIZE)

  useEffect(() => { setCurrentPage(1) }, [search, statusFilter, minScore, showFavorites])
  useEffect(() => { setCurrentPage((page) => Math.min(page, pageCount)) }, [pageCount])

  return (
    <div className="space-y-6 w-full max-w-7xl">
      <PageHeader
        title="Vagas"
        description={`${jobs.length} vagas salvas`}
        action={<div className="flex gap-2">{jobs.length > 0 && <Button variant="outline" size="sm" onClick={handleClearJobs}><Trash2 size={13}/>Limpar vagas</Button>}<Button variant="outline" size="sm" onClick={fetchJobs} loading={loading}>Atualizar</Button></div>}
      />

      {/* Filters */}
      <div className="grid gap-3 xl:grid-cols-[minmax(260px,1.4fr)_minmax(180px,.75fr)_auto_auto]">
        <div className="relative min-w-0">
          <Search size={14} className="absolute left-2.5 top-1/2 -translate-y-1/2 text-zinc-500" />
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Buscar título, empresa..."
            className="h-12 w-full border border-zinc-800 bg-zinc-950 pl-10 pr-4 text-sm text-zinc-100 placeholder-zinc-600 focus:border-violet-600 focus:outline-none focus:ring-1 focus:ring-violet-600"
          />
        </div>
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="h-12 border border-zinc-800 bg-zinc-950 px-4 text-sm text-zinc-300 focus:border-violet-600 focus:outline-none"
        >
          {STATUS_OPTIONS.map((s) => <option key={s.value} value={s.value}>{s.label}</option>)}
        </select>
        <button
          onClick={() => setShowFavorites((v) => !v)}
          className={`h-12 px-5 text-sm border transition-colors ${showFavorites ? 'bg-violet-950/50 border-violet-700 text-violet-300' : 'border-zinc-800 text-zinc-400 hover:border-zinc-600 hover:text-zinc-100'}`}
        >
          <Star size={12} className="inline mr-1" />
          Favoritas
        </button>
        <button
          onClick={() => setShowFilters((v) => !v)}
          className="h-12 px-5 text-sm border border-zinc-800 text-zinc-400 hover:border-zinc-600 hover:text-zinc-100"
        >
          {showFilters ? <ChevronUp size={12} className="inline mr-1" /> : <ChevronDown size={12} className="inline mr-1" />}
          Mais filtros
        </button>
      </div>

      {showFilters && (
        <div className="flex items-center gap-3 flex-wrap p-3 rounded-lg border border-zinc-800 bg-zinc-900/30">
          <label className="flex items-center gap-2 text-xs text-zinc-400">
            Score mínimo:
            <input type="range" min={0} max={100} step={5} value={minScore} onChange={(e) => setMinScore(Number(e.target.value))} className="w-24" />
            <span className="w-5">{minScore}</span>
          </label>
        </div>
      )}

      {error && (
        <div className="p-3 rounded-lg border border-red-800/50 bg-red-950/30 text-red-400 text-sm">{error}</div>
      )}

      {loading && (
        <div className="flex justify-center py-12">
          <div className="w-6 h-6 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
        </div>
      )}

      {!loading && displayed.length === 0 && (
        <EmptyState
          icon={<Search size={40} />}
          title="Nenhuma vaga"
          description="Faça uma pesquisa para encontrar vagas."
        />
      )}

      {!loading && displayed.length > 0 && (
        <div className="border-y border-zinc-800 overflow-hidden">
          <p className="px-1 py-3 text-xs text-zinc-500 border-b border-zinc-800">
            Mostrando {(currentPage - 1) * PAGE_SIZE + 1}–{Math.min(currentPage * PAGE_SIZE, displayed.length)} de {displayed.length} vaga(s)
            {displayed.length !== jobs.length && ` · ${jobs.length} salva(s) no total`}
          </p>
          <div className="hidden xl:grid grid-cols-[60px_130px_minmax(0,1fr)_auto] items-center gap-4 border-b border-zinc-800 px-1 py-3 text-[11px] font-semibold uppercase tracking-[0.12em] text-zinc-600">
            <span>Score</span><span>Status / nível</span><span>Vaga · empresa / fonte · publicada em</span><span className="pr-3">Ações</span>
          </div>
          <div>
            {pageJobs.map((job) => (
              <div
                key={job.id}
                className="grid grid-cols-[48px_minmax(0,1fr)] gap-3 border-b border-zinc-800 px-1 py-5 transition-colors last:border-0 hover:bg-zinc-900/40 xl:grid-cols-[60px_130px_minmax(0,1fr)_auto] xl:items-center xl:gap-4"
                onClick={() => setSelectedJob(job)}
              >
                {!job.is_manual && (
                  <div className="flex flex-col items-start gap-2">
                    <span className="text-xl font-bold tabular-nums text-zinc-100">{Math.round(job.match_score)}</span>
                    <span className={`h-2 w-2 rounded-full ${job.has_been_accessed ? 'bg-violet-500' : 'bg-emerald-500'}`} />
                  </div>
                )}
                <div className="hidden min-w-0 xl:block">
                  <div className="flex flex-col items-start gap-1.5">
                    <Badge variant={STATUS_BADGE[job.status] ?? 'secondary'} className="text-xs">
                      {STATUS_LABELS[job.status] ?? job.status}
                    </Badge>
                    <span className="text-xs text-zinc-400">{job.level || 'Não informado'}</span>
                  </div>
                </div>
                <div className="min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="text-base font-semibold text-zinc-100">{job.title}</span>
                    {job.has_been_accessed && <span className="inline-flex items-center gap-1 text-xs text-violet-400"><Eye size={11}/>Acessado</span>}
                  </div>
                  <p className="mt-1 text-sm text-zinc-500">{job.company} · {SOURCE_LABELS[job.source] ?? job.source} · {formatDate(job.published_at)}</p>
                  <div className="mt-2 flex gap-2 xl:hidden"><Badge variant={STATUS_BADGE[job.status] ?? 'secondary'}>{STATUS_LABELS[job.status] ?? job.status}</Badge>{job.level && <Badge variant="outline">{job.level}</Badge>}</div>
                </div>
                <div className="col-start-2 flex flex-wrap items-center gap-1 shrink-0 xl:col-start-auto xl:flex-nowrap" onClick={(e) => e.stopPropagation()}>
                  {!job.is_manual && (
                    <>
                      <button
                        onClick={() => handleFavorite(job.id, job.is_favorite)}
                        className={`p-1.5 rounded hover:bg-zinc-700 transition-colors ${job.is_favorite ? 'text-yellow-400' : 'text-zinc-600'}`}
                      >
                        <Star size={13} fill={job.is_favorite ? 'currentColor' : 'none'} />
                      </button>
                      <button
                        onClick={() => handleHide(job.id)}
                        className="p-1.5 rounded hover:bg-zinc-700 text-zinc-600 hover:text-zinc-400 transition-colors"
                      >
                        <EyeOff size={13} />
                      </button>
                      <button aria-label={`Excluir ${job.title}`} onClick={() => void handleDelete(job)} className="p-1.5 rounded hover:bg-red-950/40 text-zinc-600 hover:text-red-400 transition-colors"><Trash2 size={13}/></button>
                    </>
                  )}
                  <a
                    href={job.apply_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="ml-2 inline-flex h-10 items-center gap-2 bg-violet-600 px-4 text-sm font-medium text-white transition-colors hover:bg-violet-500"
                    onClick={(e) => e.stopPropagation()}
                    onMouseDown={() => handleAccess(job)}
                  >
                    Abrir vaga<ExternalLink size={15} />
                  </a>
                </div>
              </div>
            ))}
          </div>
          {pageCount > 1 && (
            <nav aria-label="Paginação de vagas" className="flex flex-wrap items-center justify-center gap-2 border-t border-zinc-800 px-4 py-5">
              <Button variant="outline" size="sm" disabled={currentPage === 1} onClick={() => setCurrentPage((page) => page - 1)}>
                <ChevronLeft size={15}/>Anterior
              </Button>
              {Array.from({ length: pageCount }, (_, index) => index + 1).map((page) => (
                <button
                  key={page}
                  type="button"
                  aria-label={`Ir para página ${page}`}
                  aria-current={currentPage === page ? 'page' : undefined}
                  onClick={() => setCurrentPage(page)}
                  className={`h-8 min-w-8 border px-2 text-sm font-medium transition-colors ${currentPage === page ? 'border-violet-500 bg-violet-600 text-white' : 'border-zinc-800 text-zinc-400 hover:border-zinc-600 hover:text-zinc-100'}`}
                >
                  {page}
                </button>
              ))}
              <Button variant="outline" size="sm" disabled={currentPage === pageCount} onClick={() => setCurrentPage((page) => page + 1)}>
                Próxima<ChevronRight size={15}/>
              </Button>
            </nav>
          )}
        </div>
      )}

      <JobDetailDrawer
        job={selectedJob}
        onClose={() => setSelectedJob(null)}
        onUpdate={handleUpdate}
        onAccess={handleAccess}
        onDelete={(job) => void handleDelete(job)}
      />
    </div>
  )
}
