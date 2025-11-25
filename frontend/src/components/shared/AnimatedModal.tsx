import { motion, AnimatePresence, useReducedMotion } from 'framer-motion';
import { ReactNode } from 'react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from '@/components/ui/dialog';
import { modalVariants, getTransition, springTransition } from '@/lib/utils/animations';

interface AnimatedModalProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  description?: string;
  children: ReactNode;
  className?: string;
}

/**
 * Animated modal/dialog component with spring physics
 */
export function AnimatedModal({
  isOpen,
  onClose,
  title,
  description,
  children,
  className = '',
}: AnimatedModalProps) {
  const prefersReducedMotion = useReducedMotion();

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className={className}>
        <AnimatePresence mode="wait">
          {isOpen && (
            <motion.div
              initial="hidden"
              animate="visible"
              exit="exit"
              variants={modalVariants}
              transition={getTransition(prefersReducedMotion, springTransition)}
            >
              {(title || description) && (
                <DialogHeader>
                  {title && <DialogTitle>{title}</DialogTitle>}
                  {description && <DialogDescription>{description}</DialogDescription>}
                </DialogHeader>
              )}
              {children}
            </motion.div>
          )}
        </AnimatePresence>
      </DialogContent>
    </Dialog>
  );
}
