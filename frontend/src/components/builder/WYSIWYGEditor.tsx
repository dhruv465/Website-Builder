import React, { useState, useCallback, useRef, useEffect } from 'react';
import { ElementToolbar } from './ElementToolbar';
import { updateCode } from '@/lib/api/code';
import { Button } from '@/components/ui/button';
import { Save, Undo, Redo } from 'lucide-react';
import { cn } from '@/lib/utils';

export interface EditableElement {
  element: HTMLElement;
  rect: DOMRect;
  originalContent: string;
  originalStyles: CSSStyleDeclaration;
}

export interface StyleEdit {
  color?: string;
  fontSize?: string;
  textAlign?: string;
  fontWeight?: string;
  fontStyle?: string;
}

export interface EditHistoryEntry {
  element: HTMLElement;
  previousContent: string;
  newContent: string;
  previousStyles: Record<string, string>;
  newStyles: Record<string, string>;
  timestamp: number;
}

export interface WYSIWYGEditorProps {
  siteId: string;
  iframeRef: React.RefObject<HTMLIFrameElement>;
  htmlCode: string;
  cssCode?: string;
  jsCode?: string;
  onCodeUpdate?: (html: string, css?: string, js?: string) => void;
  onSaveSuccess?: () => void;
  onSaveError?: (error: Error) => void;
  className?: string;
}

export const WYSIWYGEditor: React.FC<WYSIWYGEditorProps> = ({
  siteId,
  iframeRef,
  htmlCode,
  cssCode = '',
  jsCode = '',
  onCodeUpdate,
  onSaveSuccess,
  onSaveError,
  className,
}) => {
  const [selectedElement, setSelectedElement] = useState<EditableElement | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [editHistory, setEditHistory] = useState<EditHistoryEntry[]>([]);
  const [historyIndex, setHistoryIndex] = useState(-1);
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);

  const currentHtmlRef = useRef(htmlCode);
  const currentCssRef = useRef(cssCode);
  const currentJsRef = useRef(jsCode);

  // Update refs when props change
  useEffect(() => {
    currentHtmlRef.current = htmlCode;
    currentCssRef.current = cssCode;
    currentJsRef.current = jsCode;
  }, [htmlCode, cssCode, jsCode]);

  // Handle element selection
  const handleElementSelect = useCallback((element: HTMLElement) => {
    if (!element || element === document.body || element === document.documentElement) {
      return;
    }

    const rect = element.getBoundingClientRect();
    const computedStyles = window.getComputedStyle(element);

    setSelectedElement({
      element,
      rect,
      originalContent: element.innerHTML,
      originalStyles: computedStyles,
    });
    setIsEditing(false);
  }, []);

  // Handle text content edit
  const handleTextEdit = useCallback((newContent: string) => {
    if (!selectedElement) return;

    const { element } = selectedElement;
    
    // Create history entry
    const historyEntry: EditHistoryEntry = {
      element,
      previousContent: element.innerHTML,
      newContent,
      previousStyles: {},
      newStyles: {},
      timestamp: Date.now(),
    };

    // Update element
    element.innerHTML = newContent;

    // Add to history
    const newHistory = editHistory.slice(0, historyIndex + 1);
    newHistory.push(historyEntry);
    setEditHistory(newHistory);
    setHistoryIndex(newHistory.length - 1);
    setHasUnsavedChanges(true);

    // Sync code
    syncCodeFromDOM();
  }, [selectedElement, editHistory, historyIndex]);

  // Handle style edit
  const handleStyleEdit = useCallback((styles: StyleEdit) => {
    if (!selectedElement) return;

    const { element } = selectedElement;
    const previousStyles: Record<string, string> = {};
    const newStyles: Record<string, string> = {};

    // Apply styles and track changes
    Object.entries(styles).forEach(([key, value]) => {
      if (value !== undefined) {
        const cssKey = key.replace(/([A-Z])/g, '-$1').toLowerCase();
        previousStyles[cssKey] = element.style.getPropertyValue(cssKey);
        element.style.setProperty(cssKey, value);
        newStyles[cssKey] = value;
      }
    });

    // Create history entry
    const historyEntry: EditHistoryEntry = {
      element,
      previousContent: element.innerHTML,
      newContent: element.innerHTML,
      previousStyles,
      newStyles,
      timestamp: Date.now(),
    };

    // Add to history
    const newHistory = editHistory.slice(0, historyIndex + 1);
    newHistory.push(historyEntry);
    setEditHistory(newHistory);
    setHistoryIndex(newHistory.length - 1);
    setHasUnsavedChanges(true);

    // Update selected element rect
    const rect = element.getBoundingClientRect();
    setSelectedElement((prev) => prev ? { ...prev, rect } : null);

    // Sync code
    syncCodeFromDOM();
  }, [selectedElement, editHistory, historyIndex]);

  // Handle element delete
  const handleElementDelete = useCallback(() => {
    if (!selectedElement) return;

    const { element } = selectedElement;
    
    // Create history entry
    const historyEntry: EditHistoryEntry = {
      element,
      previousContent: element.outerHTML,
      newContent: '',
      previousStyles: {},
      newStyles: {},
      timestamp: Date.now(),
    };

    // Remove element
    element.remove();

    // Add to history
    const newHistory = editHistory.slice(0, historyIndex + 1);
    newHistory.push(historyEntry);
    setEditHistory(newHistory);
    setHistoryIndex(newHistory.length - 1);
    setHasUnsavedChanges(true);

    // Clear selection
    setSelectedElement(null);

    // Sync code
    syncCodeFromDOM();
  }, [selectedElement, editHistory, historyIndex]);

  // Sync code from DOM
  const syncCodeFromDOM = useCallback(() => {
    const iframe = iframeRef.current;
    if (!iframe || !iframe.contentDocument) return;

    const doc = iframe.contentDocument;
    const body = doc.body;

    if (body) {
      const newHtml = body.innerHTML;
      currentHtmlRef.current = newHtml;

      // Extract inline styles if any
      const styleElements = doc.querySelectorAll('style');
      let newCss = currentCssRef.current;
      
      styleElements.forEach((styleEl) => {
        if (styleEl.textContent && !currentCssRef.current.includes(styleEl.textContent)) {
          newCss += '\n' + styleEl.textContent;
        }
      });

      currentCssRef.current = newCss;

      if (onCodeUpdate) {
        onCodeUpdate(newHtml, newCss, currentJsRef.current);
      }
    }
  }, [iframeRef, onCodeUpdate]);

  // Undo
  const handleUndo = useCallback(() => {
    if (historyIndex < 0) return;

    const entry = editHistory[historyIndex];
    if (!entry) return;
    
    const { element, previousContent, previousStyles } = entry;

    // Restore content
    if (previousContent !== element.innerHTML) {
      element.innerHTML = previousContent;
    }

    // Restore styles
    Object.entries(previousStyles).forEach(([key, value]) => {
      element.style.setProperty(key, value);
    });

    setHistoryIndex(historyIndex - 1);
    syncCodeFromDOM();
  }, [editHistory, historyIndex, syncCodeFromDOM]);

  // Redo
  const handleRedo = useCallback(() => {
    if (historyIndex >= editHistory.length - 1) return;

    const entry = editHistory[historyIndex + 1];
    if (!entry) return;
    
    const { element, newContent, newStyles } = entry;

    // Apply content
    if (newContent !== element.innerHTML) {
      element.innerHTML = newContent;
    }

    // Apply styles
    Object.entries(newStyles).forEach(([key, value]) => {
      element.style.setProperty(key, value);
    });

    setHistoryIndex(historyIndex + 1);
    syncCodeFromDOM();
  }, [editHistory, historyIndex, syncCodeFromDOM]);

  // Save changes
  const handleSave = useCallback(async () => {
    setIsSaving(true);

    try {
      await updateCode({
        site_id: siteId,
        html_code: currentHtmlRef.current,
        css_code: currentCssRef.current,
        js_code: currentJsRef.current,
        change_description: `WYSIWYG edit at ${new Date().toISOString()}`,
      });

      setHasUnsavedChanges(false);
      
      if (onSaveSuccess) {
        onSaveSuccess();
      }
    } catch (error) {
      console.error('Save failed:', error);
      
      if (onSaveError) {
        onSaveError(error as Error);
      }
    } finally {
      setIsSaving(false);
    }
  }, [siteId, onSaveSuccess, onSaveError]);

  // Setup click handler in iframe
  useEffect(() => {
    const iframe = iframeRef.current;
    if (!iframe || !iframe.contentDocument) return;

    const handleClick = (e: MouseEvent) => {
      e.preventDefault();
      e.stopPropagation();
      handleElementSelect(e.target as HTMLElement);
    };

    iframe.contentDocument.addEventListener('click', handleClick);

    return () => {
      iframe.contentDocument?.removeEventListener('click', handleClick);
    };
  }, [iframeRef, handleElementSelect]);

  const canUndo = historyIndex >= 0;
  const canRedo = historyIndex < editHistory.length - 1;

  return (
    <div className={cn('flex flex-col', className)}>
      {/* Editor Toolbar */}
      <div className="flex items-center justify-between gap-2 p-2 border-b bg-background">
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={handleUndo}
            disabled={!canUndo}
            title="Undo (Ctrl+Z)"
          >
            <Undo className="h-4 w-4" />
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={handleRedo}
            disabled={!canRedo}
            title="Redo (Ctrl+Y)"
          >
            <Redo className="h-4 w-4" />
          </Button>
        </div>

        <div className="flex items-center gap-2">
          {hasUnsavedChanges && (
            <span className="text-xs text-muted-foreground">Unsaved changes</span>
          )}
          <Button
            variant="default"
            size="sm"
            onClick={handleSave}
            disabled={isSaving || !hasUnsavedChanges}
          >
            <Save className="h-4 w-4 mr-2" />
            {isSaving ? 'Saving...' : 'Save'}
          </Button>
        </div>
      </div>

      {/* Element Toolbar */}
      {selectedElement && (
        <ElementToolbar
          element={selectedElement.element}
          rect={selectedElement.rect}
          isEditing={isEditing}
          onTextEdit={handleTextEdit}
          onStyleEdit={handleStyleEdit}
          onDelete={handleElementDelete}
          onClose={() => setSelectedElement(null)}
          onEditModeChange={setIsEditing}
        />
      )}
    </div>
  );
};
