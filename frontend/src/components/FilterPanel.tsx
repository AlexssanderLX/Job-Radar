import { useState } from 'react'
import { ChevronDown, ChevronUp, Plus, X, Info } from 'lucide-react'
import type { SearchFilters } from '../types'
import {
  ROLE_OPTIONS, LEVEL_OPTIONS, TECH_OPTIONS, DAYS_OPTIONS,
  LOCATION_MODE_OPTIONS, SOURCE_LABELS, DEFAULT_FILTERS,
} from '../utils/constants'

interface Props {
  filters: SearchFilters
  onChange: (f: SearchFilters) => void
  onSearch: () => void
  onClear: () => void
  onSave: () => void
  isLoading: boolean
}

function MultiSelect({
  label, options, selected, onToggle, hint,
}: {
  label: string; options: string[]; selected: string[]; onToggle: (v: string) => void; hint?: string
}) {
  return (
    <div>
      <div className="flex items-center gap-1.5 mb-1.5">
        <label className="text-xs font-medium text-gray-600 dark:text-gray-400">{label}</label>
        {hint && (
          <span title={hint} className="cursor-help text-gray-400 hover:text-gray-600">
            <Info size={11} />
          </span>
        )}
      </div>
      <div className="flex flex-wrap gap-1.5">
        {options.map((opt) => (
          <button
            key={opt}
            type="button"
            onClick={() => onToggle(opt)}
            className={`px-2.5 py-1 text-xs rounded-full border transition-colors ${
              selected.includes(opt)
                ? 'bg-indigo-600 border-indigo-600 text-white'
                : 'border-gray-300 dark:border-gray-600 text-gray-600 dark:text-gray-300 hover:border-indigo-400'
            }`}
          >
            {opt}
          </button>
        ))}
      </div>
    </div>
  )
}

function TagInput({
  label, tags, onAdd, onRemove, placeholder,
}: {
  label: string; tags: string[]; onAdd: (v: string) => void; onRemove: (v: string) => void; placeholder?: string
}) {
  const [input, setInput] = useState('')

  const handleKey = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if ((e.key === 'Enter' || e.key === ',') && input.trim()) {
      e.preventDefault()
      onAdd(input.trim())
      setInput('')
    }
  }

  return (
    <div>
      <label className="block text-xs font-medium text-gray-600 dark:text-gray-400 mb-1.5">{label}</label>
      {tags.length > 0 && (
        <div className="flex flex-wrap gap-1 mb-1.5">
          {tags.map((t) => (
            <span key={t} className="inline-flex items-center gap-1 px-2 py-0.5 bg-gray-100 dark:bg-gray-700 rounded text-xs">
              {t}
              <button onClick={() => onRemove(t)} className="hover:text-red-500"><X size={10} /></button>
            </span>
          ))}
        </div>
      )}
      <div className="flex gap-1">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKey}
          placeholder={placeholder ?? 'Digite e pressione Enter'}
          className="flex-1 px-2.5 py-1.5 text-xs border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
        />
        <button
          type="button"
          onClick={() => { if (input.trim()) { onAdd(input.trim()); setInput('') } }}
          className="p-1.5 border border-gray-300 dark:border-gray-600 rounded-md hover:bg-gray-50 dark:hover:bg-gray-700"
        >
          <Plus size={14} />
        </button>
      </div>
    </div>
  )
}

export function FilterPanel({ filters, onChange, onSearch, onClear: _onClear, onSave, isLoading }: Props) {
  const [advancedOpen, setAdvancedOpen] = useState(false)
  const [customRole, setCustomRole] = useState('')

  const set = <K extends keyof SearchFilters>(key: K, val: SearchFilters[K]) =>
    onChange({ ...filters, [key]: val })

  const setLocationMode = (mode: string) => {
    const isRemote = ['remoto_brasil', 'remoto_latam', 'remoto_global'].includes(mode)
    const isIntl = mode === 'internacional'
    const loc = (mode === 'brasil' || mode === 'internacional') ? 'Brasil' : filters.location
    onChange({
      ...filters,
      location_mode: mode,
      remote: isRemote,
      accept_international: isIntl,
      location: loc,
    })
  }

  const toggleMulti = (key: 'levels' | 'technologies' | 'sources', val: string) => {
    const arr = filters[key] as string[]
    set(key, arr.includes(val) ? arr.filter((x) => x !== val) : [...arr, val])
  }

  const addTag = (key: 'required_words' | 'excluded_words' | 'technologies') => (val: string) => {
    const arr = filters[key] as string[]
    if (!arr.includes(val)) set(key, [...arr, val])
  }

  const removeTag = (key: 'required_words' | 'excluded_words' | 'technologies') => (val: string) => {
    set(key, (filters[key] as string[]).filter((x) => x !== val))
  }

  const sourceOptions = Object.keys(SOURCE_LABELS)
  const needsLocationInput = ['estado', 'cidade'].includes(filters.location_mode)
  const locationModeLabel = LOCATION_MODE_OPTIONS.find(o => o.value === filters.location_mode)?.label ?? filters.location_mode

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-5 space-y-5">
      {/* Role */}
      <div>
        <label className="block text-xs font-medium text-gray-600 dark:text-gray-400 mb-1.5">Cargo</label>
        <div className="flex flex-wrap gap-1.5 mb-2">
          {ROLE_OPTIONS.map((r) => (
            <button
              key={r}
              type="button"
              onClick={() => set('role', r)}
              className={`px-2.5 py-1 text-xs rounded-full border transition-colors ${
                filters.role === r
                  ? 'bg-indigo-600 border-indigo-600 text-white'
                  : 'border-gray-300 dark:border-gray-600 text-gray-600 dark:text-gray-300 hover:border-indigo-400'
              }`}
            >
              {r}
            </button>
          ))}
        </div>
        <div className="flex gap-2">
          <input
            value={customRole}
            onChange={(e) => setCustomRole(e.target.value)}
            placeholder="Cargo personalizado..."
            className="flex-1 px-2.5 py-1.5 text-xs border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
            onKeyDown={(e) => {
              if (e.key === 'Enter' && customRole.trim()) {
                set('role', customRole.trim())
                setCustomRole('')
              }
            }}
          />
          <button
            type="button"
            onClick={() => { if (customRole.trim()) { set('role', customRole.trim()); setCustomRole('') } }}
            className="px-3 py-1.5 text-xs bg-indigo-600 text-white rounded-md hover:bg-indigo-700"
          >
            Usar
          </button>
        </div>
        {filters.role && !ROLE_OPTIONS.includes(filters.role) && (
          <p className="text-xs text-indigo-600 mt-1">Cargo personalizado: <strong>{filters.role}</strong></p>
        )}
      </div>

      {/* Levels */}
      <div>
        <MultiSelect
          label="Nível"
          options={LEVEL_OPTIONS}
          selected={filters.levels}
          onToggle={(v) => toggleMulti('levels', v)}
          hint="Filtro obrigatório — vagas com outros níveis são excluídas"
        />
        {filters.levels.length > 0 && (
          <label className="flex items-center gap-2 mt-2 cursor-pointer">
            <input
              type="checkbox"
              checked={filters.include_unlevel}
              onChange={(e) => set('include_unlevel', e.target.checked)}
              className="w-3.5 h-3.5 rounded accent-indigo-600"
            />
            <span className="text-xs text-gray-500 dark:text-gray-400">
              Incluir vagas sem nível detectado
            </span>
          </label>
        )}
      </div>

      {/* Technologies */}
      <div>
        <MultiSelect
          label="Tecnologias"
          options={TECH_OPTIONS}
          selected={filters.technologies}
          onToggle={(v) => toggleMulti('technologies', v)}
        />
        <div className="mt-2">
          <TagInput
            label=""
            tags={filters.technologies.filter((t) => !TECH_OPTIONS.includes(t))}
            onAdd={addTag('technologies')}
            onRemove={removeTag('technologies')}
            placeholder="Tecnologia personalizada..."
          />
        </div>
      </div>

      {/* Location mode + Period */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div>
          <label className="block text-xs font-medium text-gray-600 dark:text-gray-400 mb-1.5">
            Localização
          </label>
          <select
            value={filters.location_mode}
            onChange={(e) => setLocationMode(e.target.value)}
            className="w-full px-2.5 py-1.5 text-xs border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
          >
            {LOCATION_MODE_OPTIONS.map((o) => (
              <option key={o.value} value={o.value}>{o.label}</option>
            ))}
          </select>
          {needsLocationInput && (
            <input
              value={filters.location ?? ''}
              onChange={(e) => set('location', e.target.value)}
              placeholder={filters.location_mode === 'estado' ? 'Ex: São Paulo, MG...' : 'Ex: Campinas, Curitiba...'}
              className="mt-1.5 w-full px-2.5 py-1.5 text-xs border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
            />
          )}
          {!needsLocationInput && (
            <p className="mt-1 text-xs text-gray-400">{locationModeLabel}</p>
          )}
        </div>
        <div>
          <label className="block text-xs font-medium text-gray-600 dark:text-gray-400 mb-1.5">Período</label>
          <select
            value={filters.days_ago ?? ''}
            onChange={(e) => set('days_ago', e.target.value ? Number(e.target.value) : null)}
            className="w-full px-2.5 py-1.5 text-xs border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
          >
            {DAYS_OPTIONS.map((d) => (
              <option key={d.label} value={d.value ?? ''}>{d.label}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Advanced toggle */}
      <button
        type="button"
        onClick={() => setAdvancedOpen((v) => !v)}
        className="flex items-center gap-1 text-xs text-indigo-600 dark:text-indigo-400 hover:underline"
      >
        {advancedOpen ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
        {advancedOpen ? 'Ocultar opções avançadas' : 'Opções avançadas'}
      </button>

      {advancedOpen && (
        <div className="space-y-4 border-t border-gray-100 dark:border-gray-700 pt-4">
          <TagInput
            label="Palavras obrigatórias (filtro rígido)"
            tags={filters.required_words}
            onAdd={addTag('required_words')}
            onRemove={removeTag('required_words')}
            placeholder="Palavra que deve aparecer..."
          />
          <TagInput
            label="Palavras proibidas (filtro rígido no título)"
            tags={filters.excluded_words}
            onAdd={addTag('excluded_words')}
            onRemove={removeTag('excluded_words')}
            placeholder="Senior, Lead..."
          />
          <MultiSelect
            label="Fontes"
            options={sourceOptions}
            selected={filters.sources}
            onToggle={(v) => toggleMulti('sources', v)}
          />
          <div>
            <label className="block text-xs font-medium text-gray-600 dark:text-gray-400 mb-1.5">Máx. resultados</label>
            <input
              type="number"
              min={10}
              max={500}
              value={filters.max_results}
              onChange={(e) => set('max_results', Math.min(500, Math.max(10, Number(e.target.value))))}
              className="w-28 px-2.5 py-1.5 text-xs border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
            />
          </div>
        </div>
      )}

      {/* Actions */}
      <div className="flex flex-wrap gap-2 pt-2 border-t border-gray-100 dark:border-gray-700">
        <button
          type="button"
          onClick={onSearch}
          disabled={isLoading || !filters.role}
          className="flex-1 sm:flex-none px-5 py-2 text-sm font-medium bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {isLoading ? 'Pesquisando...' : 'Pesquisar vagas'}
        </button>
        <button
          type="button"
          onClick={onSave}
          disabled={!filters.role}
          className="px-4 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50"
        >
          Salvar filtro
        </button>
        <button
          type="button"
          onClick={() => onChange({ ...DEFAULT_FILTERS })}
          className="px-4 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700"
        >
          Limpar
        </button>
      </div>
    </div>
  )
}
