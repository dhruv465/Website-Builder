import { motion, useReducedMotion } from 'framer-motion';
import { ReactNode } from 'react';
import {
  scrollFadeInVariants,
  scrollSlideInLeftVariants,
  scrollSlideInRightVariants,
  scrollScaleVariants,
  createViewportConfig,
} from '@/lib/utils/animations';

interface ScrollRevealProps {
  children: ReactNode;
  className?: string;
  direction?: 'up' | 'left' | 'right' | 'scale';
  delay?: number;
  once?: boolean;
  amount?: number;
}

/**
 * Scroll-triggered reveal animation component
 */
export function ScrollReveal({
  children,
  className = '',
  direction = 'up',
  delay = 0,
  once = true,
  amount = 0.3,
}: ScrollRevealProps) {
  const prefersReducedMotion = useReducedMotion();

  const variantMap = {
    up: scrollFadeInVariants,
    left: scrollSlideInLeftVariants,
    right: scrollSlideInRightVariants,
    scale: scrollScaleVariants,
  };

  const variants = variantMap[direction];

  if (prefersReducedMotion) {
    return <div className={className}>{children}</div>;
  }

  return (
    <motion.div
      initial="hidden"
      whileInView="visible"
      viewport={createViewportConfig(once, amount)}
      variants={variants}
      transition={{ delay }}
      className={className}
    >
      {children}
    </motion.div>
  );
}
