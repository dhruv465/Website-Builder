import { Variants, Transition } from 'framer-motion';

/**
 * Animation utility functions and variant definitions for Framer Motion
 * Provides consistent animations across the application with reduced motion support
 */

// ============================================================================
// COMMON ANIMATION VARIANTS
// ============================================================================

/**
 * Page transition variants for route changes
 */
export const pageVariants: Variants = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -20 },
};

/**
 * Modal and dialog animation variants with spring physics
 */
export const modalVariants: Variants = {
  hidden: { opacity: 0, scale: 0.95 },
  visible: { opacity: 1, scale: 1 },
  exit: { opacity: 0, scale: 0.95 },
};

/**
 * Drawer/sidebar animation variants
 */
export const drawerVariants: Variants = {
  hidden: { x: '-100%', opacity: 0 },
  visible: { x: 0, opacity: 1 },
  exit: { x: '-100%', opacity: 0 },
};

/**
 * Fade in animation variants
 */
export const fadeInVariants: Variants = {
  hidden: { opacity: 0 },
  visible: { opacity: 1 },
  exit: { opacity: 0 },
};

/**
 * Slide up animation variants
 */
export const slideUpVariants: Variants = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: 20 },
};

/**
 * Slide down animation variants
 */
export const slideDownVariants: Variants = {
  hidden: { opacity: 0, y: -20 },
  visible: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -20 },
};

/**
 * Scale animation variants
 */
export const scaleVariants: Variants = {
  hidden: { opacity: 0, scale: 0.8 },
  visible: { opacity: 1, scale: 1 },
  exit: { opacity: 0, scale: 0.8 },
};

// ============================================================================
// LIST AND GRID ANIMATIONS
// ============================================================================

/**
 * Container variants for staggered list animations
 */
export const listContainerVariants: Variants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
      delayChildren: 0.05,
    },
  },
  exit: {
    opacity: 0,
    transition: {
      staggerChildren: 0.05,
      staggerDirection: -1,
    },
  },
};

/**
 * Item variants for staggered list animations
 */
export const listItemVariants: Variants = {
  hidden: { opacity: 0, x: -20 },
  visible: { opacity: 1, x: 0 },
  exit: { opacity: 0, x: -20 },
};

/**
 * Grid container variants for staggered grid animations
 */
export const gridContainerVariants: Variants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.08,
      delayChildren: 0.1,
    },
  },
};

/**
 * Grid item variants for staggered grid animations
 */
export const gridItemVariants: Variants = {
  hidden: { opacity: 0, scale: 0.9, y: 20 },
  visible: { opacity: 1, scale: 1, y: 0 },
  exit: { opacity: 0, scale: 0.9, y: 20 },
};

// ============================================================================
// INTERACTIVE ELEMENT ANIMATIONS
// ============================================================================

/**
 * Hover animation for interactive elements
 */
export const hoverScale = {
  scale: 1.05,
  transition: { type: 'spring', stiffness: 400, damping: 10 },
};

/**
 * Tap animation for buttons and clickable elements
 */
export const tapScale = {
  scale: 0.95,
  transition: { type: 'spring', stiffness: 400, damping: 10 },
};

/**
 * Hover lift animation (subtle elevation)
 */
export const hoverLift = {
  y: -4,
  transition: { type: 'spring', stiffness: 400, damping: 10 },
};

/**
 * Card hover animation with scale and shadow
 */
export const cardHoverVariants: Variants = {
  rest: { scale: 1, y: 0 },
  hover: {
    scale: 1.02,
    y: -4,
    transition: { type: 'spring', stiffness: 400, damping: 10 },
  },
  tap: { scale: 0.98 },
};

// ============================================================================
// LOADING STATE ANIMATIONS
// ============================================================================

/**
 * Skeleton loading animation
 */
export const skeletonVariants: Variants = {
  initial: { opacity: 0.5 },
  animate: {
    opacity: [0.5, 1, 0.5],
    transition: {
      duration: 1.5,
      repeat: Infinity,
      ease: 'easeInOut',
    },
  },
};

/**
 * Pulse animation for loading indicators
 */
export const pulseVariants: Variants = {
  initial: { scale: 1, opacity: 1 },
  animate: {
    scale: [1, 1.1, 1],
    opacity: [1, 0.8, 1],
    transition: {
      duration: 1.5,
      repeat: Infinity,
      ease: 'easeInOut',
    },
  },
};

/**
 * Spinner rotation animation
 */
export const spinnerVariants: Variants = {
  animate: {
    rotate: 360,
    transition: {
      duration: 1,
      repeat: Infinity,
      ease: 'linear',
    },
  },
};

// ============================================================================
// SCROLL-TRIGGERED ANIMATIONS
// ============================================================================

/**
 * Fade in from bottom on scroll
 */
export const scrollFadeInVariants: Variants = {
  hidden: { opacity: 0, y: 50 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.6, ease: 'easeOut' },
  },
};

/**
 * Slide in from left on scroll
 */
export const scrollSlideInLeftVariants: Variants = {
  hidden: { opacity: 0, x: -50 },
  visible: {
    opacity: 1,
    x: 0,
    transition: { duration: 0.6, ease: 'easeOut' },
  },
};

/**
 * Slide in from right on scroll
 */
export const scrollSlideInRightVariants: Variants = {
  hidden: { opacity: 0, x: 50 },
  visible: {
    opacity: 1,
    x: 0,
    transition: { duration: 0.6, ease: 'easeOut' },
  },
};

/**
 * Scale up on scroll
 */
export const scrollScaleVariants: Variants = {
  hidden: { opacity: 0, scale: 0.8 },
  visible: {
    opacity: 1,
    scale: 1,
    transition: { duration: 0.6, ease: 'easeOut' },
  },
};

// ============================================================================
// TRANSITION PRESETS
// ============================================================================

/**
 * Spring transition with default settings
 */
export const springTransition: Transition = {
  type: 'spring',
  stiffness: 300,
  damping: 30,
};

/**
 * Smooth spring transition (slower, more fluid)
 */
export const smoothSpringTransition: Transition = {
  type: 'spring',
  stiffness: 200,
  damping: 25,
};

/**
 * Bouncy spring transition
 */
export const bouncySpringTransition: Transition = {
  type: 'spring',
  stiffness: 400,
  damping: 15,
};

/**
 * Tween transition with ease out
 */
export const easeOutTransition: Transition = {
  duration: 0.3,
  ease: 'easeOut',
};

/**
 * Fast tween transition
 */
export const fastTransition: Transition = {
  duration: 0.15,
  ease: 'easeInOut',
};

/**
 * Slow tween transition
 */
export const slowTransition: Transition = {
  duration: 0.6,
  ease: 'easeInOut',
};

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

/**
 * Get transition based on reduced motion preference
 * @param prefersReducedMotion - Whether user prefers reduced motion
 * @param normalTransition - Transition to use when motion is enabled
 * @returns Appropriate transition based on preference
 */
export function getTransition(
  prefersReducedMotion: boolean | null,
  normalTransition: Transition = springTransition
): Transition {
  return prefersReducedMotion ? { duration: 0 } : normalTransition;
}

/**
 * Get variants with reduced motion support
 * @param prefersReducedMotion - Whether user prefers reduced motion
 * @param variants - Variants to modify
 * @returns Variants with motion disabled if preferred
 */
export function getVariants(
  prefersReducedMotion: boolean | null,
  variants: Variants
): Variants {
  if (!prefersReducedMotion) return variants;

  // Remove motion from variants
  const reducedVariants: Variants = {};
  Object.keys(variants).forEach((key) => {
    const variant = variants[key];
    if (typeof variant === 'object' && variant !== null) {
      reducedVariants[key] = { opacity: (variant as any).opacity ?? 1 };
    }
  });

  return reducedVariants;
}

/**
 * Create stagger configuration for list animations
 * @param staggerDelay - Delay between each item (default: 0.1)
 * @param delayChildren - Initial delay before first item (default: 0)
 * @returns Stagger configuration object
 */
export function createStaggerConfig(
  staggerDelay: number = 0.1,
  delayChildren: number = 0
) {
  return {
    staggerChildren: staggerDelay,
    delayChildren,
  };
}

/**
 * Create viewport configuration for scroll animations
 * @param once - Whether animation should only happen once (default: true)
 * @param amount - Amount of element that should be visible (default: 0.3)
 * @returns Viewport configuration object
 */
export function createViewportConfig(once: boolean = true, amount: number = 0.3) {
  return {
    once,
    amount,
  };
}

/**
 * Combine multiple animation variants
 * @param variants - Array of variant objects to combine
 * @returns Combined variants object
 */
export function combineVariants(...variants: Variants[]): Variants {
  return variants.reduce((acc, variant) => ({ ...acc, ...variant }), {});
}
