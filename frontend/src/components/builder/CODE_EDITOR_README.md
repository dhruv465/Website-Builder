# Code Editor Integration

This document describes the Monaco Editor integration for advanced code editing in the website builder.

## Overview

The code editor integration provides a full-featured IDE experience within the browser, powered by Monaco Editor (the same editor that powers VS Code). It supports HTML, CSS, and JavaScript with syntax highlighting, code completion, validation, and formatting.

## Components

### CodeEditor

The main code editor component with tabbed interface for HTML, CSS, and JavaScript editing.

**Features:**
- Syntax highlighting for HTML, CSS, and JavaScript
- IntelliSense and code completion
- Real-time error detection and validation
- Auto-formatting with Prettier integration
- Bracket matching and auto-closing
- Code folding and minimap
- Keyboard shortcuts (Ctrl/Cmd+S for save, Ctrl/Cmd+Shift+F for format)
- Copy, download, and reset functionality
- Error display with line numbers and severity indicators
- Theme support (light/dark mode)

**Usage:**

```tsx
import { CodeEditor } from '@/components/builder';

function MyComponent() {
  const [htmlCode, setHtmlCode] = useState('<h1>Hello World</h1>');
  const [cssCode, setCssCode] = useState('h1 { color: blue; }');
  const [jsCode, setJsCode] = useState('console.log("Hello");');

  return (
    <CodeEditor
      htmlCode={htmlCode}
      cssCode={cssCode}
      jsCode={jsCode}
      onHtmlChange={setHtmlCode}
      onCssChange={setCssCode}
      onJsChange={setJsCode}
      height="600px"
      showToolbar={true}
      enableFormatting={true}
      enableValidation={true}
    />
  );
}
```

**Props:**

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `htmlCode` | `string` | `''` | HTML code content |
| `cssCode` | `string` | `''` | CSS code content |
| `jsCode` | `string` | `''` | JavaScript code content |
| `onHtmlChange` | `(value: string) => void` | - | Callback when HTML changes |
| `onCssChange` | `(value: string) => void` | - | Callback when CSS changes |
| `onJsChange` | `(value: string) => void` | - | Callback when JavaScript changes |
| `readOnly` | `boolean` | `false` | Make editor read-only |
| `height` | `string` | `'600px'` | Editor height |
| `defaultTab` | `'html' \| 'css' \| 'js'` | `'html'` | Default active tab |
| `showToolbar` | `boolean` | `true` | Show toolbar with actions |
| `enableFormatting` | `boolean` | `true` | Enable code formatting |
| `enableValidation` | `boolean` | `true` | Enable code validation |

### CodeDiffViewer

A side-by-side diff viewer for comparing code changes between versions.

**Features:**
- Side-by-side code comparison
- Inline diff highlighting
- Change statistics (additions/deletions)
- Syntax highlighting for both versions
- Tabbed interface for HTML, CSS, and JavaScript
- Theme support (light/dark mode)

**Usage:**

```tsx
import { CodeDiffViewer } from '@/components/builder';

function MyComponent() {
  return (
    <CodeDiffViewer
      originalHtml="<h1>Old Title</h1>"
      modifiedHtml="<h1>New Title</h1>"
      originalCss="h1 { color: red; }"
      modifiedCss="h1 { color: blue; }"
      originalJs="console.log('old');"
      modifiedJs="console.log('new');"
      height="600px"
    />
  );
}
```

**Props:**

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `originalHtml` | `string` | `''` | Original HTML code |
| `modifiedHtml` | `string` | `''` | Modified HTML code |
| `originalCss` | `string` | `''` | Original CSS code |
| `modifiedCss` | `string` | `''` | Modified CSS code |
| `originalJs` | `string` | `''` | Original JavaScript code |
| `modifiedJs` | `string` | `''` | Modified JavaScript code |
| `height` | `string` | `'600px'` | Viewer height |
| `defaultTab` | `'html' \| 'css' \| 'js'` | `'html'` | Default active tab |
| `readOnly` | `boolean` | `true` | Make viewer read-only |

### LazyCodeEditor

A lazy-loaded wrapper for Monaco Editor that reduces initial bundle size.

**Usage:**

```tsx
import { LazyCodeEditor } from '@/components/shared/LazyCodeEditor';

function MyComponent() {
  const [code, setCode] = useState('console.log("Hello");');

  return (
    <LazyCodeEditor
      value={code}
      onChange={setCode}
      language="javascript"
      height="400px"
      theme="vs-dark"
    />
  );
}
```

## Monaco Editor Configuration

### Language Features

**HTML:**
- HTML5 tag completion
- Attribute suggestions
- Format options (tab size, line wrapping, etc.)
- Emmet abbreviations support

**CSS:**
- Property suggestions
- Color picker
- CSS linting with configurable rules
- Vendor prefix warnings
- Unknown property detection

**JavaScript:**
- ES2020+ syntax support
- IntelliSense
- Syntax validation
- JSDoc support
- Type checking (optional)

### Editor Options

The editor is configured with the following default options:

```typescript
{
  readOnly: false,
  minimap: { enabled: true },
  fontSize: 14,
  lineNumbers: 'on',
  roundedSelection: true,
  scrollBeyondLastLine: false,
  automaticLayout: true,
  tabSize: 2,
  wordWrap: 'on',
  formatOnPaste: true,
  formatOnType: true,
  suggestOnTriggerCharacters: true,
  quickSuggestions: true,
  folding: true,
  foldingStrategy: 'indentation',
  showFoldingControls: 'always',
  matchBrackets: 'always',
  autoClosingBrackets: 'always',
  autoClosingQuotes: 'always',
  autoIndent: 'full',
  contextmenu: true,
  mouseWheelZoom: true,
}
```

## Keyboard Shortcuts

### Common Shortcuts

| Action | Windows/Linux | macOS |
|--------|---------------|-------|
| Save | `Ctrl+S` | `Cmd+S` |
| Format Code | `Ctrl+Shift+F` | `Cmd+Shift+F` |
| Find | `Ctrl+F` | `Cmd+F` |
| Replace | `Ctrl+H` | `Cmd+H` |
| Go to Line | `Ctrl+G` | `Cmd+G` |
| Comment Line | `Ctrl+/` | `Cmd+/` |
| Duplicate Line | `Shift+Alt+Down` | `Shift+Option+Down` |
| Delete Line | `Ctrl+Shift+K` | `Cmd+Shift+K` |
| Multi-cursor | `Alt+Click` | `Option+Click` |
| Select All Occurrences | `Ctrl+Shift+L` | `Cmd+Shift+L` |

### Editor-Specific Shortcuts

| Action | Windows/Linux | macOS |
|--------|---------------|-------|
| Toggle Comment | `Ctrl+/` | `Cmd+/` |
| Fold | `Ctrl+Shift+[` | `Cmd+Option+[` |
| Unfold | `Ctrl+Shift+]` | `Cmd+Option+]` |
| Fold All | `Ctrl+K Ctrl+0` | `Cmd+K Cmd+0` |
| Unfold All | `Ctrl+K Ctrl+J` | `Cmd+K Cmd+J` |

## Error Handling

The editor displays validation errors in real-time:

- **Errors**: Red badges and highlights for critical issues
- **Warnings**: Yellow badges and highlights for potential problems
- **Info**: Blue badges for informational messages

Errors are displayed in a panel below the editor with:
- Line and column numbers
- Error message
- Severity indicator

## Performance Optimization

### Code Splitting

The Monaco Editor is loaded lazily to reduce initial bundle size:

```tsx
const MonacoEditor = lazy(() => import('@monaco-editor/react'));
```

### Automatic Layout

The editor automatically adjusts its layout when the container size changes, ensuring optimal display on different screen sizes.

### Minimap

The minimap provides a bird's-eye view of the code and can be disabled for better performance on large files.

## Integration with Builder

### In BuilderPage

The code editor can be integrated into the builder page for advanced editing:

```tsx
import { CodeEditor } from '@/components/builder';
import { SitePreview } from '@/components/builder';

function BuilderPage() {
  const [htmlCode, setHtmlCode] = useState('');
  const [cssCode, setCssCode] = useState('');
  const [jsCode, setJsCode] = useState('');
  const [showCodeEditor, setShowCodeEditor] = useState(false);

  return (
    <div>
      <Button onClick={() => setShowCodeEditor(!showCodeEditor)}>
        {showCodeEditor ? 'Show Preview' : 'Show Code'}
      </Button>

      {showCodeEditor ? (
        <CodeEditor
          htmlCode={htmlCode}
          cssCode={cssCode}
          jsCode={jsCode}
          onHtmlChange={setHtmlCode}
          onCssChange={setCssCode}
          onJsChange={setJsCode}
        />
      ) : (
        <SitePreview
          htmlCode={htmlCode}
          cssCode={cssCode}
          jsCode={jsCode}
        />
      )}
    </div>
  );
}
```

### Version Comparison

Use the CodeDiffViewer to show changes between versions:

```tsx
import { CodeDiffViewer } from '@/components/builder';

function VersionComparison({ oldVersion, newVersion }) {
  return (
    <CodeDiffViewer
      originalHtml={oldVersion.html}
      modifiedHtml={newVersion.html}
      originalCss={oldVersion.css}
      modifiedCss={newVersion.css}
      originalJs={oldVersion.js}
      modifiedJs={newVersion.js}
    />
  );
}
```

## Testing

Visit `/dashboard/code-editor-test` to see a comprehensive demo of all code editor features.

## Dependencies

- `@monaco-editor/react`: ^4.6.0
- `monaco-editor`: ^0.45.0

## Browser Support

Monaco Editor supports all modern browsers:
- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)

## Future Enhancements

- [ ] Prettier integration for advanced formatting
- [ ] ESLint integration for JavaScript linting
- [ ] Custom themes and color schemes
- [ ] Collaborative editing with real-time sync
- [ ] Code snippets and templates
- [ ] Git diff integration
- [ ] Search and replace across all files
- [ ] Code refactoring tools
