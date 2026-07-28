import { useCallback, useEffect, useState } from 'react'
import { Copy, ExternalLink, Eye, Search, Trash2 } from 'lucide-react'
import { api } from '../services/api'
import type { LinkAccessPage } from '../types'
import { Button } from '../components/ui/Button'
import { EmptyState } from '../components/ui/EmptyState'
import { PageHeader } from '../components/ui/PageHeader'

export default function AccessedLinks() {
  const [data, setData] = useState<LinkAccessPage>({ items: [], total: 0, page: 1, page_size: 25 })
  const [query, setQuery] = useState('')
  const [type, setType] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const load = useCallback(async (page = 1) => {
    setLoading(true)
    try {
      setData(await api.getLinkAccesses({ search: query || undefined, link_type: type || undefined, page, page_size: 25 }))
      setError('')
    } catch (e) { setError(e instanceof Error ? e.message : String(e)) }
    finally { setLoading(false) }
  }, [query, type])
  useEffect(() => { void load() }, [load])
  const remove = async (id: number) => {
    if (!confirm('Remover este item do histórico? A vaga salva não será excluída.')) return
    await api.deleteLinkAccess(id); await load(data.page)
  }
  const clear = async () => {
    if (!confirm('Limpar todo o histórico? As vagas salvas serão preservadas.')) return
    await api.clearLinkAccesses(); await load()
  }
  return <div className="space-y-4 max-w-5xl">
    <PageHeader title="Links acessados" description={`${data.total} links abertos pelo Job Radar`} action={data.total ? <Button variant="outline" size="sm" onClick={clear}><Trash2 size={14}/>Limpar histórico</Button> : undefined}/>
    <div className="flex flex-wrap gap-2">
      <div className="relative"><Search size={14} className="absolute left-3 top-2.5 text-zinc-500"/><input aria-label="Pesquisar links" value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Título, empresa ou URL…" className="h-9 w-64 rounded-md border border-zinc-700 bg-zinc-900 pl-9 pr-3 text-sm"/></div>
      <select aria-label="Filtrar tipo" value={type} onChange={(e) => setType(e.target.value)} className="h-9 rounded-md border border-zinc-700 bg-zinc-900 px-3 text-sm text-zinc-300"><option value="">Todos os tipos</option><option value="job">Vagas</option><option value="hiring_post">Posts</option><option value="career_page">Carreiras</option><option value="manual_search">Pesquisas externas</option></select>
    </div>
    {error && <p className="rounded-md border border-red-900 bg-red-950/40 p-3 text-sm text-red-300">{error}</p>}
    {loading ? <div className="py-12 text-center text-sm text-zinc-500">Carregando histórico…</div> : !data.items.length ? <EmptyState icon={<Eye size={36}/>} title="Nenhum link acessado" description="Os links abertos pelo Job Radar aparecerão aqui."/> :
      <div className="overflow-hidden rounded-lg border border-zinc-800">{data.items.map((item) => <div key={item.id} className="flex items-start gap-3 border-b border-zinc-800 px-4 py-3 last:border-0">
        <Eye size={15} className="mt-0.5 shrink-0 text-indigo-400"/><div className="min-w-0 flex-1"><p className="truncate text-sm font-medium text-zinc-100">{item.title || item.original_url}</p><p className="truncate text-xs text-zinc-500">{item.company || 'Empresa não informada'} · {item.source || item.link_type}</p><p className="mt-1 text-xs text-zinc-600">Último acesso: {new Date(item.last_accessed_at).toLocaleString('pt-BR')} · {item.access_count} acesso(s)</p></div>
        <button aria-label="Copiar link" onClick={() => void navigator.clipboard.writeText(item.original_url)} className="p-2 text-zinc-500 hover:text-white"><Copy size={14}/></button>
        <a aria-label="Abrir novamente" href={item.original_url} target="_blank" rel="noopener noreferrer" onClick={() => void api.recordLinkAccess({ url: item.original_url, job_id: item.job_id || undefined, title: item.title || undefined, company: item.company || undefined, source: item.source || undefined, link_type: item.link_type, origin: 'access_history' })} className="p-2 text-indigo-400"><ExternalLink size={14}/></a>
        <button aria-label="Remover" onClick={() => void remove(item.id)} className="p-2 text-zinc-500 hover:text-red-400"><Trash2 size={14}/></button>
      </div>)}</div>}
    {data.total > data.page_size && <div className="flex justify-end gap-2"><Button variant="outline" size="sm" disabled={data.page <= 1} onClick={() => void load(data.page - 1)}>Anterior</Button><span className="self-center text-xs text-zinc-500">Página {data.page}</span><Button variant="outline" size="sm" disabled={data.page * data.page_size >= data.total} onClick={() => void load(data.page + 1)}>Próxima</Button></div>}
  </div>
}
