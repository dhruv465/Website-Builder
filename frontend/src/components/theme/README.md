# Theme Components

This directory contains all components related to theme selection, customization, and management for the website builder.

## Components

### ThemeSelector

The main component that provides a complete theme browsing and selection interface.

**Features:**
- Grid and list view modes
- Search functionality
- Category filtering
- Theme preview
- Theme customization
- Responsive design

**Usage:**
```tsx
import { ThemeSelector } from '@/components/theme';

function MyComponent() {
  const handleThemeSelect = (theme: Theme) => {
    console.log('Selected theme:', theme);
  };

  return (
    <ThemeSelector
      themes={themes}
      selectedThemeId={currentThemeId}
      onThemeSelect={handleThemeSelect}
      onThemeApply={handleThemeApply}
    />
  );
}
```

### ThemeCard

Displays a single theme with preview thumbnail, metadata, and action buttons.

**Props:**
- `theme`: Theme object
- `isSelected`: Whether this theme is currently selected
- `onPreview`: Callback when preview button is clicked
- `onSelect`: Callback when select button is clicked

### ThemeGrid

Responsive grid layout for displaying multiple theme cards.

**Props:**
- `themes`: Array of themes to display
- `selectedThemeId`: ID of currently selected theme
- `onPreview`: Preview callback
- `onSelect`: Selection callback

### ThemePreview

Full-screen modal for previewing a theme with detailed information.

**Features:**
- Color palette display
- Typography preview
- Full-size preview image
- Apply theme action

### ThemeCustomizer

Modal dialog for customizing theme colors and fonts.

**Features:**
- Color picker for all theme colors
- Font family inputs
- Live preview
- Reset to defaults
- Save customization

### ColorPicker

Reusable color picker component using react-colorful.

**Features:**
- Visual color picker
- Hex input field
- Popover interface

## Utilities

### themeUtils.ts

Utility functions for theme management:

- `generateThemeVariables()`: Generate CSS variables from theme colors
- `generateThemeCSS()`: Generate complete CSS for a theme
- `injectThemeIntoIframe()`: Apply theme to an iframe
- `applyThemeToDocument()`: Apply theme to current document
- `validateThemeAccessibility()`: Check WCAG contrast requirements

## Hooks

### useTheme

Custom hook for theme management:

```tsx
const {
  themes,
  selectedTheme,
  isLoading,
  error,
  selectTheme,
  applyTheme,
  clearTheme,
} = useTheme();
```

## API Integration

Theme API functions are available in `@/lib/api/themes`:

- `fetchThemes()`: Get all themes
- `fetchThemeById()`: Get specific theme
- `applyThemeToSite()`: Apply theme to a site
- `saveCustomTheme()`: Save custom theme
- `fetchSessionThemes()`: Get session themes
- `deleteCustomTheme()`: Delete custom theme

## Mock Data

Mock theme data is available in `@/lib/data/mockThemes.ts` for development and testing.

## Testing

Visit `/dashboard/theme-test` to test the theme selector functionality.

## Accessibility

All theme components follow WCAG 2.1 AA guidelines:
- Keyboard navigation support
- ARIA labels and roles
- Focus management
- Color contrast validation
- Screen reader compatibility

## Future Enhancements

- Theme marketplace integration
- Community-contributed themes
- Theme versioning
- Theme export/import
- Advanced customization options
- Theme templates
- AI-powered theme suggestions
