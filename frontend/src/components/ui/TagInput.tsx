import { useState, type KeyboardEvent } from 'react'
import { X } from 'lucide-react'

interface TagInputProps {
  label?: string
  value: string[]
  onChange: (v: string[]) => void
  placeholder?: string
  hint?: string
}

export function TagInput({ label, value, onChange, placeholder = 'Digite e pressione Enter', hint }: TagInputProps) {
  const [input, setInput] = useState('')

  const add = () => {
    const trimmed = input.trim()
    if (trimmed && !value.includes(trimmed)) {
      onChange([...value, trimmed])
    }
    setInput('')
  }

  const handleKey = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' || e.key === ',') {
      e.preventDefault()
      add()
    } else if (e.key === 'Backspace' && input === '' && value.length > 0) {
      onChange(value.slice(0, -1))
    }
  }

  const remove = (tag: string) => onChange(value.filter((v) => v !== tag))

  return (
    <div className="flex flex-col gap-1">
      {label && <span className="text-xs font-medium text-zinc-400">{label}</span>}
      <div className="min-h-9 rounded-md border border-zinc-700 bg-zinc-900 px-2 py-1.5 flex flex-wrap gap-1 focus-within:ring-2 focus-within:ring-indigo-500 focus-within:border-transparent">
        {value.map((tag) => (
          <span
            key={tag}
            className="inline-flex items-center gap-1 rounded border border-zinc-700 bg-zinc-800 px-1.5 py-0.5 text-xs text-zinc-300"
          >
            {tag}
            <button type="button" onClick={() => remove(tag)} className="text-zinc-500 hover:text-zinc-200">
              <X size={10} />
            </button>
          </span>
        ))}
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKey}
          onBlur={add}
          placeholder={value.length === 0 ? placeholder : ''}
          className="flex-1 bg-transparent text-sm text-zinc-100 placeholder-zinc-500 focus:outline-none min-w-[120px]"
        />
      </div>
      {hint && <p className="text-xs text-zinc-500">{hint}</p>}
    </div>
  )
}
