# Responsive Design Implementation

This document describes the responsive design and mobile optimization features implemented in the Website Builder frontend.

## Overview

The application is built with a mobile-first approach, ensuring optimal user experience across all device sizes from smartphones to large desktop displays.

## Breakpoints

The following responsive breakpoints are defined in `tailwind.config.ts`:

- **xs**: 475px - Extra small devices (small phones)
- **sm**: 640px - Small devices (landscape phones)
- **md**: 768px - Medium devices (tablets)
- **lg**: 1024px - Large devices (desktops)
- **xl**: 1280px - Extra large devices
- **2xl**: 1536px - 2X large devices

## Key Features

### 1. Mobile Navigation

**Component**: `MobileMenu.tsx`

- Hamburger menu for mobile/tablet devices (< lg breakpoint)
- Slide-in drawer animation with backdrop
- Touch-friendly navigation links (44px minimum height)
- Keyboard accessible with focus trap
- Automatically hidden on desktop

**Usage**:
```tsx
import { MobileMenu } from '@/components/shared';

// Automatically shown on mobile, hidden on desktop
<MobileMenu />
```

### 2. Responsive Typography

Typography scales automatically based on viewport size:

```css
h1: text-2xl (mobile) → text-3xl (sm) → text-4xl (lg)
h2: text-xl (mobile) → text-2xl (sm) → text-3xl (lg)
h3: text-lg (mobile) → text-xl (sm) → text-2xl (lg)
```

### 3. Touch-Optimized Inputs

**Components**: `ResponsiveInput.tsx`, `ResponsiveTextarea.tsx`

Features:
- Minimum 44px height for touch targets (WCAG guideline)
- 16px font size to prevent iOS zoom on focus
- Appropriate `inputMode` for mobile keyboards
- Optional auto-resize for textareas
- Disable auto-features (autocorrect, autocapitalize) when needed

**Usage**:
```tsx
import { ResponsiveInput, ResponsiveTextarea } from '@/components/ui';

<ResponsiveInput
  type="email"
  inputMode="email"
  placeholder="Enter email"
/>

<ResponsiveTextarea
  autoResize
  disableAutoFeatures
  placeholder="Enter description"
/>
```

### 4. Mobile Gestures

**Hooks**: `useSwipeGesture`, `usePinchZoom`

Support for touch gestures:
- Swipe left/right/up/down
- Pinch-to-zoom
- Configurable thresholds and callbacks

**Usage**:
```tsx
import { useSwipeGesture, usePinchZoom } from '@/lib/hooks/useSwipeGesture';

// Swipe gestures
const swipeRef = useSwipeGesture({
  onSwipeLeft: () => console.log('Swiped left'),
  onSwipeRight: () => console.log('Swiped right'),
  minSwipeDistance: 50,
});

// Pinch zoom
const pinchRef = usePinchZoom((scale) => {
  console.log('Pinch scale:', scale);
});

<div ref={swipeRef}>Swipeable content</div>
```

### 5. Device Detection

**Hooks**: `useTouchDevice`, `useViewportSize`, `useOrientation`

Detect device capabilities and viewport characteristics:

```tsx
import { useTouchDevice, useViewportSize, useOrientation } from '@/lib/hooks/useTouchDevice';

const isTouchDevice = useTouchDevice(); // boolean
const viewportSize = useViewportSize(); // 'mobile' | 'tablet' | 'desktop'
const orientation = useOrientation(); // 'portrait' | 'landscape'
```

### 6. Responsive Utilities

**File**: `lib/utils/responsive.ts`

Helper functions for responsive behavior:

```tsx
import {
  isMobile,
  isTablet,
  isDesktop,
  getCurrentBreakpoint,
  getResponsiveValue,
  supportsHover,
  prefersReducedMotion,
} from '@/lib/utils/responsive';

// Check device type
if (isMobile()) {
  // Mobile-specific logic
}

// Get responsive value
const columns = getResponsiveValue(
  { xs: 1, sm: 2, lg: 3 },
  2 // default
);

// Check capabilities
if (supportsHover()) {
  // Add hover effects
}
```

## Mobile Optimizations

### Viewport Configuration

The `index.html` includes mobile-optimized viewport settings:

```html
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0, user-scalable=yes, viewport-fit=cover" />
<meta name="mobile-web-app-capable" content="yes" />
<meta name="apple-mobile-web-app-capable" content="yes" />
```

### Safe Area Insets

Support for devices with notches (iPhone X+):

```css
:root {
  --safe-area-inset-top: env(safe-area-inset-top, 0px);
  --safe-area-inset-right: env(safe-area-inset-right, 0px);
  --safe-area-inset-bottom: env(safe-area-inset-bottom, 0px);
  --safe-area-inset-left: env(safe-area-inset-left, 0px);
}
```

### CSS Utilities

Mobile-specific utility classes:

- `.scrollbar-hide` - Hide scrollbars for cleaner mobile UI
- `.tap-highlight-none` - Remove tap highlight on touch
- `.select-none-touch` - Prevent text selection on interactive elements
- `.momentum-scroll` - Smooth momentum scrolling on iOS
- `.no-overscroll` - Prevent pull-to-refresh
- `.active:scale-95` - Touch feedback animation

## Responsive Layout Patterns

### Container Padding

Responsive padding scales with viewport:

```tsx
<div className="px-3 sm:px-4 md:px-6 lg:px-8">
  {/* Content with responsive padding */}
</div>
```

### Grid Layouts

Mobile-first grid layouts:

```tsx
<div className="grid grid-cols-1 xs:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4">
  {/* Responsive grid items */}
</div>
```

### Conditional Rendering

Hide/show elements based on breakpoint:

```tsx
{/* Hidden on mobile, visible on desktop */}
<div className="hidden lg:block">Desktop only</div>

{/* Visible on mobile, hidden on desktop */}
<div className="lg:hidden">Mobile only</div>
```

## Touch-Friendly Design

### Minimum Touch Targets

All interactive elements meet WCAG 2.1 AA guidelines:
- Minimum 44px × 44px touch target size
- Adequate spacing between interactive elements
- Clear visual feedback on touch

### Form Inputs

- 16px minimum font size to prevent iOS zoom
- Appropriate keyboard types via `inputMode`
- Touch-optimized spacing and sizing

### Buttons and Links

```tsx
<Button className="min-h-touch px-4 py-2">
  Touch-friendly button
</Button>
```

## Performance Considerations

### Code Splitting

Mobile devices benefit from code splitting:
- Route-based splitting with React.lazy
- Component lazy loading for heavy features
- Optimized bundle sizes

### Image Optimization

- Responsive images with `srcset`
- Lazy loading for off-screen images
- Modern formats (WebP, AVIF) with fallbacks

### Animation Performance

- Respect `prefers-reduced-motion`
- Use GPU-accelerated properties (transform, opacity)
- Disable complex animations on low-end devices

## Testing

### Responsive Testing Checklist

- [ ] Test on physical devices (iOS, Android)
- [ ] Test in browser DevTools device emulation
- [ ] Test portrait and landscape orientations
- [ ] Test with different font sizes
- [ ] Test with screen readers
- [ ] Test touch gestures
- [ ] Test keyboard navigation
- [ ] Verify safe area insets on notched devices
- [ ] Test with slow network connections
- [ ] Verify form inputs don't trigger zoom

### Recommended Test Devices

- **Mobile**: iPhone SE, iPhone 14 Pro, Samsung Galaxy S21
- **Tablet**: iPad Air, iPad Pro, Samsung Galaxy Tab
- **Desktop**: 1920×1080, 2560×1440, 3840×2160

## Browser Support

- **iOS Safari**: 14+
- **Chrome Mobile**: Latest 2 versions
- **Firefox Mobile**: Latest 2 versions
- **Samsung Internet**: Latest version
- **Desktop Browsers**: Chrome, Firefox, Safari, Edge (latest versions)

## Best Practices

1. **Mobile-First Development**: Start with mobile layout, enhance for larger screens
2. **Touch Targets**: Ensure 44px minimum size for all interactive elements
3. **Font Sizes**: Use 16px minimum to prevent iOS zoom
4. **Viewport Units**: Use with caution, prefer container-based sizing
5. **Gestures**: Provide alternative interactions for non-touch devices
6. **Performance**: Optimize images, lazy load content, minimize JavaScript
7. **Accessibility**: Test with screen readers, ensure keyboard navigation
8. **Testing**: Test on real devices, not just emulators

## Future Enhancements

- [ ] Progressive Web App (PWA) support
- [ ] Offline functionality with Service Workers
- [ ] Native app-like gestures (pull-to-refresh, swipe navigation)
- [ ] Adaptive loading based on network conditions
- [ ] Device-specific optimizations (foldable devices, etc.)
- [ ] Enhanced tablet layouts with split views
- [ ] Haptic feedback for touch interactions
