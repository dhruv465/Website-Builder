# UI Components

This directory contains all the UI components for the website builder frontend.

## Structure

- `ui/` - ShadCN UI components (buttons, cards, dialogs, etc.)
- `theme-provider.tsx` - Dark mode theme provider
- `error-boundary.tsx` - Error boundary component for error handling
- `ui-showcase.tsx` - Demo component showcasing all UI components

## Installed ShadCN UI Components

The following components have been installed and configured:

- **Alert** - Contextual feedback messages
- **Badge** - Status indicators and labels
- **Button** - Interactive buttons with multiple variants
- **Card** - Container component for content
- **Dialog** - Modal dialogs
- **Dropdown Menu** - Contextual menus
- **Input** - Text input fields
- **Popover** - Floating content panels
- **Progress** - Progress indicators
- **Select** - Dropdown select inputs
- **Separator** - Visual dividers
- **Tabs** - Tabbed content navigation
- **Textarea** - Multi-line text input
- **Tooltip** - Hover tooltips

## Custom Components

### LoadingSpinner

A flexible loading spinner component with multiple sizes and variants.

```tsx
import { LoadingSpinner } from '@/components/ui/loading-spinner'

// Basic usage
<LoadingSpinner />

// With size and variant
<LoadingSpinner size="lg" variant="muted" label="Loading..." />

// Fullscreen loading
<LoadingSpinnerFullscreen label="Processing..." />

// Inline for buttons
<Button disabled>
  <LoadingSpinnerInline className="mr-2" />
  Loading
</Button>
```

### ErrorBoundary

A React error boundary component that catches JavaScript errors and displays a fallback UI.

```tsx
import { ErrorBoundary } from '@/components/error-boundary'

// Basic usage
<ErrorBoundary>
  <YourComponent />
</ErrorBoundary>

// With error details (development mode)
<ErrorBoundary showDetails={true}>
  <YourComponent />
</ErrorBoundary>

// With custom error handler
<ErrorBoundary onError={(error, errorInfo) => {
  // Log to error tracking service
  console.error(error, errorInfo)
}}>
  <YourComponent />
</ErrorBoundary>
```

### ThemeProvider

Provides dark mode support using next-themes pattern.

```tsx
import { ThemeProvider, useTheme } from '@/components/theme-provider'

// Wrap your app
<ThemeProvider defaultTheme="system" storageKey="ui-theme">
  <App />
</ThemeProvider>

// Use in components
function ThemeToggle() {
  const { theme, setTheme } = useTheme()
  
  return (
    <Button onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}>
      Toggle Theme
    </Button>
  )
}
```

## Theme Configuration

The theme is configured in `tailwind.config.ts` with CSS variables defined in `src/index.css`.

### Color Tokens

- `background` / `foreground` - Base colors
- `primary` / `primary-foreground` - Primary action colors
- `secondary` / `secondary-foreground` - Secondary action colors
- `destructive` / `destructive-foreground` - Destructive action colors
- `muted` / `muted-foreground` - Muted/disabled colors
- `accent` / `accent-foreground` - Accent colors
- `card` / `card-foreground` - Card background colors
- `popover` / `popover-foreground` - Popover background colors
- `border` - Border color
- `input` - Input border color
- `ring` - Focus ring color

### Dark Mode

Dark mode is enabled by default and can be toggled using the ThemeProvider. The theme automatically respects the user's system preference when set to "system" mode.

## Usage Examples

See `ui-showcase.tsx` for comprehensive examples of all components in action.

## Accessibility

All components follow WCAG 2.1 AA guidelines:

- Proper ARIA labels and roles
- Keyboard navigation support
- Focus indicators
- Color contrast ratios of 4.5:1 or higher
- Screen reader compatibility

## Animation

Components use Framer Motion and Tailwind CSS animations for smooth transitions. Animations respect the user's `prefers-reduced-motion` setting.
