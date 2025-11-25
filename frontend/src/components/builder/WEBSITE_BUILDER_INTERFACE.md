# Website Builder Interface

A comprehensive, production-ready website builder interface with split-screen editing and live preview capabilities.

## Overview

The `WebsiteBuilderInterface` component provides a professional website editing experience with:

- **Split-screen layout**: Editor sidebar (left) and live preview (right)
- **Multi-page editing**: Tab-based navigation between different pages/sections
- **Real-time preview**: Instant visual feedback as you edit
- **Auto-save functionality**: Automatic saving with visual status indicators
- **Responsive preview**: Test your site on desktop, tablet, and mobile viewports
- **Image upload**: Drag-and-drop image uploading with preview
- **Professional UI**: Clean, modern design with smooth animations

## Features

### Editor Sidebar (Left Panel)

#### Header Section
- Project name display
- Back button navigation
- Real-time save status indicator (Saving/Saved/Error)

#### Tab Navigation
- Switch between different pages (Mission, Chapter, About, etc.)
- Active tab highlighting
- Smooth tab transitions

#### Content Editing
- **Page Title**: Text input for page title
- **Heading**: Main heading input
- **Content**: Large textarea for main content with character count
- **Featured Image**: Drag-and-drop image uploader with preview

#### Action Buttons
- **Save Changes**: Manual save with loading state
- **Publish**: Publish website (optional)

### Live Preview Panel (Right Panel)

#### Preview Toolbar
- **Device Selector**: Toggle between Desktop/Tablet/Mobile views
- **Refresh**: Reload preview
- **Open in New Tab**: View in separate window

#### Preview Area
- Real-time rendering of your website
- Responsive viewport sizing
- Smooth transitions between device views
- Interactive preview with scrolling

## Usage

### Basic Implementation

```tsx
import { WebsiteBuilderInterface } from '@/components/builder/WebsiteBuilderInterface';

function MyBuilderPage() {
  const handleSave = async (pages) => {
    // Save to your backend
    await api.savePages(pages);
  };

  const handlePublish = async () => {
    // Publish website
    await api.publishSite();
  };

  return (
    <WebsiteBuilderInterface
      projectName="My Website"
      onSave={handleSave}
      onPublish={handlePublish}
      onBack={() => navigate('/dashboard')}
    />
  );
}
```

### With Initial Data

```tsx
const initialPages = [
  {
    id: 'home',
    title: 'Home',
    content: {
      id: 'home',
      title: 'Welcome Home',
      heading: 'Welcome to Our Site',
      body: 'This is the home page content...',
      image: 'https://example.com/hero.jpg',
      settings: {},
    },
  },
  {
    id: 'about',
    title: 'About',
    content: {
      id: 'about',
      title: 'About Us',
      heading: 'Our Story',
      body: 'Learn about our journey...',
      image: '',
      settings: {},
    },
  },
];

<WebsiteBuilderInterface
  projectName="Company Website"
  initialPages={initialPages}
  onSave={handleSave}
  autoSaveInterval={5000} // Auto-save every 5 seconds
/>
```

### Custom Auto-Save Interval

```tsx
<WebsiteBuilderInterface
  projectName="My Site"
  onSave={handleSave}
  autoSaveInterval={10000} // Auto-save every 10 seconds
/>
```

## Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `projectName` | `string` | `'My Website'` | Name displayed in the header |
| `initialPages` | `Page[]` | Default pages | Initial page data to load |
| `onSave` | `(pages: Page[]) => Promise<void>` | - | Callback when saving changes |
| `onPublish` | `() => void` | - | Callback when publishing |
| `onBack` | `() => void` | - | Callback for back button |
| `autoSaveInterval` | `number` | `3000` | Auto-save interval in milliseconds |

## Data Structure

### Page Type

```typescript
interface Page {
  id: string;              // Unique page identifier
  title: string;           // Tab title
  content: PageContent;    // Page content
}

interface PageContent {
  id: string;              // Content identifier
  title: string;           // Page title
  heading: string;         // Main heading
  body: string;            // Main content text
  image: string;           // Image URL or base64
  settings: Record<string, any>; // Additional settings
}
```

## Customization

### Styling

The component uses Tailwind CSS and can be customized through:

1. **Tailwind Config**: Modify colors, spacing, etc.
2. **CSS Variables**: Override theme colors
3. **Component Props**: Pass custom classes

### Preview Content

Customize the preview by modifying the `PreviewContent` component:

```tsx
function PreviewContent({ page }: { page: Page }) {
  return (
    <div className="custom-preview">
      {/* Your custom preview layout */}
      <h1>{page.content.heading}</h1>
      <p>{page.content.body}</p>
    </div>
  );
}
```

### Device Viewports

Modify viewport dimensions in `getDeviceDimensions()`:

```tsx
const getDeviceDimensions = () => {
  switch (device) {
    case 'mobile':
      return { width: '375px', height: '667px' }; // iPhone SE
    case 'tablet':
      return { width: '768px', height: '1024px' }; // iPad
    default:
      return { width: '100%', height: '100%' }; // Desktop
  }
};
```

## Advanced Features

### Auto-Save

The component automatically saves changes after a specified interval when content is modified:

```tsx
// Auto-save triggers after 3 seconds of inactivity
useEffect(() => {
  if (!isDirty || !onSave) return;

  const timer = setTimeout(async () => {
    await handleSave();
  }, autoSaveInterval);

  return () => clearTimeout(timer);
}, [pages, isDirty, autoSaveInterval]);
```

### Save Status Indicators

Visual feedback for save operations:
- **Saving**: Spinner animation
- **Saved**: Green checkmark with fade-out
- **Error**: Red X indicator

### Image Upload

Supports drag-and-drop and click-to-upload:

```tsx
const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
  const file = e.target.files?.[0];
  if (!file) return;

  const reader = new FileReader();
  reader.onloadend = () => {
    updatePageContent('image', reader.result as string);
  };
  reader.readAsDataURL(file);
};
```

## Integration Examples

### With React Router

```tsx
import { useNavigate } from 'react-router-dom';

function WebsiteBuilderPage() {
  const navigate = useNavigate();

  return (
    <WebsiteBuilderInterface
      onBack={() => navigate('/dashboard')}
      onPublish={() => navigate('/publish')}
    />
  );
}
```

### With API Integration

```tsx
import { api } from '@/lib/api';
import { toast } from 'sonner';

function WebsiteBuilderPage() {
  const handleSave = async (pages: Page[]) => {
    try {
      await api.sites.updatePages(siteId, pages);
      toast.success('Changes saved!');
    } catch (error) {
      toast.error('Failed to save changes');
      throw error;
    }
  };

  return (
    <WebsiteBuilderInterface
      onSave={handleSave}
    />
  );
}
```

### With State Management (Zustand)

```tsx
import { useSiteStore } from '@/lib/store/siteStore';

function WebsiteBuilderPage() {
  const { currentSite, updatePages } = useSiteStore();

  const handleSave = async (pages: Page[]) => {
    await updatePages(currentSite.id, pages);
  };

  return (
    <WebsiteBuilderInterface
      projectName={currentSite.name}
      initialPages={currentSite.pages}
      onSave={handleSave}
    />
  );
}
```

## Accessibility

The component includes:
- Proper ARIA labels
- Keyboard navigation support
- Focus management
- Screen reader friendly
- High contrast support

## Performance

Optimizations included:
- Debounced auto-save
- Memoized callbacks
- Lazy image loading
- Efficient re-renders
- Smooth animations with Framer Motion

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Mobile browsers (iOS Safari, Chrome Mobile)

## Dependencies

- React 18+
- Framer Motion (animations)
- Radix UI (UI components)
- Tailwind CSS (styling)
- Lucide React (icons)

## Troubleshooting

### Images not uploading
- Check file size limits
- Verify file type (PNG, JPG, GIF)
- Ensure proper permissions

### Auto-save not working
- Verify `onSave` prop is provided
- Check console for errors
- Ensure `autoSaveInterval` is set correctly

### Preview not updating
- Check if content is actually changing
- Verify `previewKey` is incrementing
- Look for console errors

## Future Enhancements

Potential additions:
- [ ] Rich text editor for content
- [ ] Undo/redo functionality
- [ ] Version history
- [ ] Collaborative editing
- [ ] Custom CSS editor
- [ ] SEO settings
- [ ] Analytics integration
- [ ] A/B testing support

## License

MIT
