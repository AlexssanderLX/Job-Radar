import { AlertTriangle } from 'lucide-react'
import type { SearchResult } from '../types'
import { SOURCE_LABELS } from '../utils/constants'

interface Props {
  result: SearchResult
  sortKey: string
  onSortChange: (k: string) => void
  minScore: number
  onMinScoreChange: (v: number) => void
  showFavoritesOnly: boolean
  onFavoritesToggle: () => void
}

export function ResultsBar({
  result, sortKey, onSortChange, minScore, onMinScoreChange,
  showFavoritesOnly, onFavoritesToggle
}: Props) {
  return (
    <div className="space-y-3">
      {/* Stats */}
      <div className="flex flex-wrap gap-x-4 gap-y-1 text-sm text-gray-500 dark:text-gray-400">
        <span><strong className="text-gray-900 dark:text-gray-100">{result.total_deduplicated}</strong> vagas</span>
        <span>{result.total_raw} coletadas, {result.total_raw - result.total_deduplicated} duplicatas removidas</span>
        <span>Duração: {result.duration_seconds.toFixed(1)}s</span>
        {result.sources_searched.length > 0 && (
          <span>
            Fontes: {result.sources_searched.map((s) => SOURCE_LABELS[s] ?? s).join(', ')}
          </span>
        )}
      </div>

      {/* Failed sources warning */}
      {result.sources_failed.length > 0 && (
        <div className="flex items-center gap-2 px-3 py-2 bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-700 rounded-lg text-xs text-amber-700 dark:text-amber-300">
          <AlertTriangle size={14} />
          Fontes que falharam: {result.sources_failed.map((s) => SOURCE_LABELS[s] ?? s).join(', ')}
        </div>
      )}

      {/* Controls */}
      <div className="flex flex-wrap gap-2 items-center">
        <div className="flex items-center gap-1.5">
          <label className="text-xs text-gray-500">Ordenar por:</label>
          <select
            value={sortKey}
            onChange={(e) => onSortChange(e.target.value)}
            className="text-xs border border-gray-300 dark:border-gray-600 rounded-md px-2 py-1 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
          >
            <option value="match_score">Maior compatibilidade</option>
            <option value="published_at">Mais recentes</option>
            <option value="company">Empresa</option>
            <option value="title">Título</option>
            <option value="source">Fonte</option>
          </select>
        </div>

        <div className="flex items-center gap-1.5">
          <label className="text-xs text-gray-500">Compatibilidade mín.:</label>
          <select
            value={minScore}
            onChange={(e) => onMinScoreChange(Number(e.target.value))}
            className="text-xs border border-gray-300 dark:border-gray-600 rounded-md px-2 py-1 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
          >
            <option value={0}>Todas</option>
            <option value={30}>≥ 30</option>
            <option value={50}>≥ 50</option>
            <option value={70}>≥ 70</option>
          </select>
        </div>

        <button
          onClick={onFavoritesToggle}
          className={`px-3 py-1 text-xs rounded-md border transition-colors ${
            showFavoritesOnly
              ? 'bg-pink-50 border-pink-400 text-pink-600 dark:bg-pink-900/30 dark:border-pink-700 dark:text-pink-300'
              : 'border-gray-300 dark:border-gray-600 text-gray-500 dark:text-gray-400 hover:border-pink-400'
          }`}
        >
          ♥ Favoritas
        </button>
      </div>
    </div>
  )
}
