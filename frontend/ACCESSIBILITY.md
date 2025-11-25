# Accessibility Features

This document outlines the accessibility features implemented in the Website Builder frontend application to ensure WCAG 2.1 AA compliance.

## Overview

The application is built with accessibility as a core principle, ensuring that all users, including those using assistive technologies, can effectively use the website builder.

## Key Features

### 1. Keyboard Navigation

#### Skip Links
- Skip links are provided at the top of each page to allow keyboard users to quickly navigate to main content
- Accessible via Tab key on page load
- Links include:
  - Skip to main content
  - Skip to navigation

#### Keyboard Shortcuts
- **Ctrl+Shift+T**: Toggle theme (light/dark mode)
- **Ctrl+S**: Save/submit current form
- **Esc**: Close dialogs and modals
- **?**: Show keyboard shortcuts help dialog
- **Tab**: Navigate forward through interactive elements
- **Shift+Tab**: Navigate backward through interactive elements

#### Focus Management
- All interactive elements have visible focus indicators (2px outline)
- Focus is trapped within modals and dialogs
- Focus is restored to triggering element when modals close
- Logical tab order throughout the application

### 2. ARIA Labels and Roles

#### Semantic HTML
- Proper use of semantic HTML5 elements (`<header>`, `<nav>`, `<main>`, `<aside>`)
- Heading hierarchy maintained throughout (h1 → h2 → h3)
- Form labels properly associated with inputs

#### ARIA Attributes
- `aria-label`: Descriptive labels for icon-only buttons and controls
- `aria-labelledby`: Associates elements with their labels
- `aria-describedby`: Links form fields with error messages and hints
- `aria-current`: Indicates current page in navigation
- `aria-invalid`: Marks form fields with validation errors
- `aria-required`: Indicates required form fields
- `aria-hidden`: Hides decorative icons from screen readers
- `role`: Appropriate ARIA roles for custom components

### 3. Live Regions

#### ARIA Live Regions
- Dynamic content updates are announced to screen readers
- Two priority levels:
  - **Polite**: Non-urgent updates (form saves, status changes)
  - **Assertive**: Urgent updates (errors, critical notifications)

#### Implementation
```typescript
import { useAnnouncer } from '@/lib/hooks/useAnnouncer';

const { announce } = useAnnouncer();
announce('Website generated successfully', 'polite');
announce('Error: Failed to save', 'assertive');
```

### 4. Form Accessibility

#### Form Field Component
- Automatic association of labels, inputs, errors, and hints
- Error messages linked via `aria-describedby`
- Required fields marked with `aria-required` and visual indicator
- Validation errors announced to screen readers

#### Example Usage
```typescript
<FormField
  id="email"
  label="Email Address"
  error={errors.email?.message}
  hint="We'll never share your email"
  required
>
  <Input type="email" />
</FormField>
```

### 5. Focus Trap

#### Modal and Dialog Focus Management
- Focus is trapped within open modals/dialogs
- Tab cycles through focusable elements within the modal
- Shift+Tab cycles backward
- Escape key closes the modal
- Focus returns to trigger element on close

#### Implementation
```typescript
import { useFocusTrap } from '@/lib/hooks/useFocusTrap';

const focusTrapRef = useFocusTrap<HTMLDivElement>(isOpen);
```

### 6. Visual Accessibility

#### Color Contrast
- Minimum 4.5:1 contrast ratio for normal text
- Minimum 3:1 contrast ratio for large text
- Color is never the only means of conveying information

#### Focus Indicators
- 2px solid outline on all focusable elements
- High contrast focus indicators in both light and dark modes
- Focus indicators visible on all interactive elements

#### Responsive Text
- Text can be resized up to 200% without loss of functionality
- Relative units (rem, em) used for font sizes
- No horizontal scrolling required at 200% zoom

### 7. Reduced Motion Support

#### Prefers Reduced Motion
- Respects user's motion preferences
- Animations disabled or simplified when `prefers-reduced-motion: reduce` is set
- Transitions reduced to minimal duration

#### CSS Implementation
```css
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

### 8. Screen Reader Support

#### Screen Reader Only Content
- `.sr-only` utility class for screen reader only content
- Important information not conveyed visually is provided to screen readers
- Icon buttons include text alternatives

#### Descriptive Labels
- All images have appropriate alt text
- Icon-only buttons have aria-labels
- Form inputs have associated labels
- Links have descriptive text

## Custom Hooks

### useKeyboardShortcut
Handles keyboard shortcuts throughout the application.

```typescript
useKeyboardShortcut(callback, {
  key: 's',
  ctrlKey: true,
  enabled: true,
});
```

### useFocusTrap
Traps focus within a container (modals, dialogs).

```typescript
const focusTrapRef = useFocusTrap<HTMLDivElement>(isActive);
```

### useAnnouncer
Announces messages to screen readers via ARIA live regions.

```typescript
const { announce } = useAnnouncer();
announce('Message', 'polite' | 'assertive');
```

## Components

### Accessible Components

#### SkipLink
Provides skip navigation links for keyboard users.

```typescript
<SkipLink href="#main-content">Skip to main content</SkipLink>
```

#### LiveRegion
ARIA live region for dynamic content announcements.

```typescript
<LiveRegion message="Content updated" priority="polite" />
```

#### FormField
Accessible form field with automatic ARIA associations.

```typescript
<FormField id="name" label="Name" error={error} required>
  <Input />
</FormField>
```

#### AccessibleDialog
Dialog component with focus trap and keyboard support.

```typescript
<AccessibleDialog>
  <AccessibleDialogContent>
    <AccessibleDialogTitle>Title</AccessibleDialogTitle>
    <AccessibleDialogDescription>Description</AccessibleDialogDescription>
  </AccessibleDialogContent>
</AccessibleDialog>
```

## Testing

### Manual Testing Checklist

- [ ] All functionality accessible via keyboard
- [ ] Focus indicators visible on all interactive elements
- [ ] Skip links work correctly
- [ ] Screen reader announces dynamic content
- [ ] Form errors properly associated and announced
- [ ] Modals trap focus correctly
- [ ] Keyboard shortcuts work as expected
- [ ] Color contrast meets WCAG AA standards
- [ ] Text resizable to 200% without issues
- [ ] Reduced motion preferences respected

### Automated Testing

Run accessibility tests with:
```bash
npm run test:a11y
```

### Screen Reader Testing

Recommended screen readers for testing:
- **Windows**: NVDA (free), JAWS
- **macOS**: VoiceOver (built-in)
- **Linux**: Orca
- **Mobile**: TalkBack (Android), VoiceOver (iOS)

## Resources

- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [ARIA Authoring Practices](https://www.w3.org/WAI/ARIA/apg/)
- [WebAIM](https://webaim.org/)
- [A11y Project](https://www.a11yproject.com/)

## Compliance

This application aims to meet WCAG 2.1 Level AA compliance standards:

- ✅ Perceivable: Content is presented in ways users can perceive
- ✅ Operable: Interface components are operable via keyboard
- ✅ Understandable: Information and operation are understandable
- ✅ Robust: Content works with current and future assistive technologies

## Future Improvements

- [ ] Add more comprehensive keyboard shortcut customization
- [ ] Implement high contrast mode
- [ ] Add text-to-speech for content reading
- [ ] Enhance mobile accessibility features
- [ ] Add accessibility settings panel
