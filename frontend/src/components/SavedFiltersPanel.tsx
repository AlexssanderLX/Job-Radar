import { X, Trash2 } from 'lucide-react'
import type { SavedFilter, SearchFilters } from '../types'

interface Props {
  filters: SavedFilter[]
  onLoad: (f: SearchFilters) => void
  onDelete: (id: number) => void
  onClose: () => void
}

export function SavedFiltersPanel({ filters, onLoad, onDelete, onClose }: Props) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40">
      <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 w-full max-w-md max-h-[70vh] flex flex-col shadow-xl">
        <div className="flex items-center justify-between px-5 py-4 border-b border-gray-100 dark:border-gray-700">
          <h2 className="font-semibold text-gray-900 dark:text-gray-100">Filtros salvos</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200">
            <X size={18} />
          </button>
        </div>
        <div className="overflow-y-auto flex-1 divide-y divide-gray-100 dark:divide-gray-700">
          {filters.length === 0 && (
            <p className="p-5 text-sm text-gray-500 text-center">Nenhum filtro salvo ainda.</p>
          )}
          {filters.map((sf) => (
            <div key={sf.id} className="px-5 py-3 flex items-center gap-3">
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-800 dark:text-gray-200 truncate">{sf.name}</p>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  {sf.filters.role} {sf.filters.levels?.length ? `· ${sf.filters.levels.join(', ')}` : ''}
                </p>
              </div>
              <button
                onClick={() => { onLoad(sf.filters); onClose() }}
                className="px-3 py-1 text-xs bg-indigo-50 dark:bg-indigo-900/30 text-indigo-600 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-700 rounded-md hover:bg-indigo-100"
              >
                Carregar
              </button>
              <button
                onClick={() => onDelete(sf.id)}
                className="text-gray-400 hover:text-red-500 dark:hover:text-red-400 transition-colors"
                aria-label="Excluir filtro"
              >
                <Trash2 size={14} />
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
