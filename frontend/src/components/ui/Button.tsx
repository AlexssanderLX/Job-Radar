import { type ButtonHTMLAttributes, forwardRef } from 'react'

type Variant = 'default' | 'ghost' | 'destructive' | 'outline' | 'link'
type Size = 'sm' | 'md' | 'lg'

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant
  size?: Size
  loading?: boolean
}

const variantClasses: Record<Variant, string> = {
  default:
    'bg-violet-600 text-white hover:bg-violet-500 disabled:opacity-50',
  ghost:
    'bg-transparent text-zinc-400 hover:bg-zinc-900 hover:text-zinc-100',
  destructive:
    'bg-red-600 text-white hover:bg-red-700',
  outline:
    'border border-zinc-800 bg-transparent text-zinc-300 hover:border-zinc-600 hover:bg-zinc-900 hover:text-zinc-100',
  link:
    'bg-transparent text-violet-400 hover:text-violet-300 underline-offset-2 hover:underline p-0',
}

const sizeClasses: Record<Size, string> = {
  sm: 'h-7 px-2.5 text-xs gap-1.5',
  md: 'h-9 px-3.5 text-sm gap-2',
  lg: 'h-10 px-4 text-sm gap-2',
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ variant = 'default', size = 'md', loading, className = '', children, disabled, ...props }, ref) => {
    return (
      <button
        ref={ref}
        disabled={disabled ?? loading}
        className={[
          'inline-flex items-center justify-center rounded-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-violet-500 disabled:pointer-events-none disabled:opacity-50',
          variantClasses[variant],
          sizeClasses[size],
          className,
        ].join(' ')}
        {...props}
      >
        {loading && (
          <span className="inline-block w-3.5 h-3.5 border-2 border-current border-t-transparent rounded-full animate-spin" />
        )}
        {children}
      </button>
    )
  }
)

Button.displayName = 'Button'
