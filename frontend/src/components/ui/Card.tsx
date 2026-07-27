import type { ReactNode, HTMLAttributes } from 'react'

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  children: ReactNode
}

export function Card({ children, className = '', ...props }: CardProps) {
  return (
    <div
      className={['rounded-lg border border-zinc-800 bg-zinc-900/50', className].join(' ')}
      {...props}
    >
      {children}
    </div>
  )
}

export function CardHeader({ children, className = '' }: { children: ReactNode; className?: string }) {
  return <div className={['px-4 py-3 border-b border-zinc-800', className].join(' ')}>{children}</div>
}

export function CardTitle({ children, className = '' }: { children: ReactNode; className?: string }) {
  return <h3 className={['text-sm font-semibold text-zinc-100', className].join(' ')}>{children}</h3>
}

export function CardDescription({ children, className = '' }: { children: ReactNode; className?: string }) {
  return <p className={['text-xs text-zinc-400 mt-0.5', className].join(' ')}>{children}</p>
}

export function CardContent({ children, className = '' }: { children: ReactNode; className?: string }) {
  return <div className={['px-4 py-3', className].join(' ')}>{children}</div>
}

export function CardFooter({ children, className = '' }: { children: ReactNode; className?: string }) {
  return (
    <div className={['px-4 py-3 border-t border-zinc-800 flex items-center gap-2', className].join(' ')}>
      {children}
    </div>
  )
}
