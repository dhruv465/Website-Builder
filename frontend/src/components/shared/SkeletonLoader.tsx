import { motion, useReducedMotion } from 'framer-motion';
import { skeletonVariants } from '@/lib/utils/animations';
import { cn } from '@/lib/utils';

interface SkeletonLoaderProps {
  className?: string;
  width?: string | number;
  height?: string | number;
  variant?: 'text' | 'circular' | 'rectangular';
}

/**
 * Skeleton loader component with pulse animation
 */
export function SkeletonLoader({
  className = '',
  width = '100%',
  height = '1rem',
  variant = 'rectangular',
}: SkeletonLoaderProps) {
  const prefersReducedMotion = useReducedMotion();

  const variantClasses = {
    text: 'rounded',
    circular: 'rounded-full',
    rectangular: 'rounded-md',
  };

  return (
    <motion.div
      variants={prefersReducedMotion ? undefined : skeletonVariants}
      initial="initial"
      animate={prefersReducedMotion ? undefined : 'animate'}
      className={cn(
        'bg-muted',
        variantClasses[variant],
        className
      )}
      style={{ width, height }}
    />
  );
}

interface SkeletonTextProps {
  lines?: number;
  className?: string;
}

/**
 * Skeleton text loader with multiple lines
 */
export function SkeletonText({ lines = 3, className = '' }: SkeletonTextProps) {
  return (
    <div className={cn('space-y-2', className)}>
      {Array.from({ length: lines }).map((_, index) => (
        <SkeletonLoader
          key={index}
          variant="text"
          height="0.875rem"
          width={index === lines - 1 ? '60%' : '100%'}
        />
      ))}
    </div>
  );
}

interface SkeletonCardProps {
  className?: string;
}

/**
 * Skeleton card loader
 */
export function SkeletonCard({ className = '' }: SkeletonCardProps) {
  return (
    <div className={cn('rounded-lg border bg-card p-6', className)}>
      <div className="space-y-4">
        <SkeletonLoader height="1.5rem" width="60%" />
        <SkeletonText lines={3} />
        <div className="flex gap-2">
          <SkeletonLoader height="2rem" width="5rem" />
          <SkeletonLoader height="2rem" width="5rem" />
        </div>
      </div>
    </div>
  );
}
