# WYSIWYG Editor Implementation

## Overview

The WYSIWYG (What You See Is What You Get) editor provides live, in-place editing capabilities for generated websites. Users can click on any element in the preview, edit its content and styles, and save changes back to the backend.

## Components

### 1. WYSIWYGEditor

The main editor component that manages the editing state, history, and synchronization.

**Features:**
- Element selection and highlighting
- Real-time content editing
- Style editing (color, font size, alignment)
- Undo/Redo functionality with full history tracking
- Code synchronization between DOM and stored code
- Auto-save with API integration
- Unsaved changes indicator

**Props:**
```typescript
interface WYSIWYGEditorProps {
  siteId: string;                    // Site ID for saving
  iframeRef: React.RefObject<HTMLIFrameElement>;  // Reference to preview iframe
  htmlCode: string;                  // Current HTML code
  cssCode?: string;                  // Current CSS code
  jsCode?: string;                   // Current JS code
  onCodeUpdate?: (html: string, css?: string, js?: string) => void;  // Code update callback
  onSaveSuccess?: () => void;        // Save success callback
  onSaveError?: (error: Error) => void;  // Save error callback
  className?: string;
}
```

**Usage:**
```tsx
import { WYSIWYGEditor } from '@/components/builder';

const iframeRef = useRef<HTMLIFrameElement>(null);

<WYSIWYGEditor
  siteId="site-123"
  iframeRef={iframeRef}
  htmlCode={htmlCode}
  cssCode={cssCode}
  jsCode={jsCode}
  onCodeUpdate={(html, css, js) => {
    setHtmlCode(html);
    setCssCode(css);
    setJsCode(js);
  }}
  onSaveSuccess={() => console.log('Saved!')}
  onSaveError={(error) => console.error('Save failed:', error)}
/>
```

### 2. ElementToolbar

A floating toolbar that appears when an element is selected, providing editing controls.

**Features:**
- Text content editing with textarea
- Color picker for text color
- Font size selector (12px - 48px)
- Text alignment controls (left, center, right)
- Element deletion with confirmation
- Edit mode toggle

**Props:**
```typescript
interface ElementToolbarProps {
  element: HTMLElement;              // Selected element
  rect: DOMRect;                     // Element bounding rect
  isEditing: boolean;                // Edit mode state
  onTextEdit: (content: string) => void;  // Text edit callback
  onStyleEdit: (styles: StyleEdit) => void;  // Style edit callback
  onDelete: () => void;              // Delete callback
  onClose: () => void;               // Close toolbar callback
  onEditModeChange: (isEditing: boolean) => void;  // Edit mode change callback
  className?: string;
}
```

**Style Edit Interface:**
```typescript
interface StyleEdit {
  color?: string;        // Hex color value
  fontSize?: string;     // Font size with unit (e.g., "16px")
  textAlign?: string;    // Text alignment ("left", "center", "right")
  fontWeight?: string;   // Font weight
  fontStyle?: string;    // Font style
}
```

### 3. VersionHistory

Displays a list of site versions with restore and preview capabilities.

**Features:**
- Chronological version list (newest first)
- Version metadata (number, date, description)
- Current version indicator
- Version restore with confirmation
- Version preview
- Code statistics (HTML, CSS, JS character counts)

**Props:**
```typescript
interface VersionHistoryProps {
  versions: SiteVersion[];           // Array of versions
  currentVersionId?: string;         // Current version ID
  onVersionRestore?: (version: SiteVersion) => void;  // Restore callback
  onVersionPreview?: (version: SiteVersion) => void;  // Preview callback
  className?: string;
}
```

## Edit History System

The editor maintains a complete history of all edits for undo/redo functionality.

**History Entry Structure:**
```typescript
interface EditHistoryEntry {
  element: HTMLElement;              // Edited element
  previousContent: string;           // Content before edit
  newContent: string;                // Content after edit
  previousStyles: Record<string, string>;  // Styles before edit
  newStyles: Record<string, string>;       // Styles after edit
  timestamp: number;                 // Edit timestamp
}
```

**History Management:**
- Each edit creates a new history entry
- History is maintained as an array with a current index pointer
- Undo moves the index backward and restores previous state
- Redo moves the index forward and applies new state
- New edits after undo truncate the history from the current position

## Code Synchronization

The editor keeps the DOM and stored code in sync:

1. **DOM to Code:** When elements are edited, the editor extracts the updated HTML from the iframe's document body
2. **Style Extraction:** Inline styles are preserved, and new styles are added to the CSS code
3. **Real-time Updates:** Changes are immediately reflected in the preview
4. **Save to Backend:** The `updateCode` API is called to persist changes

**Synchronization Flow:**
```
User Edit → Update DOM → Extract HTML → Update State → Save to Backend
```

## API Integration

The editor integrates with the backend through the code API:

**Update Code Endpoint:**
```typescript
await updateCode({
  site_id: siteId,
  html_code: updatedHtml,
  css_code: updatedCss,
  js_code: updatedJs,
  change_description: 'WYSIWYG edit at [timestamp]',
});
```

**Response:**
```typescript
interface CodeResponse {
  site_id: string;
  html_code: string;
  css_code?: string;
  js_code?: string;
  version_number: number;
}
```

## Keyboard Shortcuts

The editor supports keyboard shortcuts for common actions:

- **Ctrl+Z / Cmd+Z:** Undo last edit
- **Ctrl+Y / Cmd+Y:** Redo last undone edit
- **Ctrl+S / Cmd+S:** Save changes (can be implemented)
- **Escape:** Close element toolbar

## Element Selection

Elements are selected by clicking on them in the preview iframe:

1. Click event is captured in the iframe
2. Event is prevented from default behavior
3. Target element is identified
4. Element's bounding rect is calculated
5. ElementToolbar is positioned above the element
6. Highlight overlay is displayed around the element

**Selection Restrictions:**
- Body and html elements cannot be selected
- Only elements with content are selectable

## Style Editing

The editor supports basic style editing:

**Supported Properties:**
- **Color:** Text color with color picker
- **Font Size:** Predefined sizes (12px - 48px)
- **Text Align:** Left, center, right alignment
- **Font Weight:** Bold, normal (can be extended)
- **Font Style:** Italic, normal (can be extended)

**Style Application:**
Styles are applied as inline styles on the element:
```typescript
element.style.setProperty('color', '#ff0000');
element.style.setProperty('font-size', '24px');
element.style.setProperty('text-align', 'center');
```

## Error Handling

The editor includes comprehensive error handling:

**Save Errors:**
- Network errors are caught and reported
- User is notified via callback
- Unsaved changes remain in the editor
- User can retry the save operation

**Edit Errors:**
- Invalid HTML is sanitized
- DOM manipulation errors are caught
- Editor state is preserved on error

## Performance Considerations

**Optimizations:**
- Debounced code synchronization
- Memoized callbacks to prevent unnecessary re-renders
- Efficient DOM queries using refs
- Minimal re-renders with proper state management

**Best Practices:**
- Use refs for iframe access instead of querying DOM
- Batch style updates when possible
- Limit history size for large documents
- Use virtual scrolling for long version lists

## Accessibility

The editor is built with accessibility in mind:

- **Keyboard Navigation:** All controls are keyboard accessible
- **ARIA Labels:** Buttons have descriptive labels
- **Focus Management:** Focus is properly managed in edit mode
- **Screen Reader Support:** Status messages are announced

## Future Enhancements

Potential improvements for the WYSIWYG editor:

1. **Advanced Style Editing:**
   - Background color and images
   - Borders and shadows
   - Padding and margins
   - Typography (font family, line height, letter spacing)

2. **Element Manipulation:**
   - Drag and drop repositioning
   - Resize handles for elements
   - Duplicate elements
   - Add new elements from a palette

3. **Rich Text Editing:**
   - Bold, italic, underline
   - Lists (ordered, unordered)
   - Links and images
   - Headings and paragraphs

4. **Collaborative Editing:**
   - Real-time multi-user editing
   - Presence indicators
   - Conflict resolution

5. **Advanced History:**
   - Named checkpoints
   - Branch and merge
   - Diff visualization
   - History search

6. **Code View:**
   - Split view with code editor
   - Syntax highlighting
   - Code formatting
   - Direct code editing

## Testing

The WYSIWYG editor should be tested for:

1. **Element Selection:** Click on various elements and verify selection
2. **Text Editing:** Edit text content and verify updates
3. **Style Editing:** Change colors, sizes, alignment and verify
4. **Undo/Redo:** Perform edits, undo, redo and verify state
5. **Save Functionality:** Save changes and verify API calls
6. **Version History:** Restore versions and verify content
7. **Error Handling:** Simulate errors and verify recovery
8. **Keyboard Shortcuts:** Test all keyboard shortcuts
9. **Accessibility:** Test with keyboard and screen reader

## Example Implementation

See `WYSIWYGEditorExample.tsx` for a complete working example that demonstrates:
- Editor setup and configuration
- Code state management
- Save success/error handling
- Version history integration
- User feedback with alerts

## Requirements Satisfied

This implementation satisfies the following requirements from the spec:

- **Requirement 2.2:** Live preview with real-time editing capability
- **Requirement 2.3:** Text content editing with real-time preview update
- **Requirement 2.4:** Basic style editing (color, font size, alignment)
- **Requirement 2.5:** Code synchronization and version history tracking

## Integration with BuilderPage

To integrate the WYSIWYG editor into the BuilderPage:

```tsx
import { WYSIWYGEditor, SitePreview } from '@/components/builder';

function BuilderPage() {
  const iframeRef = useRef<HTMLIFrameElement>(null);
  const [editMode, setEditMode] = useState(false);
  
  return (
    <div>
      {editMode && (
        <WYSIWYGEditor
          siteId={siteId}
          iframeRef={iframeRef}
          htmlCode={htmlCode}
          cssCode={cssCode}
          jsCode={jsCode}
          onCodeUpdate={handleCodeUpdate}
          onSaveSuccess={handleSaveSuccess}
          onSaveError={handleSaveError}
        />
      )}
      
      <SitePreview
        htmlCode={htmlCode}
        cssCode={cssCode}
        jsCode={jsCode}
        editable={editMode}
      />
    </div>
  );
}
```
