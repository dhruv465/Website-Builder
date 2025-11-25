import { useState, useRef, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  MousePointer2,
  Type,
  Palette,
  Layout,
  Settings2,
  Trash2,
  Copy,
} from 'lucide-react';
import { cn } from '@/lib/utils';

export interface VisualEditorProps {
  htmlCode: string;
  cssCode: string;
  jsCode: string;
  onHtmlChange?: (code: string) => void;
  onCssChange?: (code: string) => void;
  className?: string;
}

interface SelectedElement {
  element: HTMLElement;
  tagName: string;
  id: string;
  classes: string[];
  styles: CSSStyleDeclaration;
}

export function VisualEditor({
  htmlCode,
  cssCode,
  jsCode,
  onHtmlChange,
  onCssChange,
  className,
}: VisualEditorProps) {
  const iframeRef = useRef<HTMLIFrameElement>(null);
  const [selectedElement, setSelectedElement] = useState<SelectedElement | null>(null);
  const [isEditMode, setIsEditMode] = useState(true);

  // Initialize iframe with content
  useEffect(() => {
    if (!iframeRef.current) return;

    const iframe = iframeRef.current;
    const doc = iframe.contentDocument || iframe.contentWindow?.document;
    if (!doc) return;

    // Build complete HTML document
    const fullHtml = `
      <!DOCTYPE html>
      <html>
        <head>
          <meta charset="UTF-8">
          <meta name="viewport" content="width=device-width, initial-scale=1.0">
          <style>
            ${cssCode}
            
            /* Visual editor styles */
            .visual-editor-hover {
              outline: 2px dashed #3b82f6 !important;
              outline-offset: 2px;
              cursor: pointer;
            }
            
            .visual-editor-selected {
              outline: 2px solid #3b82f6 !important;
              outline-offset: 2px;
            }
          </style>
        </head>
        <body>
          ${htmlCode}
          <script>
            ${jsCode}
          </script>
        </body>
      </html>
    `;

    doc.open();
    doc.write(fullHtml);
    doc.close();

    // Set up event listeners after content loads
    setTimeout(() => {
      setupEventListeners(doc);
    }, 100);
  }, [htmlCode, cssCode, jsCode]);

  const setupEventListeners = (doc: Document) => {
    if (!isEditMode) return;

    const elements = doc.body.querySelectorAll('*');
    
    elements.forEach((element) => {
      const htmlElement = element as HTMLElement;

      // Hover effect
      htmlElement.addEventListener('mouseenter', (e) => {
        e.stopPropagation();
        if (selectedElement?.element !== htmlElement) {
          htmlElement.classList.add('visual-editor-hover');
        }
      });

      htmlElement.addEventListener('mouseleave', () => {
        htmlElement.classList.remove('visual-editor-hover');
      });

      // Click to select
      htmlElement.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        
        // Remove previous selection
        doc.querySelectorAll('.visual-editor-selected').forEach((el) => {
          el.classList.remove('visual-editor-selected');
        });

        // Add new selection
        htmlElement.classList.add('visual-editor-selected');
        htmlElement.classList.remove('visual-editor-hover');

        setSelectedElement({
          element: htmlElement,
          tagName: htmlElement.tagName.toLowerCase(),
          id: htmlElement.id,
          classes: Array.from(htmlElement.classList).filter(
            (c) => !c.startsWith('visual-editor-')
          ),
          styles: window.getComputedStyle(htmlElement),
        });
      });
    });
  };

  const updateElementText = (newText: string) => {
    if (!selectedElement) return;
    
    selectedElement.element.textContent = newText;
    updateHtmlCode();
  };

  const updateElementStyle = (property: string, value: string) => {
    if (!selectedElement) return;
    
    selectedElement.element.style[property as any] = value;
    updateCssCode();
  };

  const updateElementClass = (newClasses: string[]) => {
    if (!selectedElement) return;
    
    // Remove old classes (except visual editor classes)
    selectedElement.classes.forEach((cls) => {
      selectedElement.element.classList.remove(cls);
    });
    
    // Add new classes
    newClasses.forEach((cls) => {
      if (cls.trim()) {
        selectedElement.element.classList.add(cls.trim());
      }
    });
    
    updateHtmlCode();
  };

  const deleteElement = () => {
    if (!selectedElement) return;
    
    selectedElement.element.remove();
    setSelectedElement(null);
    updateHtmlCode();
  };

  const duplicateElement = () => {
    if (!selectedElement) return;
    
    const clone = selectedElement.element.cloneNode(true) as HTMLElement;
    selectedElement.element.parentNode?.insertBefore(
      clone,
      selectedElement.element.nextSibling
    );
    updateHtmlCode();
  };

  const updateHtmlCode = () => {
    if (!iframeRef.current) return;
    
    const doc = iframeRef.current.contentDocument;
    if (!doc) return;
    
    const newHtml = doc.body.innerHTML;
    onHtmlChange?.(newHtml);
  };

  const updateCssCode = () => {
    if (!selectedElement) return;
    
    // Extract inline styles and update CSS
    const inlineStyles = selectedElement.element.style.cssText;
    if (inlineStyles) {
      // This is a simplified version - in production, you'd want to
      // properly parse and update the CSS code
      onCssChange?.(cssCode + `\n/* Updated styles */\n`);
    }
  };

  return (
    <div className={cn('flex h-full gap-4', className)}>
      {/* Preview Area */}
      <div className="flex-1 flex flex-col bg-card border border-border rounded-lg overflow-hidden">
        <div className="flex items-center justify-between px-4 py-2 border-b border-border bg-muted/20">
          <div className="flex items-center gap-2">
            <MousePointer2 className="h-4 w-4 text-primary" />
            <span className="text-sm font-medium">Visual Editor</span>
          </div>
          <div className="flex items-center gap-2">
            <Button
              variant={isEditMode ? 'default' : 'outline'}
              size="sm"
              onClick={() => setIsEditMode(!isEditMode)}
            >
              {isEditMode ? 'Edit Mode' : 'Preview Mode'}
            </Button>
          </div>
        </div>
        
        <div className="flex-1 relative">
          <iframe
            ref={iframeRef}
            className="w-full h-full border-0"
            title="Visual Editor Preview"
            sandbox="allow-scripts allow-same-origin"
          />
        </div>
      </div>

      {/* Properties Panel */}
      <div className="w-80 bg-card border border-border rounded-lg overflow-hidden flex flex-col">
        <div className="px-4 py-2 border-b border-border bg-muted/20">
          <div className="flex items-center gap-2">
            <Settings2 className="h-4 w-4 text-primary" />
            <span className="text-sm font-medium">Properties</span>
          </div>
        </div>

        {selectedElement ? (
          <ScrollArea className="flex-1">
            <div className="p-4 space-y-4">
              {/* Element Info */}
              <div>
                <Label className="text-xs text-muted-foreground">Element</Label>
                <div className="mt-1 px-3 py-2 bg-muted rounded-md">
                  <code className="text-sm">&lt;{selectedElement.tagName}&gt;</code>
                </div>
              </div>

              <Separator />

              {/* Actions */}
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={duplicateElement}
                  className="flex-1"
                >
                  <Copy className="h-4 w-4 mr-2" />
                  Duplicate
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={deleteElement}
                  className="flex-1"
                >
                  <Trash2 className="h-4 w-4 mr-2" />
                  Delete
                </Button>
              </div>

              <Separator />

              {/* Tabs for different properties */}
              <Tabs defaultValue="content" className="w-full">
                <TabsList className="grid w-full grid-cols-3">
                  <TabsTrigger value="content">
                    <Type className="h-4 w-4" />
                  </TabsTrigger>
                  <TabsTrigger value="style">
                    <Palette className="h-4 w-4" />
                  </TabsTrigger>
                  <TabsTrigger value="layout">
                    <Layout className="h-4 w-4" />
                  </TabsTrigger>
                </TabsList>

                {/* Content Tab */}
                <TabsContent value="content" className="space-y-4">
                  <div>
                    <Label htmlFor="element-text">Text Content</Label>
                    <Input
                      id="element-text"
                      value={selectedElement.element.textContent || ''}
                      onChange={(e) => updateElementText(e.target.value)}
                      className="mt-1"
                    />
                  </div>

                  <div>
                    <Label htmlFor="element-id">ID</Label>
                    <Input
                      id="element-id"
                      value={selectedElement.id}
                      onChange={(e) => {
                        selectedElement.element.id = e.target.value;
                        updateHtmlCode();
                      }}
                      className="mt-1"
                      placeholder="element-id"
                    />
                  </div>

                  <div>
                    <Label htmlFor="element-classes">Classes</Label>
                    <Input
                      id="element-classes"
                      value={selectedElement.classes.join(' ')}
                      onChange={(e) => updateElementClass(e.target.value.split(' '))}
                      className="mt-1"
                      placeholder="class-1 class-2"
                    />
                  </div>
                </TabsContent>

                {/* Style Tab */}
                <TabsContent value="style" className="space-y-4">
                  <div>
                    <Label htmlFor="color">Text Color</Label>
                    <Input
                      id="color"
                      type="color"
                      value={selectedElement.styles.color || '#000000'}
                      onChange={(e) => updateElementStyle('color', e.target.value)}
                      className="mt-1 h-10"
                    />
                  </div>

                  <div>
                    <Label htmlFor="bg-color">Background Color</Label>
                    <Input
                      id="bg-color"
                      type="color"
                      value={selectedElement.styles.backgroundColor || '#ffffff'}
                      onChange={(e) => updateElementStyle('backgroundColor', e.target.value)}
                      className="mt-1 h-10"
                    />
                  </div>

                  <div>
                    <Label htmlFor="font-size">Font Size</Label>
                    <Input
                      id="font-size"
                      type="number"
                      value={parseInt(selectedElement.styles.fontSize) || 16}
                      onChange={(e) => updateElementStyle('fontSize', `${e.target.value}px`)}
                      className="mt-1"
                    />
                  </div>

                  <div>
                    <Label htmlFor="font-weight">Font Weight</Label>
                    <select
                      id="font-weight"
                      value={selectedElement.styles.fontWeight || 'normal'}
                      onChange={(e) => updateElementStyle('fontWeight', e.target.value)}
                      className="mt-1 w-full px-3 py-2 bg-background border border-input rounded-md"
                    >
                      <option value="normal">Normal</option>
                      <option value="bold">Bold</option>
                      <option value="lighter">Lighter</option>
                      <option value="bolder">Bolder</option>
                    </select>
                  </div>
                </TabsContent>

                {/* Layout Tab */}
                <TabsContent value="layout" className="space-y-4">
                  <div>
                    <Label htmlFor="display">Display</Label>
                    <select
                      id="display"
                      value={selectedElement.styles.display || 'block'}
                      onChange={(e) => updateElementStyle('display', e.target.value)}
                      className="mt-1 w-full px-3 py-2 bg-background border border-input rounded-md"
                    >
                      <option value="block">Block</option>
                      <option value="inline">Inline</option>
                      <option value="inline-block">Inline Block</option>
                      <option value="flex">Flex</option>
                      <option value="grid">Grid</option>
                      <option value="none">None</option>
                    </select>
                  </div>

                  <div className="grid grid-cols-2 gap-2">
                    <div>
                      <Label htmlFor="width">Width</Label>
                      <Input
                        id="width"
                        value={selectedElement.styles.width || 'auto'}
                        onChange={(e) => updateElementStyle('width', e.target.value)}
                        className="mt-1"
                        placeholder="auto"
                      />
                    </div>
                    <div>
                      <Label htmlFor="height">Height</Label>
                      <Input
                        id="height"
                        value={selectedElement.styles.height || 'auto'}
                        onChange={(e) => updateElementStyle('height', e.target.value)}
                        className="mt-1"
                        placeholder="auto"
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-2">
                    <div>
                      <Label htmlFor="margin">Margin</Label>
                      <Input
                        id="margin"
                        value={selectedElement.styles.margin || '0'}
                        onChange={(e) => updateElementStyle('margin', e.target.value)}
                        className="mt-1"
                        placeholder="0"
                      />
                    </div>
                    <div>
                      <Label htmlFor="padding">Padding</Label>
                      <Input
                        id="padding"
                        value={selectedElement.styles.padding || '0'}
                        onChange={(e) => updateElementStyle('padding', e.target.value)}
                        className="mt-1"
                        placeholder="0"
                      />
                    </div>
                  </div>
                </TabsContent>
              </Tabs>
            </div>
          </ScrollArea>
        ) : (
          <div className="flex-1 flex items-center justify-center p-4">
            <div className="text-center text-muted-foreground">
              <MousePointer2 className="h-12 w-12 mx-auto mb-2 opacity-50" />
              <p className="text-sm">Click on an element to edit its properties</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
