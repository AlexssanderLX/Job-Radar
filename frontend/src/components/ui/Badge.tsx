import type { ReactNode } from 'react'

type Variant = 'default' | 'secondary' | 'destructive' | 'outline' | 'success' | 'warning'

interface BadgeProps {
  variant?: Variant
  children: ReactNode
  className?: string
}

const variantClasses: Record<Variant, string> = {
  default: 'bg-indigo-600/20 text-indigo-400 border-indigo-600/30',
  secondary: 'bg-zinc-800 text-zinc-300 border-zinc-700',
  destructive: 'bg-red-600/20 text-red-400 border-red-600/30',
  outline: 'bg-transparent text-zinc-400 border-zinc-700',
  success: 'bg-green-600/20 text-green-400 border-green-600/30',
  warning: 'bg-yellow-600/20 text-yellow-400 border-yellow-600/30',
}

export function Badge({ variant = 'default', children, className = '' }: BadgeProps) {
  return (
    <span
      className={[
        'inline-flex items-center gap-1 rounded border px-1.5 py-0.5 text-xs font-medium',
        variantClasses[variant],
        className,
      ].join(' ')}
    >
      {children}
    </span>
  )
}
