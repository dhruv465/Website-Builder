import { motion, useReducedMotion } from 'framer-motion';
import { ReactNode } from 'react';
import {
  gridContainerVariants,
  gridItemVariants,
  getVariants,
} from '@/lib/utils/animations';

interface AnimatedGridProps {
  children: ReactNode;
  className?: string;
  staggerDelay?: number;
  delayChildren?: number;
}

/**
 * Animated grid container with staggered children animations
 */
export function AnimatedGrid({
  children,
  className = '',
  staggerDelay = 0.08,
  delayChildren = 0.1,
}: AnimatedGridProps) {
  const prefersReducedMotion = useReducedMotion();

  const containerVariants = {
    ...gridContainerVariants,
    visible: {
      ...gridContainerVariants.visible,
      transition: {
        staggerChildren: prefersReducedMotion ? 0 : staggerDelay,
        delayChildren: prefersReducedMotion ? 0 : delayChildren,
      },
    },
  };

  return (
    <motion.div
      initial="hidden"
      animate="visible"
      exit="exit"
      variants={getVariants(prefersReducedMotion, containerVariants)}
      className={className}
    >
      {children}
    </motion.div>
  );
}

interface AnimatedGridItemProps {
  children: ReactNode;
  className?: string;
}

/**
 * Animated grid item for use within AnimatedGrid
 */
export function AnimatedGridItem({ children, className = '' }: AnimatedGridItemProps) {
  const prefersReducedMotion = useReducedMotion();

  return (
    <motion.div
      variants={getVariants(prefersReducedMotion, gridItemVariants)}
      className={className}
    >
      {children}
    </motion.div>
  );
}
