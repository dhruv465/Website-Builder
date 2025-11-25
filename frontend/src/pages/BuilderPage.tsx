import { useState, useEffect, useCallback } from 'react';
import { useParams } from 'react-router-dom';
import { 
  Loader2, 
  Send, 
  Sparkles, 
  LayoutTemplate, 
  History, 
  Settings, 
  MessageSquare,
  Code2,
  MousePointer2,
  Undo2,
  Redo2,
  FileText,
} from 'lucide-react';
import StudioLayout from '@/layouts/StudioLayout';
import { RightPanel } from '@/components/layout/RightPanel';
import { SitePreview } from '@/components/builder/SitePreview';
import { CodeEditor } from '@/components/builder/CodeEditor';
import { VisualEditor } from '@/components/builder/VisualEditor';
import { TemplateLibrary } from '@/components/templates/TemplateLibrary';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';
import { useSession } from '@/lib/context/SessionContext';
import { useWorkflow } from '@/lib/context/WorkflowContext';
import { useAnnouncer } from '@/lib/hooks/useAnnouncer';
import { useUndoRedo, useUndoRedoShortcuts } from '@/lib/hooks/useUndoRedo';
import { useAutoSave, AutoSaveIndicator } from '@/lib/hooks/useAutoSave';
import { Site } from '@/lib/types/api';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Dialog, DialogContent } from "@/components/ui/dialog";
import { apiClient } from '@/lib/api/client';

type EditorMode = 'preview' | 'code' | 'visual';

interface CodeState {
  htmlCode: string;
  cssCode: string;
  jsCode: string;
}

export default function BuilderPage() {
  const { siteId } = useParams<{ siteId?: string }>();
  const { session } = useSession();
  const {
    workflowState,
    startCreateWorkflow,
    startUpdateWorkflow,
    isCreating,
    isUpdating,
    reset: resetWorkflow,
  } = useWorkflow();
  const { announce } = useAnnouncer();

  const [currentSite, setCurrentSite] = useState<Site | null>(null);
  const [prompt, setPrompt] = useState('');
  const [framework, setFramework] = useState<'react' | 'vue' | 'html'>('react');
  const [designStyle, setDesignStyle] = useState<string>('auto');
  const [selectedVersionId, setSelectedVersionId] = useState<string | null>(null);
  const [editorMode, setEditorMode] = useState<EditorMode>('preview');
  const [isTemplateLibraryOpen, setIsTemplateLibraryOpen] = useState(false);
  
  // Initialize code state with undo/redo
  const initialCodeState: CodeState = {
    htmlCode: '',
    cssCode: '',
    jsCode: '',
  };
  
  const {
    state: codeState,
    setState: setCodeState,
    undo,
    redo,
    canUndo,
    canRedo,
    reset: resetHistory,
  } = useUndoRedo<CodeState>(initialCodeState);

  // Set up keyboard shortcuts for undo/redo
  useUndoRedoShortcuts(undo, redo, true);

  // Auto-save functionality
  const { isSaving, lastSaved, isDirty } = useAutoSave({
    data: codeState,
    onSave: async (data) => {
      if (!currentSite || !siteId) return;
      
      try {
        await apiClient.put(`/api/code/${siteId}`, {
          html_code: data.htmlCode,
          css_code: data.cssCode,
          js_code: data.jsCode,
        });
        announce('Changes saved successfully', 'polite');
      } catch (error) {
        console.error('Failed to save changes:', error);
        throw error;
      }
    },
    interval: 30000, // 30 seconds
    enabled: !!currentSite && !!siteId,
  });
  
  // Load site data if siteId is provided
  useEffect(() => {
    if (siteId && session) {
      const site = session.sites.find((s) => s.id === siteId);
      if (site) {
        setCurrentSite(site);
        // Set initial design style if available
        if (site.design_style) {
          setDesignStyle(site.design_style);
        }
        
        // Load code into undo/redo state
        const latestVersion = site.versions[site.versions.length - 1];
        if (latestVersion) {
          const newCodeState = {
            htmlCode: latestVersion.html_code,
            cssCode: latestVersion.css_code || '',
            jsCode: latestVersion.js_code || '',
          };
          resetHistory(newCodeState);
        }
      }
    }
  }, [siteId, session, resetHistory]);

  // Update code state when version changes
  useEffect(() => {
    if (!currentSite || currentSite.versions.length === 0) return;
    
    const versionToDisplay = selectedVersionId 
      ? currentSite.versions.find(v => v.id === selectedVersionId) 
      : currentSite.versions[currentSite.versions.length - 1];
    
    if (versionToDisplay) {
      const newCodeState = {
        htmlCode: versionToDisplay.html_code,
        cssCode: versionToDisplay.css_code || '',
        jsCode: versionToDisplay.js_code || '',
      };
      resetHistory(newCodeState);
    }
  }, [selectedVersionId, currentSite, resetHistory]);

  // Update current site when workflow completes
  useEffect(() => {
    if (workflowState?.status === 'completed' && session) {
      const updatedSite = session.sites.find((s) => s.id === siteId);
      if (updatedSite) {
        setCurrentSite(updatedSite);
        announce('Website generated successfully', 'polite');
      }
      resetWorkflow();
    }
  }, [workflowState?.status, session, siteId, announce, resetWorkflow]);

  const handleSubmit = useCallback(async () => {
    if (!prompt.trim() || !session) return;

    const styleToSend = designStyle === 'auto' ? undefined : designStyle;

    try {
      if (currentSite) {
        await startUpdateWorkflow({
          session_id: session.id,
          site_id: currentSite.id,
          requirements: prompt,
          framework: framework as any,
          design_style: styleToSend as any,
        });
      } else {
        await startCreateWorkflow({
          session_id: session.id,
          requirements: prompt,
          framework: framework,
          design_style: styleToSend as any || 'modern',
          features: [],
        });
      }
      setPrompt('');
    } catch (error) {
      console.error('Failed to start workflow:', error);
    }
  }, [prompt, session, currentSite, framework, designStyle, startCreateWorkflow, startUpdateWorkflow]);

  const handleCodeChange = (type: 'html' | 'css' | 'js', value: string) => {
    setCodeState((prev) => ({
      ...prev,
      [`${type}Code`]: value,
    }));
  };

  const handleTemplateSelect = (template: any) => {
    // Apply template code to current state
    setCodeState({
      htmlCode: template.html_code,
      cssCode: template.css_code,
      jsCode: template.js_code,
    });
    announce(`Template "${template.name}" applied successfully`, 'polite');
  };

  const isLoading = isCreating || isUpdating;
  const hasCode = currentSite && currentSite.versions.length > 0;

  const SidebarContent = (
    <div className="flex flex-col h-full bg-card text-card-foreground">
      {/* Top Section - Logo & Brand */}
      <div className="h-16 flex items-center px-4 border-b border-border bg-muted/20">
        <div className="h-8 w-8 rounded-lg bg-primary flex items-center justify-center shadow-sm mr-3">
          <Sparkles className="h-4 w-4 text-primary-foreground" />
        </div>
        <span className="font-semibold text-lg tracking-tight text-foreground">AI Builder</span>
      </div>
      
      {/* Navigation Menu */}
      <nav className="p-4 space-y-1">
        <Button variant="ghost" className="w-full justify-start gap-3 text-muted-foreground hover:text-primary hover:bg-primary/5">
          <LayoutTemplate className="h-5 w-5" />
          Builder
        </Button>
        <Button 
          variant="ghost" 
          className="w-full justify-start gap-3 text-muted-foreground hover:text-primary hover:bg-primary/5"
          onClick={() => setIsTemplateLibraryOpen(true)}
        >
          <FileText className="h-5 w-5" />
          Templates
        </Button>
        <Button variant="ghost" className="w-full justify-start gap-3 text-muted-foreground hover:text-primary hover:bg-primary/5">
          <History className="h-5 w-5" />
          History
        </Button>
        <Button variant="ghost" className="w-full justify-start gap-3 text-muted-foreground hover:text-primary hover:bg-primary/5">
          <Settings className="h-5 w-5" />
          Settings
        </Button>
      </nav>

      <Separator className="my-2 opacity-50" />

      {/* Editor Mode Toggle */}
      {hasCode && (
        <div className="px-4 py-2">
          <label className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-2 block">
            Editor Mode
          </label>
          <Tabs value={editorMode} onValueChange={(v) => setEditorMode(v as EditorMode)} className="w-full">
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="preview" className="text-xs">
                <LayoutTemplate className="h-4 w-4" />
              </TabsTrigger>
              <TabsTrigger value="code" className="text-xs">
                <Code2 className="h-4 w-4" />
              </TabsTrigger>
              <TabsTrigger value="visual" className="text-xs">
                <MousePointer2 className="h-4 w-4" />
              </TabsTrigger>
            </TabsList>
          </Tabs>
        </div>
      )}

      {/* Undo/Redo Controls */}
      {hasCode && (
        <div className="px-4 py-2 flex gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={undo}
            disabled={!canUndo}
            className="flex-1"
            title="Undo (Cmd/Ctrl + Z)"
          >
            <Undo2 className="h-4 w-4" />
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={redo}
            disabled={!canRedo}
            className="flex-1"
            title="Redo (Cmd/Ctrl + Shift + Z)"
          >
            <Redo2 className="h-4 w-4" />
          </Button>
        </div>
      )}

      {/* Auto-save Indicator */}
      {hasCode && (
        <div className="px-4 py-2">
          <AutoSaveIndicator
            isSaving={isSaving}
            lastSaved={lastSaved}
            isDirty={isDirty}
            error={null}
          />
        </div>
      )}

      <Separator className="my-2 opacity-50" />

      {/* Project Controls (Dropdowns) */}
      <div className="px-4 py-2 space-y-4">
        <div className="space-y-2">
          <label className="text-xs font-medium text-muted-foreground uppercase tracking-wider">Framework</label>
          <Select value={framework} onValueChange={(value: any) => setFramework(value)}>
            <SelectTrigger className="w-full bg-background border-input">
              <SelectValue placeholder="Select Framework" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="react">React + Tailwind</SelectItem>
              <SelectItem value="vue">Vue + Tailwind</SelectItem>
              <SelectItem value="html">HTML + CSS</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div className="space-y-2">
          <label className="text-xs font-medium text-muted-foreground uppercase tracking-wider">Design Style</label>
          <Select value={designStyle} onValueChange={setDesignStyle}>
            <SelectTrigger className="w-full bg-background border-input">
              <SelectValue placeholder="Select Style" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="auto">Auto (AI Recommended)</SelectItem>
              <SelectItem value="bold_minimalism">Bold Minimalism</SelectItem>
              <SelectItem value="brutalism">Brutalism</SelectItem>
              <SelectItem value="flat_minimalist">Flat Minimalist</SelectItem>
              <SelectItem value="anti_design">Anti Design</SelectItem>
              <SelectItem value="vibrant_blocks">Vibrant Blocks</SelectItem>
              <SelectItem value="organic_fluid">Organic Fluid</SelectItem>
              <SelectItem value="retro_nostalgic">Retro Nostalgic</SelectItem>
              <SelectItem value="experimental">Experimental</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {currentSite && currentSite.versions.length > 0 && (
          <div className="space-y-2">
            <label className="text-xs font-medium text-muted-foreground uppercase tracking-wider">Version</label>
            <Select 
              value={selectedVersionId || (currentSite.versions.length > 0 ? currentSite.versions[currentSite.versions.length - 1]?.id : '')} 
              onValueChange={setSelectedVersionId}
            >
              <SelectTrigger className="w-full bg-background border-input">
                <SelectValue placeholder="Select Version" />
              </SelectTrigger>
              <SelectContent>
                {[...currentSite.versions].reverse().map((version, index) => (
                  <SelectItem key={version.id} value={version.id}>
                    v{currentSite.versions.length - index} - {new Date(version.created_at).toLocaleTimeString()}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        )}
      </div>

      {/* AI Chat Section */}
      <div className="mt-auto flex flex-col border-t border-border bg-muted/20 h-[40%] min-h-[300px]">
        <div className="p-4 border-b border-border flex items-center gap-2 bg-muted/30">
          <MessageSquare className="h-4 w-4 text-primary" />
          <span className="text-sm font-medium">AI Assistant</span>
        </div>
        
        <ScrollArea className="flex-1 p-4">
          <div className="space-y-4">
            <div className="flex gap-3">
              <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0">
                <Sparkles className="h-4 w-4 text-primary" />
              </div>
              <div className="bg-card border border-border rounded-2xl rounded-tl-none p-3 text-sm shadow-sm">
                <p className="text-muted-foreground">Hi! Describe your website and I'll build it for you.</p>
              </div>
            </div>
          </div>
        </ScrollArea>

        {/* Chat Input */}
        <div className="p-4 bg-card border-t border-border">
          <div className="relative">
            <Textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="Describe your changes..."
              className="min-h-[80px] pr-12 resize-none bg-background border-input focus:ring-primary/20"
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSubmit();
                }
              }}
            />
            <Button 
              size="icon" 
              className="absolute bottom-2 right-2 h-8 w-8 rounded-md bg-primary hover:bg-primary-hover text-primary-foreground shadow-sm"
              onClick={handleSubmit}
              disabled={isLoading || !prompt.trim()}
            >
              {isLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
            </Button>
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <StudioLayout sidebar={SidebarContent} rightPanel={<RightPanel />}>
      <div className="h-full w-full flex items-center justify-center p-6 bg-secondary/30">
        <div className="w-full h-full bg-background rounded-xl shadow-sm border border-border/50 relative overflow-hidden">
          {editorMode === 'preview' && (
            <SitePreview
              htmlCode={codeState.htmlCode}
              cssCode={codeState.cssCode}
              jsCode={codeState.jsCode}
              editable={false}
            />
          )}
          
          {editorMode === 'code' && (
            <CodeEditor
              htmlCode={codeState.htmlCode}
              cssCode={codeState.cssCode}
              jsCode={codeState.jsCode}
              onHtmlChange={(value) => handleCodeChange('html', value)}
              onCssChange={(value) => handleCodeChange('css', value)}
              onJsChange={(value) => handleCodeChange('js', value)}
              readOnly={false}
            />
          )}
          
          {editorMode === 'visual' && (
            <VisualEditor
              htmlCode={codeState.htmlCode}
              cssCode={codeState.cssCode}
              jsCode={codeState.jsCode}
              onHtmlChange={(value) => handleCodeChange('html', value)}
              onCssChange={(value) => handleCodeChange('css', value)}
            />
          )}
        </div>
      </div>

      {/* Template Library Dialog */}
      <Dialog open={isTemplateLibraryOpen} onOpenChange={setIsTemplateLibraryOpen}>
        <DialogContent className="max-w-6xl h-[90vh] p-0">
          <TemplateLibrary
            onSelectTemplate={handleTemplateSelect}
            onClose={() => setIsTemplateLibraryOpen(false)}
          />
        </DialogContent>
      </Dialog>
    </StudioLayout>
  );
}
