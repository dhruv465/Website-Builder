import { cn } from '@/lib/utils'
import { Loader2 } from 'lucide-react'
import { type VariantProps, cva } from 'class-variance-authority'

const spinnerVariants = cva('animate-spin', {
  variants: {
    size: {
      default: 'h-6 w-6',
      sm: 'h-4 w-4',
      lg: 'h-8 w-8',
      xl: 'h-12 w-12',
    },
    variant: {
      default: 'text-primary',
      muted: 'text-muted-foreground',
      destructive: 'text-destructive',
    },
  },
  defaultVariants: {
    size: 'default',
    variant: 'default',
  },
})

export interface LoadingSpinnerProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof spinnerVariants> {
  label?: string
}

export function LoadingSpinner({
  size,
  variant,
  label,
  className,
  ...props
}: LoadingSpinnerProps) {
  return (
    <div
      role="status"
      aria-label={label || 'Loading'}
      className={cn('flex items-center justify-center', className)}
      {...props}
    >
      <Loader2 className={cn(spinnerVariants({ size, variant }))} />
      {label && <span className="ml-2 text-sm text-muted-foreground">{label}</span>}
      <span className="sr-only">{label || 'Loading'}</span>
    </div>
  )
}

// Fullscreen loading spinner
export function LoadingSpinnerFullscreen({ label }: { label?: string }) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-background/80 backdrop-blur-sm">
      <div className="flex flex-col items-center gap-4">
        <LoadingSpinner size="xl" label={label} />
      </div>
    </div>
  )
}

// Inline loading spinner for buttons
export function LoadingSpinnerInline({ className }: { className?: string }) {
  return <Loader2 className={cn('h-4 w-4 animate-spin', className)} />
}
