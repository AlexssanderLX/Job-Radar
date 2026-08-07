import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Briefcase, Star, Eye, EyeOff, SendHorizontal, Search,
  BookMarked, Globe, TrendingUp, Plus, Clock,
} from 'lucide-react'
import { api } from '../services/api'
import type { DashboardData } from '../types'
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card'
import { Button } from '../components/ui/Button'
import { Badge } from '../components/ui/Badge'
import { PageHeader } from '../components/ui/PageHeader'
import { SOURCE_LABELS } from '../utils/constants'

function ScoreColor(score: number): 'success' | 'warning' | 'secondary' {
  if (score >= 70) return 'success'
  if (score >= 40) return 'warning'
  return 'secondary'
}

function StatCard({ icon: Icon, label, value, color }: {
  icon: React.ElementType
  label: string
  value: number
  color: string
}) {
  return (
    <div className="flex items-center gap-4 border-y border-zinc-800 px-1 py-5">
      <div className={`p-2 ${color}`}>
        <Icon size={16} className="text-current" />
      </div>
      <div>
        <p className="text-2xl font-bold text-zinc-100">{value.toLocaleString('pt-BR')}</p>
        <p className="text-xs text-zinc-400">{label}</p>
      </div>
    </div>
  )
}

export default function Dashboard() {
  const navigate = useNavigate()
  const [data, setData] = useState<DashboardData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    api.getDashboard()
      .then(setData)
      .catch((e: Error) => setError(e.message))
      .finally(() => setLoading(false))
  }, [])

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="w-6 h-6 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="p-4 rounded-lg border border-red-800/50 bg-red-950/30 text-red-400 text-sm">
        Erro ao carregar dashboard: {error}
        <br />
        <span className="text-xs text-red-500">Verifique se o backend está rodando em localhost:8010</span>
      </div>
    )
  }

  const d = data!

  return (
    <div className="space-y-8 max-w-7xl">
      <PageHeader
        title="Dashboard"
        description="Visão geral do Job Radar"
        action={
          <Button onClick={() => navigate('/search')} size="sm">
            <Plus size={14} /> Nova pesquisa
          </Button>
        }
      />

      {/* Stats Grid */}
      <div className="grid grid-cols-2 gap-x-6 gap-y-3 lg:grid-cols-5">
        <StatCard icon={Briefcase} label="Total de vagas" value={d.total_jobs} color="bg-zinc-800 text-zinc-300" />
        <StatCard icon={TrendingUp} label="Novas" value={d.new_jobs} color="bg-indigo-900/50 text-indigo-400" />
        <StatCard icon={Star} label="Favoritas" value={d.favorite_jobs} color="bg-yellow-900/50 text-yellow-400" />
        <StatCard icon={EyeOff} label="Ocultadas" value={d.hidden_jobs} color="bg-zinc-800 text-zinc-500" />
        <StatCard icon={SendHorizontal} label="Candidaturas" value={d.applied_jobs} color="bg-green-900/50 text-green-400" />
        <StatCard icon={Search} label="Pesquisas" value={d.searches_count} color="bg-blue-900/50 text-blue-400" />
        <StatCard icon={BookMarked} label="Perfis ativos" value={d.profiles_count} color="bg-purple-900/50 text-purple-400" />
        <StatCard icon={Globe} label="Fontes ativas" value={d.sources_count} color="bg-orange-900/50 text-orange-400" />
        <StatCard icon={Eye} label="Links acessados" value={d.accessed_links} color="bg-sky-900/50 text-sky-400" />
        <StatCard icon={Briefcase} label="Vagas acessadas" value={d.accessed_jobs} color="bg-cyan-900/50 text-cyan-400" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Recent jobs */}
        <div className="lg:col-span-2">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>Últimas vagas</CardTitle>
                <Button variant="ghost" size="sm" onClick={() => navigate('/jobs')}>Ver todas</Button>
              </div>
            </CardHeader>
            <CardContent className="p-0">
              {d.recent_jobs.length === 0 ? (
                <p className="px-4 py-6 text-sm text-zinc-500 text-center">Nenhuma vaga ainda. Faça uma pesquisa.</p>
              ) : (
                <div className="divide-y divide-zinc-800">
                  {d.recent_jobs.map((job) => (
                    <div key={job.id} className="flex items-start gap-3 px-4 py-2.5 hover:bg-zinc-800/30 transition-colors">
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-zinc-200 truncate">{job.title}</p>
                        <p className="text-xs text-zinc-500 truncate">{job.company}</p>
                      </div>
                      {!job.is_manual && (
                        <Badge variant={ScoreColor(job.match_score)}>
                          {Math.round(job.match_score)}
                        </Badge>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Right column */}
        <div className="space-y-4">
          {/* Top matches */}
          <Card>
            <CardHeader>
              <CardTitle>Maior compatibilidade</CardTitle>
            </CardHeader>
            <CardContent className="p-0">
              {d.top_jobs.length === 0 ? (
                <p className="px-4 py-4 text-sm text-zinc-500 text-center">Sem dados</p>
              ) : (
                <div className="divide-y divide-zinc-800">
                  {d.top_jobs.map((job) => (
                    <div key={job.id} className="flex items-center gap-2 px-4 py-2">
                      <Badge variant={ScoreColor(job.match_score)} className="shrink-0">
                        {Math.round(job.match_score)}
                      </Badge>
                      <span className="text-xs text-zinc-300 truncate">{job.title}</span>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          {/* By source */}
          {Object.keys(d.by_source).length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>Por fonte</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                {Object.entries(d.by_source).sort((a, b) => b[1] - a[1]).map(([src, count]) => (
                  <div key={src} className="flex items-center gap-2">
                    <span className="text-xs text-zinc-400 w-28 truncate">{SOURCE_LABELS[src] ?? src}</span>
                    <div className="flex-1 h-1.5 bg-zinc-800 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-indigo-600 rounded-full"
                        style={{ width: `${Math.min(100, (count / d.total_jobs) * 100)}%` }}
                      />
                    </div>
                    <span className="text-xs text-zinc-500 w-6 text-right">{count}</span>
                  </div>
                ))}
              </CardContent>
            </Card>
          )}

          {/* Recent searches */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>Pesquisas recentes</CardTitle>
                <Button variant="ghost" size="sm" onClick={() => navigate('/history')}>Ver</Button>
              </div>
            </CardHeader>
            <CardContent className="p-0">
              {d.recent_searches.length === 0 ? (
                <p className="px-4 py-4 text-sm text-zinc-500 text-center">Nenhuma pesquisa</p>
              ) : (
                <div className="divide-y divide-zinc-800">
                  {d.recent_searches.map((s) => {
                    const filters = s.filters as Record<string, unknown>
                    const roles = (filters.roles as string[] | undefined) ?? []
                    const role = roles[0] ?? (filters.role as string | undefined) ?? '—'
                    return (
                      <div key={s.id} className="flex items-center gap-2 px-4 py-2">
                        <Clock size={12} className="text-zinc-600 shrink-0" />
                        <div className="flex-1 min-w-0">
                          <p className="text-xs text-zinc-300 truncate">{role}</p>
                          <p className="text-xs text-zinc-600">
                            {new Date(s.searched_at).toLocaleDateString('pt-BR')} · {s.total_found} vagas
                          </p>
                        </div>
                      </div>
                    )
                  })}
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Quick actions */}
      <div className="flex gap-2 flex-wrap">
        <Button variant="outline" size="sm" onClick={() => navigate('/search')}>
          <Search size={14} /> Nova pesquisa
        </Button>
        <Button variant="outline" size="sm" onClick={() => navigate('/profiles')}>
          <Plus size={14} /> Criar perfil
        </Button>
        <Button variant="outline" size="sm" onClick={() => navigate('/jobs?is_favorite=true')}>
          <Star size={14} /> Ver favoritas
        </Button>
        <Button variant="outline" size="sm" onClick={() => navigate('/accessed-links')}>
          <Eye size={14} /> Links acessados
        </Button>
      </div>
    </div>
  )
}
