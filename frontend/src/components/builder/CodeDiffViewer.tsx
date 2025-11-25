import React, { useState } from 'react';
import { DiffEditor } from '@monaco-editor/react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { useTheme } from '@/components/theme-provider';
import { FileCode, Palette, Braces, GitCompare } from 'lucide-react';

export interface CodeDiffViewerProps {
  originalHtml?: string;
  modifiedHtml?: string;
  originalCss?: string;
  modifiedCss?: string;
  originalJs?: string;
  modifiedJs?: string;
  height?: string;
  defaultTab?: 'html' | 'css' | 'js';
  readOnly?: boolean;
}

export const CodeDiffViewer: React.FC<CodeDiffViewerProps> = ({
  originalHtml = '',
  modifiedHtml = '',
  originalCss = '',
  modifiedCss = '',
  originalJs = '',
  modifiedJs = '',
  height = '600px',
  defaultTab = 'html',
  readOnly = true,
}) => {
  const { theme } = useTheme();
  const [activeTab, setActiveTab] = useState<'html' | 'css' | 'js'>(defaultTab);

  const editorTheme = theme === 'dark' ? 'vs-dark' : 'vs-light';

  const diffOptions = {
    readOnly,
    renderSideBySide: true,
    enableSplitViewResizing: true,
    originalEditable: false,
    automaticLayout: true,
    fontSize: 14,
    minimap: { enabled: false },
    scrollBeyondLastLine: false,
    wordWrap: 'on' as const,
  };

  // Calculate diff statistics
  const calculateDiffStats = (original: string, modified: string) => {
    const originalLines = original.split('\n');
    const modifiedLines = modified.split('\n');
    
    let additions = 0;
    let deletions = 0;
    
    // Simple line-based diff calculation
    const maxLength = Math.max(originalLines.length, modifiedLines.length);
    for (let i = 0; i < maxLength; i++) {
      const origLine = originalLines[i] || '';
      const modLine = modifiedLines[i] || '';
      
      if (origLine !== modLine) {
        if (!origLine) additions++;
        else if (!modLine) deletions++;
        else {
          additions++;
          deletions++;
        }
      }
    }
    
    return { additions, deletions };
  };

  const htmlStats = calculateDiffStats(originalHtml, modifiedHtml);
  const cssStats = calculateDiffStats(originalCss, modifiedCss);
  const jsStats = calculateDiffStats(originalJs, modifiedJs);

  const getStatsForTab = (tab: 'html' | 'css' | 'js') => {
    switch (tab) {
      case 'html':
        return htmlStats;
      case 'css':
        return cssStats;
      case 'js':
        return jsStats;
    }
  };

  const currentStats = getStatsForTab(activeTab);

  return (
    <div className="flex flex-col h-full border rounded-lg overflow-hidden bg-background">
      <Tabs value={activeTab} onValueChange={(v) => setActiveTab(v as any)} className="flex-1 flex flex-col">
        <div className="flex items-center justify-between border-b bg-muted/30 px-4 py-2">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <GitCompare className="h-4 w-4 text-muted-foreground" />
              <span className="text-sm font-medium">Code Comparison</span>
            </div>
            
            <TabsList className="h-9">
              <TabsTrigger value="html" className="gap-2">
                <FileCode className="h-4 w-4" />
                HTML
                {(htmlStats.additions > 0 || htmlStats.deletions > 0) && (
                  <Badge variant="secondary" className="ml-1 h-5 px-1 text-xs">
                    {htmlStats.additions + htmlStats.deletions}
                  </Badge>
                )}
              </TabsTrigger>
              <TabsTrigger value="css" className="gap-2">
                <Palette className="h-4 w-4" />
                CSS
                {(cssStats.additions > 0 || cssStats.deletions > 0) && (
                  <Badge variant="secondary" className="ml-1 h-5 px-1 text-xs">
                    {cssStats.additions + cssStats.deletions}
                  </Badge>
                )}
              </TabsTrigger>
              <TabsTrigger value="js" className="gap-2">
                <Braces className="h-4 w-4" />
                JavaScript
                {(jsStats.additions > 0 || jsStats.deletions > 0) && (
                  <Badge variant="secondary" className="ml-1 h-5 px-1 text-xs">
                    {jsStats.additions + jsStats.deletions}
                  </Badge>
                )}
              </TabsTrigger>
            </TabsList>
          </div>

          <div className="flex items-center gap-2">
            {currentStats.additions > 0 && (
              <Badge variant="default" className="bg-green-500 hover:bg-green-600">
                +{currentStats.additions}
              </Badge>
            )}
            {currentStats.deletions > 0 && (
              <Badge variant="destructive">
                -{currentStats.deletions}
              </Badge>
            )}
          </div>
        </div>

        <div className="flex items-center justify-between border-b bg-muted/50 px-4 py-1 text-xs text-muted-foreground">
          <span>Original</span>
          <span>Modified</span>
        </div>

        <TabsContent value="html" className="flex-1 m-0 p-0" style={{ height }}>
          <DiffEditor
            height={height}
            language="html"
            original={originalHtml}
            modified={modifiedHtml}
            theme={editorTheme}
            options={diffOptions}
          />
        </TabsContent>

        <TabsContent value="css" className="flex-1 m-0 p-0" style={{ height }}>
          <DiffEditor
            height={height}
            language="css"
            original={originalCss}
            modified={modifiedCss}
            theme={editorTheme}
            options={diffOptions}
          />
        </TabsContent>

        <TabsContent value="js" className="flex-1 m-0 p-0" style={{ height }}>
          <DiffEditor
            height={height}
            language="javascript"
            original={originalJs}
            modified={modifiedJs}
            theme={editorTheme}
            options={diffOptions}
          />
        </TabsContent>
      </Tabs>
    </div>
  );
};
