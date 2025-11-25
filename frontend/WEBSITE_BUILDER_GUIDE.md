# Website Builder Interface - Complete Guide

## Overview

The Website Builder Interface is a professional, production-ready component that provides a split-screen editing experience with live preview capabilities. It's designed to match modern website builders like Webflow, Wix, and the interface shown in your screenshot.

## 🎯 Key Features

### Editor Panel (Left Side)
- **Multi-page editing** with tab navigation
- **Real-time content editing** with instant preview updates
- **Image upload** with drag-and-drop support
- **Auto-save** functionality with visual indicators
- **Character counting** for content fields
- **Clean, intuitive interface** with proper spacing and typography

### Preview Panel (Right Side)
- **Live preview** that updates as you type
- **Responsive device testing** (Desktop, Tablet, Mobile)
- **Interactive preview** with scrolling
- **Smooth transitions** between device views
- **Professional preview toolbar** with controls

## 🚀 Getting Started

### 1. Access the Builder

Navigate to the Website Builder from your dashboard:

```
http://localhost:3000/dashboard/website-builder
```

Or click the "Website Builder" card on the dashboard.

### 2. Basic Usage

The interface is divided into two main sections:

**Left Sidebar (Editor)**
- Switch between pages using tabs (Mission, Chapter, About)
- Edit page title, heading, and content
- Upload featured images
- Save changes manually or let auto-save handle it

**Right Panel (Preview)**
- See your changes in real-time
- Switch between device views
- Refresh preview if needed
- Open in new tab for full-screen view

### 3. Editing Content

1. **Select a page** by clicking its tab
2. **Edit the fields**:
   - Page Title: The title shown in browser tabs
   - Heading: Main heading displayed on the page
   - Content: Main body text
   - Featured Image: Hero/banner image
3. **Changes auto-save** after 3 seconds of inactivity
4. **Manual save** available via the "Save Changes" button

### 4. Image Upload

Two ways to add images:

**Method 1: Click to Upload**
1. Click the upload area
2. Select an image file (PNG, JPG, GIF)
3. Image appears instantly in preview

**Method 2: Drag and Drop**
1. Drag an image file from your computer
2. Drop it on the upload area
3. Image uploads and displays

### 5. Device Preview

Test your site on different devices:

- **Desktop** (default): Full-width view
- **Tablet**: 768px × 1024px viewport
- **Mobile**: 375px × 667px viewport

Click the device icons in the preview toolbar to switch views.

## 💻 Developer Integration

### Basic Implementation

```tsx
import { WebsiteBuilderInterface } from '@/components/builder';

function MyPage() {
  const handleSave = async (pages) => {
    // Save to your backend
    await fetch('/api/pages', {
      method: 'POST',
      body: JSON.stringify(pages),
    });
  };

  return (
    <WebsiteBuilderInterface
      projectName="My Website"
      onSave={handleSave}
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
      title: 'Welcome',
      heading: 'Welcome to Our Site',
      body: 'This is the home page...',
      image: '/images/hero.jpg',
      settings: {},
    },
  },
];

<WebsiteBuilderInterface
  projectName="Company Site"
  initialPages={initialPages}
  onSave={handleSave}
/>
```

### With All Features

```tsx
import { useNavigate } from 'react-router-dom';
import { toast } from 'sonner';

function WebsiteBuilderPage() {
  const navigate = useNavigate();

  const handleSave = async (pages) => {
    try {
      await api.savePages(pages);
      toast.success('Saved!');
    } catch (error) {
      toast.error('Save failed');
      throw error;
    }
  };

  const handlePublish = async () => {
    try {
      await api.publishSite();
      toast.success('Published!');
    } catch (error) {
      toast.error('Publish failed');
    }
  };

  return (
    <WebsiteBuilderInterface
      projectName="My Awesome Site"
      initialPages={myPages}
      onSave={handleSave}
      onPublish={handlePublish}
      onBack={() => navigate('/dashboard')}
      autoSaveInterval={5000}
    />
  );
}
```

## 🎨 Customization

### Modify Preview Content

Edit the `PreviewContent` component in `WebsiteBuilderInterface.tsx`:

```tsx
function PreviewContent({ page }: { page: Page }) {
  return (
    <div className="custom-layout">
      {/* Your custom preview layout */}
      <h1>{page.content.heading}</h1>
      <p>{page.content.body}</p>
    </div>
  );
}
```

### Change Device Dimensions

Modify the `getDeviceDimensions` function:

```tsx
const getDeviceDimensions = () => {
  switch (device) {
    case 'mobile':
      return { width: '390px', height: '844px' }; // iPhone 12
    case 'tablet':
      return { width: '820px', height: '1180px' }; // iPad Air
    default:
      return { width: '100%', height: '100%' };
  }
};
```

### Add More Pages

```tsx
const pages = [
  { id: 'home', title: 'Home', content: {...} },
  { id: 'about', title: 'About', content: {...} },
  { id: 'services', title: 'Services', content: {...} },
  { id: 'contact', title: 'Contact', content: {...} },
];
```

### Custom Auto-Save Interval

```tsx
<WebsiteBuilderInterface
  autoSaveInterval={10000} // 10 seconds
/>
```

## 🔧 API Integration

### Save to Backend

```tsx
const handleSave = async (pages: Page[]) => {
  const response = await fetch('/api/sites/123/pages', {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ pages }),
  });

  if (!response.ok) {
    throw new Error('Save failed');
  }
};
```

### Load from Backend

```tsx
const [pages, setPages] = useState<Page[]>([]);

useEffect(() => {
  fetch('/api/sites/123/pages')
    .then(res => res.json())
    .then(data => setPages(data.pages));
}, []);

<WebsiteBuilderInterface
  initialPages={pages}
  onSave={handleSave}
/>
```

### Publish Website

```tsx
const handlePublish = async () => {
  const response = await fetch('/api/sites/123/publish', {
    method: 'POST',
  });

  const data = await response.json();
  
  toast.success('Published!', {
    description: `Live at ${data.url}`,
  });
};
```

## 📱 Responsive Behavior

The interface is fully responsive:

- **Desktop (1024px+)**: Full split-screen layout
- **Tablet (768px-1023px)**: Collapsible sidebar
- **Mobile (<768px)**: Stacked layout with tabs

## ⚡ Performance

Optimizations included:

- **Debounced auto-save**: Prevents excessive API calls
- **Memoized callbacks**: Reduces re-renders
- **Lazy image loading**: Faster initial load
- **Efficient state updates**: Only updates changed fields
- **Smooth animations**: Hardware-accelerated with Framer Motion

## 🎯 Best Practices

### 1. Error Handling

```tsx
const handleSave = async (pages: Page[]) => {
  try {
    await api.savePages(pages);
  } catch (error) {
    console.error('Save error:', error);
    toast.error('Failed to save changes');
    throw error; // Re-throw to show error status
  }
};
```

### 2. Loading States

```tsx
const [isLoading, setIsLoading] = useState(true);

useEffect(() => {
  loadPages().finally(() => setIsLoading(false));
}, []);

if (isLoading) {
  return <LoadingSpinner />;
}

return <WebsiteBuilderInterface {...props} />;
```

### 3. Unsaved Changes Warning

```tsx
useEffect(() => {
  const handleBeforeUnload = (e: BeforeUnloadEvent) => {
    if (isDirty) {
      e.preventDefault();
      e.returnValue = '';
    }
  };

  window.addEventListener('beforeunload', handleBeforeUnload);
  return () => window.removeEventListener('beforeunload', handleBeforeUnload);
}, [isDirty]);
```

## 🐛 Troubleshooting

### Images Not Uploading

**Problem**: Images don't appear after upload

**Solutions**:
- Check file size (max 10MB)
- Verify file type (PNG, JPG, GIF only)
- Check browser console for errors
- Ensure proper CORS settings if loading from external source

### Auto-Save Not Working

**Problem**: Changes aren't being saved automatically

**Solutions**:
- Verify `onSave` prop is provided
- Check `autoSaveInterval` is set correctly
- Look for errors in browser console
- Ensure backend endpoint is working

### Preview Not Updating

**Problem**: Preview doesn't reflect changes

**Solutions**:
- Check if content is actually changing
- Try manual refresh button
- Verify `previewKey` is incrementing
- Check for JavaScript errors in console

### Performance Issues

**Problem**: Interface feels slow or laggy

**Solutions**:
- Reduce `autoSaveInterval` frequency
- Optimize preview content rendering
- Check for memory leaks in DevTools
- Reduce image sizes

## 🔐 Security Considerations

### Image Upload

```tsx
// Validate file type
const validateImage = (file: File) => {
  const validTypes = ['image/png', 'image/jpeg', 'image/gif'];
  if (!validTypes.includes(file.type)) {
    throw new Error('Invalid file type');
  }
  
  // Check file size (10MB max)
  if (file.size > 10 * 1024 * 1024) {
    throw new Error('File too large');
  }
};
```

### Content Sanitization

```tsx
import DOMPurify from 'dompurify';

const sanitizeContent = (html: string) => {
  return DOMPurify.sanitize(html);
};
```

## 📚 Additional Resources

- [Component Documentation](./src/components/builder/WEBSITE_BUILDER_INTERFACE.md)
- [API Integration Guide](../docs/API_INTEGRATION.md)
- [Accessibility Guide](../docs/ACCESSIBILITY_GUIDE.md)
- [Performance Guide](../docs/PERFORMANCE_GUIDE.md)

## 🎉 Examples

### Example 1: Blog Builder

```tsx
const blogPages = [
  { id: 'home', title: 'Home', content: {...} },
  { id: 'blog', title: 'Blog', content: {...} },
  { id: 'about', title: 'About', content: {...} },
];

<WebsiteBuilderInterface
  projectName="My Blog"
  initialPages={blogPages}
  onSave={saveBlogPages}
/>
```

### Example 2: Portfolio Builder

```tsx
const portfolioPages = [
  { id: 'work', title: 'Work', content: {...} },
  { id: 'about', title: 'About', content: {...} },
  { id: 'contact', title: 'Contact', content: {...} },
];

<WebsiteBuilderInterface
  projectName="Portfolio"
  initialPages={portfolioPages}
  onSave={savePortfolio}
/>
```

### Example 3: Landing Page Builder

```tsx
const landingPages = [
  { id: 'hero', title: 'Hero', content: {...} },
  { id: 'features', title: 'Features', content: {...} },
  { id: 'pricing', title: 'Pricing', content: {...} },
  { id: 'cta', title: 'Call to Action', content: {...} },
];

<WebsiteBuilderInterface
  projectName="Product Launch"
  initialPages={landingPages}
  onSave={saveLanding}
/>
```

## 🚀 Next Steps

1. **Try the demo**: Visit `/dashboard/website-builder`
2. **Read the docs**: Check `WEBSITE_BUILDER_INTERFACE.md`
3. **Customize**: Modify preview content and styling
4. **Integrate**: Connect to your backend API
5. **Deploy**: Build and deploy your builder!

## 📝 License

MIT
