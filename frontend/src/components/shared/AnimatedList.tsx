import { motion, useReducedMotion } from 'framer-motion';
import { ReactNode } from 'react';
import {
  listContainerVariants,
  listItemVariants,
  getVariants,
} from '@/lib/utils/animations';

interface AnimatedListProps {
  children: ReactNode;
  className?: string;
  staggerDelay?: number;
  delayChildren?: number;
}

/**
 * Animated list container with staggered children animations
 */
export function AnimatedList({
  children,
  className = '',
  staggerDelay = 0.1,
  delayChildren = 0.05,
}: AnimatedListProps) {
  const prefersReducedMotion = useReducedMotion();

  const containerVariants = {
    ...listContainerVariants,
    visible: {
      ...listContainerVariants.visible,
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

interface AnimatedListItemProps {
  children: ReactNode;
  className?: string;
}

/**
 * Animated list item for use within AnimatedList
 */
export function AnimatedListItem({ children, className = '' }: AnimatedListItemProps) {
  const prefersReducedMotion = useReducedMotion();

  return (
    <motion.div
      variants={getVariants(prefersReducedMotion, listItemVariants)}
      className={className}
    >
      {children}
    </motion.div>
  );
}
