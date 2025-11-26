import { useState, useEffect, Suspense, lazy, useRef } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { SitePreview } from '@/components/builder/SitePreview';
import { DeviceEmulator, Orientation } from '@/components/builder/DeviceEmulator';
import { PerformanceOverlay } from '@/components/builder/PerformanceOverlay';
import { AgentActivity, AgentStep } from '@/components/builder/AgentActivity';
import { NaturalLanguageInput, AgentStepStatus } from '@/components/editor/NaturalLanguageInput';
import { Undo, Redo, Save, Code, Eye, Home, Sparkles, GripVertical, Maximize2, Brain } from 'lucide-react';
import { cn } from '@/lib/utils';
import { motion, AnimatePresence } from 'framer-motion';

// Lazy load heavy components
const CodeEditor = lazy(() => import('@/components/builder/CodeEditor').then(module => ({ default: module.CodeEditor })));

export default function BuilderPage() {
  const location = useLocation();
  const navigate = useNavigate();
  const initialPrompt = location.state?.prompt || '';
  const resizeRef = useRef<HTMLDivElement>(null);

  // Site state
  const [htmlCode, setHtmlCode] = useState('<div class="container"><h1>Welcome</h1><p>Your website will appear here...</p></div>');
  const [cssCode, setCssCode] = useState('body { margin: 0; font-family: Inter, sans-serif; } .container { max-width: 1200px; margin: 0 auto; padding: 2rem; text-align: center; }');
  const [jsCode, setJsCode] = useState('');
  
  // Editor state
  const [viewMode, setViewMode] = useState<'code' | 'preview'>('preview');
  const [history, setHistory] = useState<Array<{ html: string; css: string; js: string }>>([]);
  const [historyIndex, setHistoryIndex] = useState(-1);
  const [lastSaved, setLastSaved] = useState<Date>(new Date());
  const [selectedDevice, setSelectedDevice] = useState('Desktop');
  const [orientation, setOrientation] = useState<Orientation>('portrait');
  
  // Layout state
  const [leftWidth, setLeftWidth] = useState(25); // percentage - 25% left, 75% right
  const [isResizing, setIsResizing] = useState(false);

  // Agent State
  const [agentSteps, setAgentSteps] = useState<AgentStep[]>([]);
  const [isAgentActive, setIsAgentActive] = useState(false);

  // Initialize history
  useEffect(() => {
    setHistory([{ html: htmlCode, css: cssCode, js: jsCode }]);
    setHistoryIndex(0);
  }, []);

  // Generate initial website from prompt
  useEffect(() => {
    if (initialPrompt) {
      console.log('Generating website from prompt:', initialPrompt);
      setHtmlCode(`<div class="container">
        <h1>Generated from: "${initialPrompt}"</h1>
        <p>AI generation in progress...</p>
      </div>`);
    }
  }, [initialPrompt]);

  // Auto-save every 30 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      setLastSaved(new Date());
    }, 30000);
    return () => clearInterval(interval);
  }, [htmlCode, cssCode, jsCode]);

  // Handle resize
  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (!isResizing) return;
      const container = resizeRef.current?.parentElement;
      if (!container) return;
      
      const containerRect = container.getBoundingClientRect();
      const newWidth = ((e.clientX - containerRect.left) / containerRect.width) * 100;
      
      // Constrain between 20% and 50%
      if (newWidth >= 20 && newWidth <= 50) {
        setLeftWidth(newWidth);
      }
    };

    const handleMouseUp = () => {
      setIsResizing(false);
    };

    if (isResizing) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
    }

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isResizing]);

  const handleCodeChange = (html: string, css: string, js: string) => {
    setHtmlCode(html);
    setCssCode(css);
    setJsCode(js);
    
    const newHistory = history.slice(0, historyIndex + 1);
    newHistory.push({ html, css, js });
    if (newHistory.length > 50) newHistory.shift();
    setHistory(newHistory);
    setHistoryIndex(newHistory.length - 1);
  };

  const undo = () => {
    if (historyIndex > 0) {
      const newIndex = historyIndex - 1;
      const state = history[newIndex];
      if (state) {
        setHtmlCode(state.html);
        setCssCode(state.css);
        setJsCode(state.js);
        setHistoryIndex(newIndex);
      }
    }
  };

  const redo = () => {
    if (historyIndex < history.length - 1) {
      const newIndex = historyIndex + 1;
      const state = history[newIndex];
      if (state) {
        setHtmlCode(state.html);
        setCssCode(state.css);
        setJsCode(state.js);
        setHistoryIndex(newIndex);
      }
    }
  };

  const handleApplyEdit = (html: string, css: string) => {
    handleCodeChange(html, css, jsCode);
  };

  const handleAgentProgress = (step: string, status: AgentStepStatus) => {
    setIsAgentActive(true);
    
    setAgentSteps(prev => {
      // Initialize steps if empty
      if (prev.length === 0) {
        return [
          { id: 'parse', label: 'Analyzing Request', status: 'pending', icon: Brain },
          { id: 'apply', label: 'Generating Code', status: 'pending', icon: Code },
        ];
      }

      return prev.map(s => {
        if (s.id === step) {
          return { ...s, status };
        }
        return s;
      });
    });

    if (step === 'apply' && (status === 'completed' || status === 'failed')) {
      setTimeout(() => setIsAgentActive(false), 3000);
    }
  };

  return (
    <div className="h-screen flex flex-col bg-background text-foreground overflow-hidden">
      {/* Top Header - Modern Glass Effect */}
      <header className="h-14 border-b border-white/5 bg-background/80 backdrop-blur-xl flex items-center justify-between px-6 shrink-0 z-50">
        <div className="flex items-center gap-6">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => navigate('/')}
            className="gap-2 hover:bg-white/5 transition-all"
          >
            <Home className="h-4 w-4" />
            <span className="font-medium">Velora</span>
          </Button>
          
          <div className="h-5 w-px bg-white/10" />
          
          <div className="flex items-center gap-1 bg-white/5 rounded-lg p-1">
            <Button
              variant="ghost"
              size="sm"
              onClick={undo}
              disabled={historyIndex <= 0}
              title="Undo (⌘Z)"
              className="h-8 w-8 p-0 hover:bg-white/10"
            >
              <Undo className="h-4 w-4" />
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={redo}
              disabled={historyIndex >= history.length - 1}
              title="Redo (⌘⇧Z)"
              className="h-8 w-8 p-0 hover:bg-white/10"
            >
              <Redo className="h-4 w-4" />
            </Button>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-white/5 text-xs text-muted-foreground border border-white/5">
            <div className="h-1.5 w-1.5 rounded-full bg-green-500 animate-pulse" />
            <Save className="h-3 w-3" />
            <span>Saved {lastSaved.toLocaleTimeString()}</span>
          </div>
        </div>
      </header>

      {/* Main Content - Resizable Split View */}
      <div className="flex-1 flex overflow-hidden relative">
        {/* Left Side - AI Assistant Only */}
        <div 
          className="flex flex-col bg-card/30 backdrop-blur-sm border-r border-white/5 shadow-2xl z-40"
          style={{ width: `${leftWidth}%` }}
        >
          {/* AI Assistant Header */}
          <div className="h-14 border-b border-white/5 bg-background/40 backdrop-blur-sm px-6 flex items-center justify-between shrink-0">
            <div className="flex items-center gap-2">
              <div className="h-8 w-8 rounded-lg bg-primary/10 flex items-center justify-center">
                <Sparkles className="h-4 w-4 text-primary" />
              </div>
              <span className="text-sm font-semibold">Velora AI</span>
            </div>
            
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setLeftWidth(25)}
              className="gap-2 text-xs text-muted-foreground hover:text-foreground"
            >
              <Maximize2 className="h-3 w-3" />
              Reset
            </Button>
          </div>

          {/* Info Section / Agent Activity */}
          <div className="flex-1 p-6 overflow-auto relative">
            <div className="absolute inset-0 p-6">
              <AnimatePresence mode="wait">
                {isAgentActive ? (
                  <motion.div
                    key="agent"
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -20 }}
                  >
                    <AgentActivity steps={agentSteps} isVisible={true} />
                  </motion.div>
                ) : (
                  <motion.div
                    key="tips"
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -20 }}
                    className="space-y-4"
                  >
                    <div className="p-4 rounded-xl bg-white/5 border border-white/5">
                      <h3 className="text-sm font-semibold mb-2">💡 Quick Tips</h3>
                      <ul className="text-xs text-muted-foreground space-y-1">
                        <li>• Use natural language to edit your website</li>
                        <li>• Switch to Code view to edit manually</li>
                        <li>• Changes are auto-saved every 30 seconds</li>
                        <li>• Use Undo/Redo to navigate history</li>
                      </ul>
                    </div>
                    
                    <div className="p-4 rounded-xl bg-primary/5 border border-primary/20">
                      <h3 className="text-sm font-semibold mb-2 text-primary">✨ Example Commands</h3>
                      <ul className="text-xs text-muted-foreground space-y-1">
                        <li>• "Change the header background to blue"</li>
                        <li>• "Add a contact form"</li>
                        <li>• "Make the text larger"</li>
                        <li>• "Center all content"</li>
                      </ul>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </div>

          {/* AI Input - Moved to Bottom */}
          <div className="p-6 border-t border-white/5 bg-gradient-to-br from-primary/5 to-transparent shrink-0">
            <NaturalLanguageInput
              onApplyEdit={handleApplyEdit}
              htmlCode={htmlCode}
              cssCode={cssCode}
              onProgress={handleAgentProgress}
            />
          </div>
        </div>

        {/* Resize Handle - Modern Draggable */}
        <div
          ref={resizeRef}
          onMouseDown={() => setIsResizing(true)}
          className={cn(
            "w-1 bg-white/5 hover:bg-primary/50 cursor-col-resize transition-all relative group z-50",
            isResizing && "bg-primary"
          )}
        >
          <div className="absolute inset-y-0 -left-1 -right-1 flex items-center justify-center">
            <div className="h-12 w-6 rounded-full bg-background border border-white/10 shadow-lg flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
              <GripVertical className="h-4 w-4 text-muted-foreground" />
            </div>
          </div>
        </div>

        {/* Right Side - Code Editor or Preview */}
        <div 
          className="flex flex-col bg-background relative z-0"
          style={{ width: `${100 - leftWidth}%` }}
        >
          {/* Header - Code/Preview Toggle + Device Selector */}
          <div className="h-14 border-b border-white/5 bg-background/60 backdrop-blur-sm shrink-0 flex items-center justify-between px-4">
            {/* Code/Preview Toggle */}
            <Tabs value={viewMode} onValueChange={(v) => setViewMode(v as any)}>
              <TabsList className="bg-white/5 p-1 border border-white/5">
                <TabsTrigger value="preview" className="gap-2 data-[state=active]:bg-white/10 data-[state=active]:text-white">
                  <Eye className="h-4 w-4" />
                  <span className="font-medium">Preview</span>
                </TabsTrigger>
                <TabsTrigger value="code" className="gap-2 data-[state=active]:bg-white/10 data-[state=active]:text-white">
                  <Code className="h-4 w-4" />
                  <span className="font-medium">Code</span>
                </TabsTrigger>
              </TabsList>
            </Tabs>

            {/* Device Selector (only show in preview mode) */}
            {viewMode === 'preview' && (
              <DeviceEmulator
                selectedDevice={selectedDevice}
                orientation={orientation}
                onDeviceChange={setSelectedDevice}
                onOrientationChange={setOrientation}
              />
            )}
          </div>

          {/* Content Area */}
          <div className="flex-1 overflow-hidden">
            <Suspense fallback={
              <div className="flex items-center justify-center h-full">
                <div className="text-center space-y-2">
                  <div className="h-8 w-8 border-2 border-primary border-t-transparent rounded-full animate-spin mx-auto" />
                  <p className="text-sm text-muted-foreground">Loading...</p>
                </div>
              </div>
            }>
              {viewMode === 'preview' ? (
                <div className="h-full bg-[#121212]">
                  <SitePreview
                    htmlCode={htmlCode}
                    cssCode={cssCode}
                    jsCode={jsCode}
                  />
                </div>
              ) : (
                <CodeEditor
                  htmlCode={htmlCode}
                  cssCode={cssCode}
                  jsCode={jsCode}
                  onHtmlChange={(html) => handleCodeChange(html, cssCode, jsCode)}
                  onCssChange={(css) => handleCodeChange(htmlCode, css, jsCode)}
                  onJsChange={(js) => handleCodeChange(htmlCode, cssCode, js)}
                  height="100%"
                />
              )}
            </Suspense>
          </div>
        </div>
      </div>

      {/* Performance Overlay */}
      <PerformanceOverlay
        htmlCode={htmlCode}
        cssCode={cssCode}
        jsCode={jsCode}
      />
    </div>
  );
}
