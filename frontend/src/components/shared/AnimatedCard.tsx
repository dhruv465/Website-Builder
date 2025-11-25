import { motion, useReducedMotion } from 'framer-motion';
import { ReactNode } from 'react';
import { Card } from '@/components/ui/card';
import { cardHoverVariants } from '@/lib/utils/animations';
import { cn } from '@/lib/utils';

interface AnimatedCardProps {
  children: ReactNode;
  className?: string;
  onClick?: () => void;
  enableHover?: boolean;
}

/**
 * Animated card component with hover and tap animations
 */
export function AnimatedCard({
  children,
  className = '',
  onClick,
  enableHover = true,
}: AnimatedCardProps) {
  const prefersReducedMotion = useReducedMotion();

  const MotionCard = motion(Card);

  return (
    <MotionCard
      initial="rest"
      whileHover={enableHover && !prefersReducedMotion ? 'hover' : undefined}
      whileTap={onClick && !prefersReducedMotion ? 'tap' : undefined}
      variants={cardHoverVariants}
      onClick={onClick}
      className={cn(
        onClick && 'cursor-pointer',
        'transition-shadow duration-200',
        className
      )}
    >
      {children}
    </MotionCard>
  );
}
