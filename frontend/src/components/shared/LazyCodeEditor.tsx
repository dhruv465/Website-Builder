import React, { lazy, Suspense } from 'react';
import { LoadingSpinner } from '@/components/ui/loading-spinner';

interface LazyCodeEditorProps {
  value: string;
  onChange?: (value: string | undefined) => void;
  language?: string;
  height?: string;
  theme?: string;
  options?: Record<string, any>;
}

// Lazy load Monaco Editor to reduce initial bundle size
const MonacoEditor = lazy(() =>
  import('@monaco-editor/react').then((module) => ({
    default: module.default,
  }))
);

/**
 * Lazy-loaded code editor component using Monaco Editor
 * This component demonstrates the pattern for lazy loading heavy dependencies
 * Monaco Editor is only loaded when this component is rendered
 */
export const LazyCodeEditor: React.FC<LazyCodeEditorProps> = ({
  value,
  onChange,
  language = 'javascript',
  height = '400px',
  theme = 'vs-dark',
  options = {},
}) => {
  const defaultOptions = {
    minimap: { enabled: true },
    fontSize: 14,
    lineNumbers: 'on' as const,
    roundedSelection: true,
    scrollBeyondLastLine: false,
    automaticLayout: true,
    tabSize: 2,
    wordWrap: 'on' as const,
    ...options,
  };

  return (
    <Suspense
      fallback={
        <div
          className="flex items-center justify-center border rounded-md bg-muted/50"
          style={{ height }}
        >
          <LoadingSpinner size="lg" />
        </div>
      }
    >
      <div className="border rounded-md overflow-hidden">
        <MonacoEditor
          height={height}
          language={language}
          value={value}
          onChange={onChange}
          theme={theme}
          options={defaultOptions}
        />
      </div>
    </Suspense>
  );
};
