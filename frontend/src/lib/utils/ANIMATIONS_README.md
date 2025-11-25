# Animation System Documentation

This document describes the comprehensive animation system built with Framer Motion for the Website Builder frontend.

## Overview

The animation system provides:
- **Consistent animations** across the application
- **Reduced motion support** for accessibility
- **Reusable animation components** and utilities
- **Performance-optimized** animations
- **Type-safe** animation definitions

## Core Utilities

### Animation Variants

Pre-defined animation variants for common patterns:

#### Page Transitions
```typescript
import { pageVariants } from '@/lib/utils/animations';

<motion.div variants={pageVariants} initial="initial" animate="animate" exit="exit">
  {/* Page content */}
</motion.div>
```

#### Modal/Dialog Animations
```typescript
import { modalVariants } from '@/lib/utils/animations';

<motion.div variants={modalVariants} initial="hidden" animate="visible" exit="exit">
  {/* Modal content */}
</motion.div>
```

#### List Animations (Staggered)
```typescript
import { listContainerVariants, listItemVariants } from '@/lib/utils/animations';

<motion.div variants={listContainerVariants} initial="hidden" animate="visible">
  {items.map(item => (
    <motion.div key={item.id} variants={listItemVariants}>
      {/* Item content */}
    </motion.div>
  ))}
</motion.div>
```

#### Grid Animations (Staggered)
```typescript
import { gridContainerVariants, gridItemVariants } from '@/lib/utils/animations';

<motion.div variants={gridContainerVariants} initial="hidden" animate="visible">
  {items.map(item => (
    <motion.div key={item.id} variants={gridItemVariants}>
      {/* Item content */}
    </motion.div>
  ))}
</motion.div>
```

#### Scroll-Triggered Animations
```typescript
import { scrollFadeInVariants } from '@/lib/utils/animations';

<motion.div
  variants={scrollFadeInVariants}
  initial="hidden"
  whileInView="visible"
  viewport={{ once: true, amount: 0.3 }}
>
  {/* Content */}
</motion.div>
```

### Interactive Animations

#### Hover Effects
```typescript
import { hoverScale, hoverLift } from '@/lib/utils/animations';

<motion.div whileHover={hoverScale}>
  {/* Hoverable content */}
</motion.div>
```

#### Tap Effects
```typescript
import { tapScale } from '@/lib/utils/animations';

<motion.button whileTap={tapScale}>
  Click me
</motion.button>
```

#### Card Hover
```typescript
import { cardHoverVariants } from '@/lib/utils/animations';

<motion.div
  initial="rest"
  whileHover="hover"
  whileTap="tap"
  variants={cardHoverVariants}
>
  {/* Card content */}
</motion.div>
```

### Loading Animations

#### Skeleton Loading
```typescript
import { skeletonVariants } from '@/lib/utils/animations';

<motion.div variants={skeletonVariants} initial="initial" animate="animate">
  {/* Skeleton content */}
</motion.div>
```

#### Pulse Animation
```typescript
import { pulseVariants } from '@/lib/utils/animations';

<motion.div variants={pulseVariants} initial="initial" animate="animate">
  {/* Pulsing content */}
</motion.div>
```

#### Spinner
```typescript
import { spinnerVariants } from '@/lib/utils/animations';

<motion.div variants={spinnerVariants} animate="animate">
  {/* Spinner icon */}
</motion.div>
```

### Transition Presets

```typescript
import {
  springTransition,
  smoothSpringTransition,
  bouncySpringTransition,
  easeOutTransition,
  fastTransition,
  slowTransition,
} from '@/lib/utils/animations';

<motion.div transition={springTransition}>
  {/* Content */}
</motion.div>
```

### Utility Functions

#### getTransition
Automatically adjusts transitions based on reduced motion preference:

```typescript
import { getTransition, springTransition } from '@/lib/utils/animations';
import { useReducedMotion } from 'framer-motion';

const prefersReducedMotion = useReducedMotion();
const transition = getTransition(prefersReducedMotion, springTransition);
```

#### getVariants
Simplifies variants for reduced motion:

```typescript
import { getVariants, pageVariants } from '@/lib/utils/animations';
import { useReducedMotion } from 'framer-motion';

const prefersReducedMotion = useReducedMotion();
const variants = getVariants(prefersReducedMotion, pageVariants);
```

#### createStaggerConfig
Creates stagger configuration for list/grid animations:

```typescript
import { createStaggerConfig } from '@/lib/utils/animations';

const staggerConfig = createStaggerConfig(0.1, 0.05);
// { staggerChildren: 0.1, delayChildren: 0.05 }
```

#### createViewportConfig
Creates viewport configuration for scroll animations:

```typescript
import { createViewportConfig } from '@/lib/utils/animations';

const viewportConfig = createViewportConfig(true, 0.3);
// { once: true, amount: 0.3 }
```

#### combineVariants
Combines multiple variant objects:

```typescript
import { combineVariants } from '@/lib/utils/animations';

const combined = combineVariants(variants1, variants2, variants3);
```

## Animation Components

### AnimatedPage
Wraps page content with page transition animations:

```typescript
import { AnimatedPage } from '@/components/shared';

<AnimatedPage className="container">
  {/* Page content */}
</AnimatedPage>
```

### AnimatedList & AnimatedListItem
Creates staggered list animations:

```typescript
import { AnimatedList, AnimatedListItem } from '@/components/shared';

<AnimatedList staggerDelay={0.1} delayChildren={0.05}>
  {items.map(item => (
    <AnimatedListItem key={item.id}>
      {/* Item content */}
    </AnimatedListItem>
  ))}
</AnimatedList>
```

### AnimatedGrid & AnimatedGridItem
Creates staggered grid animations:

```typescript
import { AnimatedGrid, AnimatedGridItem } from '@/components/shared';

<AnimatedGrid className="grid grid-cols-3 gap-4">
  {items.map(item => (
    <AnimatedGridItem key={item.id}>
      {/* Item content */}
    </AnimatedGridItem>
  ))}
</AnimatedGrid>
```

### AnimatedCard
Card component with hover animations:

```typescript
import { AnimatedCard } from '@/components/shared';

<AnimatedCard enableHover onClick={handleClick}>
  {/* Card content */}
</AnimatedCard>
```

### AnimatedButton
Button with hover and tap animations:

```typescript
import { AnimatedButton } from '@/components/shared';

<AnimatedButton variant="default" size="lg">
  Click me
</AnimatedButton>
```

### AnimatedModal
Modal with spring-based animations:

```typescript
import { AnimatedModal } from '@/components/shared';

<AnimatedModal
  isOpen={isOpen}
  onClose={handleClose}
  title="Modal Title"
  description="Modal description"
>
  {/* Modal content */}
</AnimatedModal>
```

### ScrollReveal
Scroll-triggered reveal animations:

```typescript
import { ScrollReveal } from '@/components/shared';

<ScrollReveal direction="up" delay={0.2} once={true}>
  {/* Content to reveal */}
</ScrollReveal>
```

Directions: `'up' | 'left' | 'right' | 'scale'`

### AnimatedSpinner
Loading spinner with rotation animation:

```typescript
import { AnimatedSpinner } from '@/components/shared';

<AnimatedSpinner size="md" />
```

Sizes: `'sm' | 'md' | 'lg'`

### LoadingOverlay
Full-screen loading overlay:

```typescript
import { LoadingOverlay } from '@/components/shared';

<LoadingOverlay isLoading={isLoading} message="Loading..." />
```

### Skeleton Loaders
Loading state placeholders:

```typescript
import { SkeletonLoader, SkeletonText, SkeletonCard } from '@/components/shared';

// Single skeleton
<SkeletonLoader variant="rectangular" width="100%" height="2rem" />

// Text skeleton
<SkeletonText lines={3} />

// Card skeleton
<SkeletonCard />
```

## Accessibility

### Reduced Motion Support

All animations automatically respect the user's `prefers-reduced-motion` setting:

```typescript
import { useReducedMotion } from 'framer-motion';

const prefersReducedMotion = useReducedMotion();

// Animations are automatically disabled when prefersReducedMotion is true
```

### Best Practices

1. **Always use `useReducedMotion()`** when creating custom animations
2. **Provide instant transitions** when reduced motion is preferred
3. **Keep animations subtle** - avoid excessive motion
4. **Use semantic HTML** - animations should enhance, not replace, semantic structure
5. **Test with reduced motion enabled** in your OS settings

## Performance

### Optimization Tips

1. **Use `transform` and `opacity`** for animations (GPU-accelerated)
2. **Avoid animating `width`, `height`, `top`, `left`** (causes layout recalculation)
3. **Use `will-change` sparingly** - only for animations that will definitely happen
4. **Implement code splitting** for heavy animation libraries
5. **Use `AnimatePresence`** for exit animations
6. **Limit simultaneous animations** - stagger when possible

### Code Splitting

Heavy animation components are lazy-loaded:

```typescript
const HeavyAnimatedComponent = lazy(() => import('./HeavyAnimatedComponent'));

<Suspense fallback={<SkeletonLoader />}>
  <HeavyAnimatedComponent />
</Suspense>
```

## Examples

### Complete Page with Animations

```typescript
import { AnimatedPage, ScrollReveal, AnimatedGrid, AnimatedGridItem } from '@/components/shared';

export default function ExamplePage() {
  return (
    <AnimatedPage className="container">
      <ScrollReveal direction="up">
        <h1>Page Title</h1>
      </ScrollReveal>

      <ScrollReveal direction="up" delay={0.2}>
        <p>Page description</p>
      </ScrollReveal>

      <AnimatedGrid className="grid grid-cols-3 gap-4">
        {items.map(item => (
          <AnimatedGridItem key={item.id}>
            <Card>{item.content}</Card>
          </AnimatedGridItem>
        ))}
      </AnimatedGrid>
    </AnimatedPage>
  );
}
```

### Interactive Card Grid

```typescript
import { AnimatedGrid, AnimatedGridItem, AnimatedCard } from '@/components/shared';

export default function CardGrid() {
  return (
    <AnimatedGrid className="grid grid-cols-3 gap-4">
      {items.map(item => (
        <AnimatedGridItem key={item.id}>
          <AnimatedCard enableHover onClick={() => handleClick(item.id)}>
            <CardHeader>
              <CardTitle>{item.title}</CardTitle>
            </CardHeader>
          </AnimatedCard>
        </AnimatedGridItem>
      ))}
    </AnimatedGrid>
  );
}
```

### Loading States

```typescript
import { SkeletonCard, AnimatedGrid, AnimatedGridItem } from '@/components/shared';

export default function LoadingExample() {
  const { data, isLoading } = useQuery();

  if (isLoading) {
    return (
      <div className="grid grid-cols-3 gap-4">
        {[1, 2, 3].map(i => (
          <SkeletonCard key={i} />
        ))}
      </div>
    );
  }

  return (
    <AnimatedGrid className="grid grid-cols-3 gap-4">
      {data.map(item => (
        <AnimatedGridItem key={item.id}>
          <Card>{item.content}</Card>
        </AnimatedGridItem>
      ))}
    </AnimatedGrid>
  );
}
```

## Testing

Animation components are fully tested. See `animations.test.ts` for examples.

```typescript
import { describe, it, expect } from 'vitest';
import { getTransition, springTransition } from './animations';

describe('Animation Utilities', () => {
  it('should respect reduced motion preference', () => {
    const result = getTransition(true, springTransition);
    expect(result.duration).toBe(0);
  });
});
```

## Browser Support

- Chrome/Edge: Full support
- Firefox: Full support
- Safari: Full support (iOS 12+)
- Reduced motion: All modern browsers

## Resources

- [Framer Motion Documentation](https://www.framer.com/motion/)
- [Web Animations API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Animations_API)
- [prefers-reduced-motion](https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-reduced-motion)
- [WCAG Animation Guidelines](https://www.w3.org/WAI/WCAG21/Understanding/animation-from-interactions.html)
