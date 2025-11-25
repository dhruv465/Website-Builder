import { motion, useReducedMotion } from 'framer-motion';
import { ComponentProps } from 'react';
import { Button } from '@/components/ui/button';
import { tapScale, hoverScale } from '@/lib/utils/animations';

type AnimatedButtonProps = ComponentProps<typeof Button>;

/**
 * Animated button component with hover and tap animations
 */
export function AnimatedButton({ children, disabled, ...props }: AnimatedButtonProps) {
  const prefersReducedMotion = useReducedMotion();

  return (
    <motion.div
      whileHover={!disabled && !prefersReducedMotion ? hoverScale : undefined}
      whileTap={!disabled && !prefersReducedMotion ? tapScale : undefined}
      style={{ display: 'inline-block' }}
    >
      <Button disabled={disabled} {...props}>
        {children}
      </Button>
    </motion.div>
  );
}
