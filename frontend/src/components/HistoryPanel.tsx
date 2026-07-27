import { X } from 'lucide-react'
import type { SearchHistory } from '../types'
import { SOURCE_LABELS } from '../utils/constants'

interface Props {
  history: SearchHistory[]
  onClose: () => void
  onReload: (filters: SearchHistory['filters']) => void
}

function summarize(filters: Record<string, unknown>) {
  const roles = Array.isArray(filters.roles) ? filters.roles.filter((value): value is string => typeof value === 'string') : []
  const levels = Array.isArray(filters.levels) ? filters.levels.filter((value): value is string => typeof value === 'string') : []
  const legacyRole = typeof filters.role === 'string' ? filters.role : ''
  return `${roles.join(', ') || legacyRole || 'Pesquisa'}${levels.length ? ` · ${levels.join(', ')}` : ''}`
}

export function HistoryPanel({ history, onClose, onReload }: Props) {
  return <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
    <div className="flex max-h-[80vh] w-full max-w-xl flex-col rounded-xl border border-zinc-700 bg-zinc-900 shadow-xl">
      <div className="flex items-center justify-between border-b border-zinc-800 px-5 py-4"><h2 className="font-semibold text-zinc-100">Histórico de pesquisas</h2><button aria-label="Fechar histórico" onClick={onClose} className="text-zinc-400 hover:text-white"><X size={18}/></button></div>
      <div className="flex-1 divide-y divide-zinc-800 overflow-y-auto">
        {!history.length && <p className="p-5 text-center text-sm text-zinc-500">Nenhuma pesquisa realizada ainda.</p>}
        {history.map((item) => <div key={item.id} className="flex items-start justify-between gap-3 px-5 py-3">
          <div><p className="text-sm font-medium text-zinc-200">{summarize(item.filters)}</p><p className="mt-0.5 text-xs text-zinc-500">{new Date(item.searched_at).toLocaleString('pt-BR')} · {item.total_found} vagas · {item.duration_seconds.toFixed(1)}s</p>{item.sources_failed.length > 0 && <p className="mt-1 text-xs text-amber-500">Falha: {item.sources_failed.map((source) => SOURCE_LABELS[source] ?? source).join(', ')}</p>}</div>
          <button onClick={() => { onReload(item.filters); onClose() }} className="shrink-0 rounded-md border border-indigo-800 px-3 py-1 text-xs text-indigo-300 hover:bg-indigo-950">Reutilizar</button>
        </div>)}
      </div>
    </div>
  </div>
}
