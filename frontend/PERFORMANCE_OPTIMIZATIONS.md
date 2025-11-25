# Performance Optimizations

This document outlines all performance optimizations implemented in the website builder frontend.

## Table of Contents

1. [Code Splitting](#code-splitting)
2. [Lazy Loading](#lazy-loading)
3. [Virtual Scrolling](#virtual-scrolling)
4. [Debouncing & Throttling](#debouncing--throttling)
5. [Memoization](#memoization)
6. [Image Optimization](#image-optimization)
7. [Font Optimization](#font-optimization)
8. [Build Optimization](#build-optimization)
9. [Prefetching](#prefetching)

## Code Splitting

### Route-Based Code Splitting

All page components are lazy-loaded using React's `lazy()` and `Suspense`:

```typescript
// frontend/src/router/index.tsx
const DashboardPage = lazy(() => import('../pages/DashboardPage'));
const ProjectsPage = lazy(() => import('../pages/ProjectsPage'));
```

**Benefits:**
- Reduces initial bundle size
- Faster initial page load
- Only loads code when needed

### Component-Based Code Splitting

Heavy components are lazy-loaded:

```typescript
// Monaco Editor (code editor)
import { LazyCodeEditor } from '@/components/shared/LazyCodeEditor';

// Recharts (charting library)
import { LazyChart } from '@/components/shared/LazyChart';
```

**Usage:**
```tsx
<LazyCodeEditor
  value={code}
  onChange={setCode}
  language="javascript"
  height="400px"
/>
```

## Lazy Loading

### Images

Use the `LazyImage` component for automatic lazy loading:

```tsx
import { LazyImage } from '@/components/shared';

<LazyImage
  src="/path/to/image.jpg"
  alt="Description"
  className="w-full h-auto"
/>
```

**Features:**
- Intersection Observer API
- Automatic loading when visible
- Placeholder skeleton while loading
- Error handling

### Custom Hook

Use `useIntersectionObserver` for custom lazy loading:

```tsx
import { useIntersectionObserver } from '@/lib/hooks';

const { ref, isVisible } = useIntersectionObserver({
  threshold: 0.1,
  freezeOnceVisible: true,
});

<div ref={ref}>
  {isVisible && <ExpensiveComponent />}
</div>
```

## Virtual Scrolling

For long lists (logs, project history), use `VirtualList`:

```tsx
import { VirtualList } from '@/components/shared';

<VirtualList
  items={logEntries}
  height={600}
  itemHeight={50}
  renderItem={(log, index) => (
    <div key={index} className="p-2">
      {log.message}
    </div>
  )}
/>
```

**Benefits:**
- Only renders visible items
- Handles thousands of items smoothly
- Minimal memory footprint

## Debouncing & Throttling

### Debounce Hook

Use for search inputs and filters:

```tsx
import { useDebounce } from '@/lib/hooks';

const [searchQuery, setSearchQuery] = useState('');
const debouncedSearch = useDebounce(searchQuery, 300);

// Use debouncedSearch for API calls or filtering
useEffect(() => {
  // API call with debouncedSearch
}, [debouncedSearch]);
```

### Utility Functions

```typescript
import { debounce, throttle } from '@/lib/utils/performance';

// Debounce: Wait for user to stop typing
const handleSearch = debounce((query: string) => {
  // API call
}, 300);

// Throttle: Limit execution rate
const handleScroll = throttle(() => {
  // Scroll handling
}, 100);
```

## Memoization

### Component Memoization

Use `React.memo` for expensive components:

```tsx
const ProjectCard = React.memo<ProjectCardProps>(({ site, ...props }) => {
  // Component implementation
});
```

### Value Memoization

Use `useMemo` for expensive computations:

```tsx
const filteredSites = useMemo(() => {
  return sites.filter(site => 
    site.name.toLowerCase().includes(searchQuery.toLowerCase())
  );
}, [sites, searchQuery]);
```

### Callback Memoization

Use `useCallback` for stable function references:

```tsx
const handleDelete = useCallback((id: string) => {
  // Delete logic
}, []);
```

## Image Optimization

### Responsive Images

```tsx
<LazyImage
  src="/images/hero.jpg"
  alt="Hero image"
  srcSet="/images/hero-320w.jpg 320w,
          /images/hero-640w.jpg 640w,
          /images/hero-1280w.jpg 1280w"
  sizes="(max-width: 640px) 100vw,
         (max-width: 1024px) 50vw,
         33vw"
/>
```

### Utility Functions

```typescript
import { generateSrcSet, generateSizes } from '@/lib/utils/performance';

const srcSet = generateSrcSet('/images/hero.jpg', [320, 640, 1280]);
const sizes = generateSizes({
  '(max-width: 640px)': '100vw',
  '(max-width: 1024px)': '50vw',
  default: '33vw',
});
```

### Best Practices

- Use modern formats (WebP, AVIF)
- Provide multiple sizes
- Use `loading="lazy"` attribute
- Optimize image dimensions
- Compress images

## Font Optimization

### CSS Configuration

```css
/* frontend/src/index.css */
body {
  font-display: swap; /* Show fallback font while loading */
}

@font-face {
  font-display: swap;
}
```

### Preload Critical Fonts

```typescript
import { preloadResources } from '@/lib/utils/performance';

preloadResources([
  '/fonts/inter-var.woff2',
], 'font');
```

## Build Optimization

### Vite Configuration

```typescript
// frontend/vite.config.ts
export default defineConfig({
  build: {
    rollupOptions: {
      output: {
        manualChunks: (id) => {
          // React core
          if (id.includes('node_modules/react')) {
            return 'react-vendor';
          }
          // Animations
          if (id.includes('node_modules/framer-motion')) {
            return 'animations';
          }
          // UI components
          if (id.includes('node_modules/@radix-ui')) {
            return 'ui-vendor';
          }
          // Charts (lazy loaded)
          if (id.includes('node_modules/recharts')) {
            return 'charts';
          }
        },
      },
    },
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true, // Remove console.log in production
        drop_debugger: true,
      },
    },
  },
});
```

### Bundle Analysis

```bash
# Install bundle analyzer
npm install --save-dev rollup-plugin-visualizer

# Build and analyze
npm run build
```

## Prefetching

### Prefetch Links

Use `PrefetchLink` for anticipated navigation:

```tsx
import { PrefetchLink } from '@/components/shared';

// Prefetch on hover
<PrefetchLink to="/dashboard/projects" prefetch="hover">
  View Projects
</PrefetchLink>

// Prefetch when visible
<PrefetchLink to="/dashboard/builder" prefetch="visible">
  Create New Site
</PrefetchLink>
```

### Manual Prefetching

```typescript
import { prefetchResources } from '@/lib/utils/performance';

// Prefetch routes user is likely to visit
prefetchResources([
  '/dashboard/projects',
  '/dashboard/builder',
]);
```

## Performance Monitoring

### Metrics to Track

- **First Contentful Paint (FCP)**: < 1.8s
- **Largest Contentful Paint (LCP)**: < 2.5s
- **Time to Interactive (TTI)**: < 3.8s
- **Total Blocking Time (TBT)**: < 200ms
- **Cumulative Layout Shift (CLS)**: < 0.1

### Tools

- Chrome DevTools Performance tab
- Lighthouse
- Web Vitals extension
- React DevTools Profiler

## Best Practices

1. **Always use lazy loading for:**
   - Route components
   - Heavy libraries (Monaco, Charts)
   - Images below the fold

2. **Use virtual scrolling for:**
   - Lists with > 100 items
   - Log viewers
   - Project history

3. **Debounce/throttle:**
   - Search inputs (300ms debounce)
   - Scroll handlers (100ms throttle)
   - Resize handlers (100ms throttle)

4. **Memoize:**
   - Expensive computations
   - Filtered/sorted lists
   - Components that receive stable props

5. **Optimize images:**
   - Use modern formats
   - Provide multiple sizes
   - Lazy load below fold
   - Compress appropriately

## Checklist

- [x] Route-based code splitting
- [x] Component lazy loading
- [x] Virtual scrolling for long lists
- [x] Debounced search inputs
- [x] Memoized components and values
- [x] Lazy-loaded images
- [x] Font optimization with font-display: swap
- [x] Build optimization with manual chunks
- [x] Prefetching for anticipated navigation
- [x] Loading skeletons with Suspense

## Future Optimizations

- [ ] Service Worker for offline support
- [ ] HTTP/2 Server Push
- [ ] Resource hints (preconnect, dns-prefetch)
- [ ] Progressive Web App (PWA)
- [ ] Edge caching with CDN
- [ ] Image CDN integration
- [ ] Bundle size monitoring in CI/CD
