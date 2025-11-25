# SitePreview Component Implementation

## Overview

Successfully implemented the SitePreview component with all required features for task 9 of the modern-website-builder-frontend spec.

## Components Created

### 1. SitePreview.tsx
Main component that provides an interactive iframe-based preview of generated websites.

**Features:**
- ✅ Sandboxed iframe rendering with `allow-scripts` and `allow-same-origin`
- ✅ HTML/CSS/JS code injection into iframe
- ✅ Responsive viewport controls (mobile, tablet, desktop)
- ✅ Zoom controls (25% - 200%)
- ✅ Element selection with click event handling
- ✅ Element highlighting overlay system
- ✅ Fullscreen mode support
- ✅ Refresh functionality
- ✅ Screenshot capture (placeholder for html2canvas integration)

**Props:**
```typescript
interface SitePreviewProps {
  htmlCode: string;
  cssCode?: string;
  jsCode?: string;
  onElementSelect?: (element: HTMLElement) => void;
  viewport?: 'mobile' | 'tablet' | 'desktop';
  editable?: boolean;
  className?: string;
}
```

### 2. ViewportControls.tsx
Toolbar component for switching between device viewports.

**Features:**
- ✅ Mobile (375 × 667px)
- ✅ Tablet (768 × 1024px)
- ✅ Desktop (1440 × 900px)
- ✅ Visual feedback for active viewport
- ✅ Tooltips with device dimensions
- ✅ Keyboard accessible

### 3. PreviewControls.tsx
Toolbar component for zoom, refresh, screenshot, and fullscreen controls.

**Features:**
- ✅ Zoom in/out buttons
- ✅ Zoom percentage display with reset
- ✅ Refresh button to reload iframe
- ✅ Screenshot capture button
- ✅ Fullscreen toggle
- ✅ Tooltips for all controls
- ✅ Disabled states for zoom limits

### 4. ElementHighlight.tsx
Visual overlay component for highlighting selected elements.

**Features:**
- ✅ Border highlight with primary color
- ✅ Corner handles for visual feedback
- ✅ Element dimensions display
- ✅ Close button to clear selection
- ✅ Zoom-aware positioning
- ✅ Smooth transitions

### 5. SitePreviewExample.tsx
Complete example demonstrating all SitePreview features.

**Features:**
- ✅ Sample HTML/CSS/JS code
- ✅ Code viewer with tabs
- ✅ Element selection feedback
- ✅ Toggle code visibility
- ✅ Beautiful example website (hero + features)

## File Structure

```
frontend/src/components/builder/
├── SitePreview.tsx           # Main preview component
├── ViewportControls.tsx      # Viewport switcher
├── PreviewControls.tsx       # Zoom/refresh/fullscreen controls
├── ElementHighlight.tsx      # Element selection overlay
├── SitePreviewExample.tsx    # Example/demo component
├── index.ts                  # Updated exports
└── README.md                 # Updated documentation

frontend/src/pages/
└── PreviewTestPage.tsx       # Test page for preview component

frontend/src/router/
└── index.tsx                 # Added preview-test route
```

## Technical Implementation

### Iframe Security
- Uses `sandbox` attribute with `allow-scripts` and `allow-same-origin`
- Prevents default link navigation to keep users in preview
- Isolated document context for safe code execution

### Code Injection
- Builds complete HTML document with DOCTYPE
- Injects CSS in `<style>` tag
- Injects JS in `<script>` tag
- Includes base styles for consistent rendering

### Element Selection
- Click event listener on iframe document
- Prevents default behavior and propagation
- Calculates element bounding rect
- Triggers callback with selected element
- Visual highlight overlay with dimensions

### Viewport Responsiveness
- Predefined dimensions for common devices
- Smooth transitions between viewports
- Maintains aspect ratios
- Centered preview in container

### Zoom Functionality
- CSS transform scale on iframe
- Transform origin at top-left
- Adjusts container dimensions
- Limits: 25% minimum, 200% maximum
- Zoom-aware element highlighting

### Fullscreen Mode
- Uses Fullscreen API
- Listens for fullscreen changes
- Updates UI state accordingly
- Escape key exits fullscreen

## Requirements Satisfied

✅ **Requirement 2.1**: Site preview with iframe rendering
- Sandboxed iframe with HTML/CSS/JS injection
- Responsive viewport controls
- Zoom and fullscreen capabilities

✅ **Requirement 2.2**: Element selection and highlighting
- Click-to-select functionality
- Visual highlight overlay
- Element information display
- Callback for parent components

## Testing

### Build Verification
- ✅ TypeScript compilation successful
- ✅ No type errors
- ✅ Vite build successful
- ✅ All components properly exported

### Manual Testing Available
Navigate to `/dashboard/preview-test` to see the component in action with:
- Example website with hero and features
- All viewport sizes
- Zoom controls
- Element selection
- Code viewer

## Usage Example

```tsx
import { SitePreview } from '@/components/builder';

function MyPage() {
  const handleElementSelect = (element: HTMLElement) => {
    console.log('Selected:', element.tagName);
  };

  return (
    <SitePreview
      htmlCode="<h1>Hello World</h1>"
      cssCode="h1 { color: blue; }"
      jsCode="console.log('loaded');"
      onElementSelect={handleElementSelect}
      viewport="desktop"
      editable={true}
    />
  );
}
```

## Future Enhancements

1. **Screenshot Capture**: Integrate html2canvas library for actual screenshot functionality
2. **Element Editing**: Add inline editing toolbar for selected elements
3. **Responsive Breakpoints**: Add custom viewport size input
4. **Performance**: Optimize iframe re-rendering with memoization
5. **Accessibility**: Add keyboard shortcuts for viewport switching
6. **Export**: Add export functionality for preview as image/PDF

## Notes

- Screenshot functionality is a placeholder and requires html2canvas library integration
- Element highlighting works best with zoom levels between 50% and 150%
- Fullscreen mode requires user gesture (button click) to activate
- Preview automatically prevents link navigation for better UX

## Dependencies Used

- React 18
- Lucide React (icons)
- Radix UI (tooltips, buttons)
- Tailwind CSS (styling)
- TypeScript (type safety)

All dependencies were already present in the project.
