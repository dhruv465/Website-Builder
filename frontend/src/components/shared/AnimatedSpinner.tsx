import { motion, useReducedMotion } from 'framer-motion';
import { Loader2 } from 'lucide-react';
import { spinnerVariants } from '@/lib/utils/animations';
import { cn } from '@/lib/utils';

interface AnimatedSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

/**
 * Animated loading spinner component
 */
export function AnimatedSpinner({ size = 'md', className = '' }: AnimatedSpinnerProps) {
  const prefersReducedMotion = useReducedMotion();

  const sizeClasses = {
    sm: 'h-4 w-4',
    md: 'h-8 w-8',
    lg: 'h-12 w-12',
  };

  if (prefersReducedMotion) {
    return <Loader2 className={cn(sizeClasses[size], 'animate-spin', className)} />;
  }

  return (
    <motion.div variants={spinnerVariants} animate="animate">
      <Loader2 className={cn(sizeClasses[size], className)} />
    </motion.div>
  );
}

interface LoadingOverlayProps {
  isLoading: boolean;
  message?: string;
  className?: string;
}

/**
 * Full-screen loading overlay with spinner
 */
export function LoadingOverlay({
  isLoading,
  message = 'Loading...',
  className = '',
}: LoadingOverlayProps) {
  const prefersReducedMotion = useReducedMotion();

  if (!isLoading) return null;

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: prefersReducedMotion ? 0 : 0.2 }}
      className={cn(
        'fixed inset-0 z-50 flex items-center justify-center bg-background/80 backdrop-blur-sm',
        className
      )}
    >
      <div className="flex flex-col items-center gap-4">
        <AnimatedSpinner size="lg" />
        {message && <p className="text-sm text-muted-foreground">{message}</p>}
      </div>
    </motion.div>
  );
}
