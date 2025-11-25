/**
 * Responsive utility functions and helpers
 */

/**
 * Breakpoint values matching Tailwind config
 */
export const breakpoints = {
  xs: 475,
  sm: 640,
  md: 768,
  lg: 1024,
  xl: 1280,
  '2xl': 1536,
} as const;

export type Breakpoint = keyof typeof breakpoints;

/**
 * Check if current viewport matches a breakpoint
 * @param breakpoint The breakpoint to check
 * @param direction 'up' for min-width, 'down' for max-width
 */
export function matchesBreakpoint(
  breakpoint: Breakpoint,
  direction: 'up' | 'down' = 'up'
): boolean {
  if (typeof window === 'undefined') return false;
  
  const width = window.innerWidth;
  const breakpointValue = breakpoints[breakpoint];
  
  return direction === 'up' ? width >= breakpointValue : width < breakpointValue;
}

/**
 * Get current breakpoint category
 */
export function getCurrentBreakpoint(): Breakpoint {
  if (typeof window === 'undefined') return 'lg';
  
  const width = window.innerWidth;
  
  if (width >= breakpoints['2xl']) return '2xl';
  if (width >= breakpoints.xl) return 'xl';
  if (width >= breakpoints.lg) return 'lg';
  if (width >= breakpoints.md) return 'md';
  if (width >= breakpoints.sm) return 'sm';
  return 'xs';
}

/**
 * Check if device is mobile (< md breakpoint)
 */
export function isMobile(): boolean {
  return matchesBreakpoint('md', 'down');
}

/**
 * Check if device is tablet (md to lg)
 */
export function isTablet(): boolean {
  return matchesBreakpoint('md', 'up') && matchesBreakpoint('lg', 'down');
}

/**
 * Check if device is desktop (>= lg)
 */
export function isDesktop(): boolean {
  return matchesBreakpoint('lg', 'up');
}

/**
 * Get responsive value based on current breakpoint
 * @param values Object with breakpoint keys and values
 * @param defaultValue Fallback value
 */
export function getResponsiveValue<T>(
  values: Partial<Record<Breakpoint, T>>,
  defaultValue: T
): T {
  const currentBreakpoint = getCurrentBreakpoint();
  
  // Check current breakpoint first
  const currentValue = values[currentBreakpoint];
  if (currentValue !== undefined) {
    return currentValue;
  }
  
  // Fall back to smaller breakpoints
  const breakpointOrder: Breakpoint[] = ['xs', 'sm', 'md', 'lg', 'xl', '2xl'];
  const currentIndex = breakpointOrder.indexOf(currentBreakpoint);
  
  for (let i = currentIndex - 1; i >= 0; i--) {
    const bp = breakpointOrder[i];
    if (bp) {
      const value = values[bp];
      if (value !== undefined) {
        return value;
      }
    }
  }
  
  return defaultValue;
}

/**
 * Clamp a value for touch-friendly sizing
 * Ensures minimum 44px touch target size (WCAG guideline)
 */
export function clampTouchSize(size: number): number {
  const MIN_TOUCH_SIZE = 44;
  return Math.max(size, MIN_TOUCH_SIZE);
}

/**
 * Get optimal font size for mobile to prevent iOS zoom on input focus
 */
export function getMobileFontSize(): string {
  return isMobile() ? '16px' : '14px';
}

/**
 * Check if device supports hover (not touch-only)
 */
export function supportsHover(): boolean {
  if (typeof window === 'undefined') return true;
  return window.matchMedia('(hover: hover)').matches;
}

/**
 * Check if user prefers reduced motion
 */
export function prefersReducedMotion(): boolean {
  if (typeof window === 'undefined') return false;
  return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
}

/**
 * Get safe area insets for devices with notches
 */
export function getSafeAreaInsets(): {
  top: number;
  right: number;
  bottom: number;
  left: number;
} {
  if (typeof window === 'undefined' || !CSS.supports('padding-top: env(safe-area-inset-top)')) {
    return { top: 0, right: 0, bottom: 0, left: 0 };
  }

  const computedStyle = getComputedStyle(document.documentElement);
  
  return {
    top: parseInt(computedStyle.getPropertyValue('--safe-area-inset-top') || '0'),
    right: parseInt(computedStyle.getPropertyValue('--safe-area-inset-right') || '0'),
    bottom: parseInt(computedStyle.getPropertyValue('--safe-area-inset-bottom') || '0'),
    left: parseInt(computedStyle.getPropertyValue('--safe-area-inset-left') || '0'),
  };
}

/**
 * Responsive grid columns calculator
 * @param itemCount Number of items to display
 * @param maxColumns Maximum columns for desktop
 */
export function getResponsiveColumns(itemCount: number, maxColumns: number = 3): {
  mobile: number;
  tablet: number;
  desktop: number;
} {
  const mobile = itemCount === 1 ? 1 : Math.min(itemCount, 2);
  const tablet = Math.min(itemCount, Math.ceil(maxColumns / 1.5));
  const desktop = Math.min(itemCount, maxColumns);
  
  return { mobile, tablet, desktop };
}

/**
 * Format responsive class names
 * @param base Base class
 * @param responsive Responsive variants
 */
export function responsiveClass(
  base: string,
  responsive?: Partial<Record<Breakpoint, string>>
): string {
  if (!responsive) return base;
  
  const classes = [base];
  
  Object.entries(responsive).forEach(([breakpoint, value]) => {
    if (value) {
      classes.push(`${breakpoint}:${value}`);
    }
  });
  
  return classes.join(' ');
}
