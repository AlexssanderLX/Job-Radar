import { useState, useRef, useEffect, useCallback } from 'react'
import { ChevronDown, X, Check, Search } from 'lucide-react'

interface Option {
  value: string
  label: string
}

interface MultiSelectProps {
  options: Option[]
  value: string[]
  onChange: (value: string[]) => void
  label?: string
  placeholder?: string
  searchPlaceholder?: string
  className?: string
  disabled?: boolean
}

export function MultiSelect({
  options,
  value,
  onChange,
  label,
  placeholder = 'Selecionar...',
  searchPlaceholder = 'Buscar...',
  className = '',
  disabled = false,
}: MultiSelectProps) {
  const [open, setOpen] = useState(false)
  const [search, setSearch] = useState('')
  const containerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!open) return
    const handler = (e: MouseEvent) => {
      if (!containerRef.current?.contains(e.target as Node)) setOpen(false)
    }
    document.addEventListener('mousedown', handler)
    return () => document.removeEventListener('mousedown', handler)
  }, [open])

  useEffect(() => {
    if (!open) setSearch('')
  }, [open])

  const filtered = options.filter((o) =>
    o.label.toLowerCase().includes(search.toLowerCase())
  )

  const toggle = useCallback(
    (val: string) => {
      onChange(value.includes(val) ? value.filter((v) => v !== val) : [...value, val])
    },
    [value, onChange]
  )

  const selectAll = () => onChange(filtered.map((o) => o.value))
  const clear = () => onChange([])

  const displayText =
    value.length === 0
      ? placeholder
      : value.length === 1
        ? (options.find((o) => o.value === value[0])?.label ?? value[0])
        : `${value.length} selecionado(s)`

  return (
    <div ref={containerRef} className={['relative flex flex-col gap-1', className].join(' ')}>
      {label && <span className="text-xs font-medium text-zinc-400">{label}</span>}
      <button
        type="button"
        onClick={() => !disabled && setOpen((v) => !v)}
        disabled={disabled}
        className={[
          'flex items-center justify-between h-9 w-full rounded-md border border-zinc-700 bg-zinc-900 px-3 text-sm text-left transition-colors',
          'focus:outline-none focus:ring-2 focus:ring-indigo-500',
          disabled ? 'opacity-50 cursor-not-allowed' : 'hover:border-zinc-600',
          value.length > 0 ? 'text-zinc-100' : 'text-zinc-500',
        ].join(' ')}
      >
        <span className="truncate">{displayText}</span>
        <ChevronDown size={14} className={['text-zinc-500 transition-transform', open ? 'rotate-180' : ''].join(' ')} />
      </button>

      {/* Selected badges */}
      {value.length > 1 && (
        <div className="flex flex-wrap gap-1 mt-1">
          {value.map((v) => {
            const opt = options.find((o) => o.value === v)
            return (
              <span
                key={v}
                className="inline-flex items-center gap-1 rounded border border-indigo-600/30 bg-indigo-600/15 px-1.5 py-0.5 text-xs text-indigo-400"
              >
                {opt?.label ?? v}
                <button
                  type="button"
                  onClick={(e) => { e.stopPropagation(); toggle(v) }}
                  className="hover:text-indigo-200"
                >
                  <X size={10} />
                </button>
              </span>
            )
          })}
        </div>
      )}

      {open && (
        <div className="absolute top-full left-0 right-0 z-50 mt-1 rounded-md border border-zinc-700 bg-zinc-950 shadow-2xl">
          {/* Search */}
          <div className="flex items-center gap-2 border-b border-zinc-800 px-2.5 py-2">
            <Search size={12} className="text-zinc-500 shrink-0" />
            <input
              autoFocus
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder={searchPlaceholder}
              className="flex-1 bg-transparent text-sm text-zinc-100 placeholder-zinc-500 focus:outline-none min-w-0"
            />
          </div>
          {/* Actions */}
          <div className="flex items-center justify-between px-2.5 py-1.5 border-b border-zinc-800">
            <button
              type="button"
              onClick={selectAll}
              className="text-xs text-indigo-400 hover:text-indigo-300"
            >
              Selecionar todos
            </button>
            <button
              type="button"
              onClick={clear}
              className="text-xs text-zinc-500 hover:text-zinc-300"
            >
              Limpar
            </button>
          </div>
          {/* Options */}
          <div className="max-h-48 overflow-y-auto">
            {filtered.length === 0 && (
              <p className="px-3 py-2 text-xs text-zinc-500">Nenhuma opção</p>
            )}
            {filtered.map((opt) => (
              <button
                key={opt.value}
                type="button"
                onClick={() => toggle(opt.value)}
                className="flex w-full items-center gap-2.5 px-2.5 py-2 text-sm text-zinc-300 hover:bg-zinc-800 hover:text-zinc-100 transition-colors"
              >
                <span
                  className={[
                    'flex h-4 w-4 shrink-0 items-center justify-center rounded border transition-colors',
                    value.includes(opt.value)
                      ? 'bg-indigo-600 border-indigo-600'
                      : 'border-zinc-600',
                  ].join(' ')}
                >
                  {value.includes(opt.value) && <Check size={10} className="text-white" />}
                </span>
                {opt.label}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
