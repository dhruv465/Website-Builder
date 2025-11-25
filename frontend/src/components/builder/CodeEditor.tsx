import React, { useRef, useState } from 'react';
import Editor, { Monaco, OnMount } from '@monaco-editor/react';
import * as monaco from 'monaco-editor';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { useTheme } from '@/components/theme-provider';
import { 
  Code2, 
  FileCode, 
  Palette, 
  Braces, 
  Download,
  Copy,
  RotateCcw,
  Check,
  AlertCircle
} from 'lucide-react';
import { cn } from '@/lib/utils';

export interface CodeEditorProps {
  htmlCode?: string;
  cssCode?: string;
  jsCode?: string;
  onHtmlChange?: (value: string) => void;
  onCssChange?: (value: string) => void;
  onJsChange?: (value: string) => void;
  readOnly?: boolean;
  height?: string;
  defaultTab?: 'html' | 'css' | 'js';
  showToolbar?: boolean;
  enableFormatting?: boolean;
  enableValidation?: boolean;
}

interface EditorError {
  line: number;
  column: number;
  message: string;
  severity: 'error' | 'warning' | 'info';
}

export const CodeEditor: React.FC<CodeEditorProps> = ({
  htmlCode = '',
  cssCode = '',
  jsCode = '',
  onHtmlChange,
  onCssChange,
  onJsChange,
  readOnly = false,
  height = '600px',
  defaultTab = 'html',
  showToolbar = true,
  enableFormatting = true,
  enableValidation = true,
}) => {
  const { theme } = useTheme();
  const [activeTab, setActiveTab] = useState<'html' | 'css' | 'js'>(defaultTab);
  const [copied, setCopied] = useState(false);
  const [errors, setErrors] = useState<EditorError[]>([]);
  
  const htmlEditorRef = useRef<monaco.editor.IStandaloneCodeEditor | null>(null);
  const cssEditorRef = useRef<monaco.editor.IStandaloneCodeEditor | null>(null);
  const jsEditorRef = useRef<monaco.editor.IStandaloneCodeEditor | null>(null);
  const monacoRef = useRef<Monaco | null>(null);

  const editorTheme = theme === 'dark' ? 'vs-dark' : 'vs-light';

  // Configure Monaco Editor on mount
  const handleEditorWillMount = (monaco: Monaco) => {
    monacoRef.current = monaco;

    // Configure HTML language features
    monaco.languages.html.htmlDefaults.setOptions({
      format: {
        tabSize: 2,
        insertSpaces: true,
        wrapLineLength: 120,
        unformatted: 'wbr',
        contentUnformatted: 'pre,code,textarea',
        indentInnerHtml: true,
        preserveNewLines: true,
        maxPreserveNewLines: 2,
        indentHandlebars: false,
        endWithNewline: false,
        extraLiners: 'head, body, /html',
        wrapAttributes: 'auto',
      },
      suggest: {
        html5: true,
      },
    });

    // Configure CSS language features
    monaco.languages.css.cssDefaults.setOptions({
      validate: enableValidation,
      lint: {
        compatibleVendorPrefixes: 'warning',
        vendorPrefix: 'warning',
        duplicateProperties: 'warning',
        emptyRules: 'warning',
        importStatement: 'ignore',
        boxModel: 'ignore',
        universalSelector: 'ignore',
        zeroUnits: 'ignore',
        fontFaceProperties: 'warning',
        hexColorLength: 'error',
        argumentsInColorFunction: 'error',
        unknownProperties: 'warning',
        ieHack: 'ignore',
        unknownVendorSpecificProperties: 'ignore',
        propertyIgnoredDueToDisplay: 'warning',
        important: 'ignore',
        float: 'ignore',
        idSelector: 'ignore',
      },
    });

    // Configure JavaScript/TypeScript language features
    monaco.languages.typescript.javascriptDefaults.setDiagnosticsOptions({
      noSemanticValidation: !enableValidation,
      noSyntaxValidation: !enableValidation,
    });

    monaco.languages.typescript.javascriptDefaults.setCompilerOptions({
      target: monaco.languages.typescript.ScriptTarget.ES2020,
      allowNonTsExtensions: true,
      allowJs: true,
      checkJs: false,
    });
  };

  // Handle editor mount for each language
  const handleHtmlEditorMount: OnMount = (editor, monaco) => {
    htmlEditorRef.current = editor;
    setupEditor(editor, monaco, 'html');
  };

  const handleCssEditorMount: OnMount = (editor, monaco) => {
    cssEditorRef.current = editor;
    setupEditor(editor, monaco, 'css');
  };

  const handleJsEditorMount: OnMount = (editor, monaco) => {
    jsEditorRef.current = editor;
    setupEditor(editor, monaco, 'javascript');
  };

  // Setup editor with common configurations
  const setupEditor = (
    editor: monaco.editor.IStandaloneCodeEditor,
    monaco: Monaco,
    _language: string
  ) => {
    // Add keyboard shortcuts
    editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyS, () => {
      handleSave();
    });

    editor.addCommand(
      monaco.KeyMod.CtrlCmd | monaco.KeyMod.Shift | monaco.KeyCode.KeyF,
      () => {
        handleFormat();
      }
    );

    // Listen for validation errors
    if (enableValidation) {
      monaco.editor.onDidChangeMarkers(() => {
        const model = editor.getModel();
        if (model) {
          const markers = monaco.editor.getModelMarkers({ resource: model.uri });
          const editorErrors: EditorError[] = markers.map((marker) => ({
            line: marker.startLineNumber,
            column: marker.startColumn,
            message: marker.message,
            severity:
              marker.severity === monaco.MarkerSeverity.Error
                ? 'error'
                : marker.severity === monaco.MarkerSeverity.Warning
                ? 'warning'
                : 'info',
          }));
          setErrors(editorErrors);
        }
      });
    }
  };

  // Get current active editor
  const getCurrentEditor = () => {
    switch (activeTab) {
      case 'html':
        return htmlEditorRef.current;
      case 'css':
        return cssEditorRef.current;
      case 'js':
        return jsEditorRef.current;
      default:
        return null;
    }
  };

  // Format code
  const handleFormat = async () => {
    if (!enableFormatting) return;
    
    const editor = getCurrentEditor();
    if (editor) {
      await editor.getAction('editor.action.formatDocument')?.run();
    }
  };

  // Copy code to clipboard
  const handleCopy = async () => {
    const editor = getCurrentEditor();
    if (editor) {
      const value = editor.getValue();
      await navigator.clipboard.writeText(value);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  // Download code
  const handleDownload = () => {
    const editor = getCurrentEditor();
    if (editor) {
      const value = editor.getValue();
      const extension = activeTab === 'html' ? 'html' : activeTab === 'css' ? 'css' : 'js';
      const blob = new Blob([value], { type: 'text/plain' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `code.${extension}`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    }
  };

  // Reset code
  const handleReset = () => {
    const editor = getCurrentEditor();
    if (editor) {
      const originalValue =
        activeTab === 'html' ? htmlCode : activeTab === 'css' ? cssCode : jsCode;
      editor.setValue(originalValue);
    }
  };

  // Save code (placeholder for actual save logic)
  const handleSave = () => {
    // This would typically trigger a save to the backend
    console.log('Save triggered');
  };

  // Get error count by severity
  const getErrorCount = (severity: 'error' | 'warning' | 'info') => {
    return errors.filter((e) => e.severity === severity).length;
  };

  const editorOptions: monaco.editor.IStandaloneEditorConstructionOptions = {
    readOnly,
    minimap: { enabled: true },
    fontSize: 14,
    lineNumbers: 'on',
    roundedSelection: true,
    scrollBeyondLastLine: false,
    automaticLayout: true,
    tabSize: 2,
    wordWrap: 'on',
    formatOnPaste: enableFormatting,
    formatOnType: enableFormatting,
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
  };

  return (
    <div className="flex flex-col h-full border rounded-lg overflow-hidden bg-background">
      <Tabs value={activeTab} onValueChange={(v) => setActiveTab(v as any)} className="flex-1 flex flex-col">
        <div className="flex items-center justify-between border-b bg-muted/30 px-4 py-2">
          <TabsList className="h-9">
            <TabsTrigger value="html" className="gap-2">
              <FileCode className="h-4 w-4" />
              HTML
            </TabsTrigger>
            <TabsTrigger value="css" className="gap-2">
              <Palette className="h-4 w-4" />
              CSS
            </TabsTrigger>
            <TabsTrigger value="js" className="gap-2">
              <Braces className="h-4 w-4" />
              JavaScript
            </TabsTrigger>
          </TabsList>

          {showToolbar && (
            <div className="flex items-center gap-2">
              {errors.length > 0 && (
                <div className="flex items-center gap-2 mr-2">
                  {getErrorCount('error') > 0 && (
                    <Badge variant="destructive" className="gap-1">
                      <AlertCircle className="h-3 w-3" />
                      {getErrorCount('error')}
                    </Badge>
                  )}
                  {getErrorCount('warning') > 0 && (
                    <Badge variant="secondary" className="gap-1">
                      <AlertCircle className="h-3 w-3" />
                      {getErrorCount('warning')}
                    </Badge>
                  )}
                </div>
              )}
              
              {enableFormatting && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleFormat}
                  title="Format Code (Ctrl/Cmd + Shift + F)"
                >
                  <Code2 className="h-4 w-4" />
                </Button>
              )}
              
              <Button
                variant="ghost"
                size="sm"
                onClick={handleCopy}
                title="Copy to Clipboard"
              >
                {copied ? (
                  <Check className="h-4 w-4 text-green-500" />
                ) : (
                  <Copy className="h-4 w-4" />
                )}
              </Button>
              
              <Button
                variant="ghost"
                size="sm"
                onClick={handleDownload}
                title="Download File"
              >
                <Download className="h-4 w-4" />
              </Button>
              
              <Button
                variant="ghost"
                size="sm"
                onClick={handleReset}
                title="Reset to Original"
              >
                <RotateCcw className="h-4 w-4" />
              </Button>
            </div>
          )}
        </div>

        <TabsContent value="html" className="flex-1 m-0 p-0" style={{ height }}>
          <Editor
            height={height}
            defaultLanguage="html"
            value={htmlCode}
            onChange={(value) => onHtmlChange?.(value || '')}
            theme={editorTheme}
            options={editorOptions}
            beforeMount={handleEditorWillMount}
            onMount={handleHtmlEditorMount}
          />
        </TabsContent>

        <TabsContent value="css" className="flex-1 m-0 p-0" style={{ height }}>
          <Editor
            height={height}
            defaultLanguage="css"
            value={cssCode}
            onChange={(value) => onCssChange?.(value || '')}
            theme={editorTheme}
            options={editorOptions}
            onMount={handleCssEditorMount}
          />
        </TabsContent>

        <TabsContent value="js" className="flex-1 m-0 p-0" style={{ height }}>
          <Editor
            height={height}
            defaultLanguage="javascript"
            value={jsCode}
            onChange={(value) => onJsChange?.(value || '')}
            theme={editorTheme}
            options={editorOptions}
            onMount={handleJsEditorMount}
          />
        </TabsContent>
      </Tabs>

      {errors.length > 0 && (
        <div className="border-t bg-muted/30 p-2 max-h-32 overflow-y-auto">
          <div className="text-xs font-medium mb-1">Issues:</div>
          {errors.slice(0, 5).map((error, index) => (
            <div
              key={index}
              className={cn(
                'text-xs py-1 px-2 rounded mb-1',
                error.severity === 'error' && 'bg-destructive/10 text-destructive',
                error.severity === 'warning' && 'bg-yellow-500/10 text-yellow-600 dark:text-yellow-500',
                error.severity === 'info' && 'bg-blue-500/10 text-blue-600 dark:text-blue-500'
              )}
            >
              Line {error.line}:{error.column} - {error.message}
            </div>
          ))}
          {errors.length > 5 && (
            <div className="text-xs text-muted-foreground">
              ... and {errors.length - 5} more issues
            </div>
          )}
        </div>
      )}
    </div>
  );
};
