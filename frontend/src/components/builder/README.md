# Builder Components

This directory contains the BuilderForm component and its sub-components for creating website requirements through multiple input methods.

## Components

### BuilderForm

The main form component that orchestrates all input methods and configuration options.

**Features:**
- Multi-tab interface (Text, Chat, Voice)
- Form validation with React Hook Form and Zod
- Auto-save to localStorage with debouncing
- Character count with visual feedback
- Framework selection
- Feature checkboxes
- Loading states

**Usage:**
```tsx
import { BuilderForm } from '@/components/builder';
import { BuilderFormData } from '@/lib/types/site';

function MyPage() {
  const handleSubmit = async (data: BuilderFormData) => {
    // Handle form submission
    console.log(data);
  };

  return <BuilderForm onSubmit={handleSubmit} isLoading={false} />;
}
```

### ChatInterface

A chat-style interface for conversational requirement gathering.

**Features:**
- Message history display
- User and assistant message bubbles
- Auto-scroll to latest message
- Timestamp display

### VoiceInput

Voice-to-text input using the Web Speech API.

**Features:**
- Browser speech recognition
- Visual recording indicator
- Error handling for unsupported browsers
- Real-time transcript capture

**Browser Support:**
- Chrome/Edge: Full support
- Safari: Full support
- Firefox: Not supported

### FrameworkSelector

Visual framework selection with cards.

**Features:**
- React, Vue, Next.js, HTML options
- Visual selection feedback
- Keyboard navigation support
- Accessible with ARIA attributes

### FeatureCheckboxes

Multi-select checkboxes for common website features.

**Features:**
- 10 common website features
- Descriptions for each feature
- Accessible checkbox implementation
- Responsive grid layout

## Form Data Structure

```typescript
interface BuilderFormData {
  requirements: string;
  framework?: 'react' | 'vue' | 'nextjs' | 'html';
  designStyle?: 'modern' | 'minimal' | 'corporate' | 'creative';
  features?: string[];
  colorScheme?: string;
}
```

## Auto-save

The form automatically saves to localStorage with a 1-second debounce. The saved data is restored when the user returns to the form.

**Storage Key:** `builder-form-draft`

## Validation

Form validation is handled by Zod with the following rules:
- Requirements: 10-5000 characters
- Framework: Optional enum
- Design Style: Optional enum
- Features: Optional array
- Color Scheme: Optional string

## Accessibility

All components follow WCAG 2.1 AA guidelines:
- Proper ARIA labels and roles
- Keyboard navigation support
- Focus indicators
- Screen reader compatibility
- Error message associations

---

## SitePreview

An interactive iframe-based preview component for displaying generated websites with viewport controls, zoom, and element selection.

**Features:**
- Sandboxed iframe rendering
- HTML/CSS/JS code injection
- Responsive viewport controls (mobile, tablet, desktop)
- Zoom controls (25% - 200%)
- Screenshot capture functionality
- Element selection with click handling
- Element highlighting overlay system
- Fullscreen mode
- Refresh functionality

**Usage:**
```tsx
import { SitePreview } from '@/components/builder';

function PreviewPage() {
  const handleElementSelect = (element: HTMLElement) => {
    console.log('Selected:', element);
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

**Props:**
```typescript
interface SitePreviewProps {
  htmlCode: string;              // HTML content to render
  cssCode?: string;              // CSS styles
  jsCode?: string;               // JavaScript code
  onElementSelect?: (element: HTMLElement) => void;  // Element click handler
  viewport?: 'mobile' | 'tablet' | 'desktop';        // Initial viewport
  editable?: boolean;            // Enable element selection
  className?: string;            // Additional CSS classes
}
```

### ViewportControls

Toolbar for switching between device viewports.

**Viewports:**
- Mobile: 375 × 667px
- Tablet: 768 × 1024px
- Desktop: 1440 × 900px

### PreviewControls

Toolbar for zoom, refresh, screenshot, and fullscreen controls.

**Controls:**
- Zoom In/Out: Adjust preview scale
- Zoom Reset: Return to 100%
- Refresh: Reload iframe content
- Screenshot: Capture preview (requires html2canvas)
- Fullscreen: Toggle fullscreen mode

### ElementHighlight

Visual overlay for selected elements in the preview.

**Features:**
- Border highlight with primary color
- Corner handles for visual feedback
- Element dimensions display
- Close button to clear selection
- Zoom-aware positioning

### SitePreviewExample

A complete example demonstrating all SitePreview features with sample HTML/CSS/JS code.

**Features:**
- Example website with hero and features sections
- Code viewer with syntax highlighting
- Element selection feedback
- Toggle code visibility

## Security

The iframe uses the `sandbox` attribute with `allow-scripts` and `allow-same-origin` to provide a secure preview environment. Link navigation is prevented by default to keep users in the preview context.
