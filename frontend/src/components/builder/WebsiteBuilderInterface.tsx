import { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Save, 
  Eye, 
  Monitor, 
  Tablet, 
  Smartphone, 
  RotateCcw, 
  ExternalLink,
  Upload,
  Check,
  Loader2,
  ArrowLeft,
  X,
  Sparkles,
  Zap,
  Layout
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { cn } from '@/lib/utils';

// Types
type DeviceType = 'desktop' | 'tablet' | 'mobile';
type SaveStatus = 'idle' | 'saving' | 'saved' | 'error';

interface PageContent {
  id: string;
  title: string;
  heading: string;
  body: string;
  image: string;
  settings: Record<string, any>;
}

interface Page {
  id: string;
  title: string;
  content: PageContent;
}

interface WebsiteBuilderInterfaceProps {
  projectName?: string;
  initialPages?: Page[];
  onSave?: (pages: Page[]) => Promise<void>;
  onPublish?: () => void;
  onBack?: () => void;
  autoSaveInterval?: number;
}

export function WebsiteBuilderInterface({
  projectName = 'My Website',
  initialPages = [],
  onSave,
  onPublish,
  onBack,
  autoSaveInterval = 3000,
}: WebsiteBuilderInterfaceProps) {
  // State
  const [pages, setPages] = useState<Page[]>(initialPages.length > 0 ? initialPages : [
    {
      id: 'mission',
      title: 'Mission',
      content: {
        id: 'mission',
        title: 'Our Mission',
        heading: 'Our Mission',
        body: 'We are dedicated to creating innovative solutions that make a difference.',
        image: '',
        settings: {},
      },
    },
    {
      id: 'chapter',
      title: 'Chapter',
      content: {
        id: 'chapter',
        title: 'Our Chapter',
        heading: 'Our Chapter',
        body: 'Learn about our chapter and what we do.',
        image: '',
        settings: {},
      },
    },
    {
      id: 'about',
      title: 'About',
      content: {
        id: 'about',
        title: 'About Us',
        heading: 'About Us',
        body: 'Discover our story and values.',
        image: '',
        settings: {},
      },
    },
  ]);
  
  const [currentPageId, setCurrentPageId] = useState<string>(pages[0]?.id || 'mission');
  const [device, setDevice] = useState<DeviceType>('desktop');
  const [saveStatus, setSaveStatus] = useState<SaveStatus>('idle');
  const [previewKey, setPreviewKey] = useState(0);
  const [isDirty, setIsDirty] = useState(false);

  const currentPage = pages.find(p => p.id === currentPageId) || pages[0] || {
    id: 'error',
    title: 'Error',
    content: {
      id: 'error',
      title: 'Error',
      heading: 'Error',
      body: 'Page not found',
      image: '',
      settings: {}
    }
  };

  // Auto-save functionality
  useEffect(() => {
    if (!isDirty || !onSave) return;

    const timer = setTimeout(async () => {
      await handleSave();
    }, autoSaveInterval);

    return () => clearTimeout(timer);
  }, [pages, isDirty, autoSaveInterval]);

  // Handle save
  const handleSave = useCallback(async () => {
    if (!onSave) return;

    setSaveStatus('saving');
    try {
      await onSave(pages);
      setSaveStatus('saved');
      setIsDirty(false);
      setTimeout(() => setSaveStatus('idle'), 2000);
    } catch (error) {
      setSaveStatus('error');
      setTimeout(() => setSaveStatus('idle'), 3000);
    }
  }, [pages, onSave]);

  // Update page content
  const updatePageContent = useCallback((field: keyof PageContent, value: string) => {
    setPages(prev => prev.map(page => 
      page.id === currentPageId
        ? { ...page, content: { ...page.content, [field]: value } }
        : page
    ));
    setIsDirty(true);
  }, [currentPageId]);

  // Handle image upload
  const handleImageUpload = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onloadend = () => {
      updatePageContent('image', reader.result as string);
    };
    reader.readAsDataURL(file);
  }, [updatePageContent]);

  // Refresh preview
  const refreshPreview = useCallback(() => {
    setPreviewKey(prev => prev + 1);
  }, []);

  // Device viewport dimensions
  const getDeviceDimensions = () => {
    switch (device) {
      case 'mobile':
        return { width: '375px', height: '667px' };
      case 'tablet':
        return { width: '768px', height: '1024px' };
      default:
        return { width: '100%', height: '100%' };
    }
  };

  const dimensions = getDeviceDimensions();

  return (
    <div className="flex h-screen bg-black text-white overflow-hidden font-sans selection:bg-primary/30">
      {/* Background Effects */}
      <div className="fixed inset-0 z-0 pointer-events-none">
        <div className="absolute top-[-20%] left-[-10%] w-[50%] h-[50%] rounded-full bg-primary/5 blur-[120px]" />
        <div className="absolute bottom-[-20%] right-[-10%] w-[50%] h-[50%] rounded-full bg-accent/5 blur-[120px]" />
        <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20 brightness-100 contrast-150 mix-blend-overlay" />
      </div>

      {/* Left Sidebar - Editor Panel */}
      <motion.div
        initial={{ x: -20, opacity: 0 }}
        animate={{ x: 0, opacity: 1 }}
        className="relative z-10 w-[400px] bg-black/40 backdrop-blur-xl border-r border-white/10 flex flex-col overflow-hidden"
      >
        {/* Header */}
        <div className="p-4 border-b border-white/10">
          <div className="flex items-center gap-3 mb-4">
            {onBack && (
              <Button
                variant="ghost"
                size="icon"
                onClick={onBack}
                className="h-8 w-8 text-white/70 hover:text-white hover:bg-white/10"
              >
                <ArrowLeft className="h-4 w-4" />
              </Button>
            )}
            <div className="flex items-center gap-2">
               <div className="p-1.5 bg-primary/20 rounded-lg">
                  <Layout className="h-4 w-4 text-primary" />
               </div>
               <h1 className="text-sm font-medium text-white">
                  {projectName}
               </h1>
            </div>
          </div>
          
          {/* Save Status */}
          <div className="flex items-center justify-between">
             <div className="flex items-center gap-2 text-xs text-white/50">
               <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
               <span>Online</span>
             </div>
             <div className="flex items-center gap-2 text-xs">
               <AnimatePresence mode="wait">
                 {saveStatus === 'saving' && (
                   <motion.div
                     key="saving"
                     initial={{ opacity: 0 }}
                     animate={{ opacity: 1 }}
                     exit={{ opacity: 0 }}
                     className="flex items-center gap-1 text-white/50"
                   >
                     <Loader2 className="h-3 w-3 animate-spin" />
                     <span>Saving...</span>
                   </motion.div>
                 )}
                 {saveStatus === 'saved' && (
                   <motion.div
                     key="saved"
                     initial={{ opacity: 0, scale: 0.8 }}
                     animate={{ opacity: 1, scale: 1 }}
                     exit={{ opacity: 0 }}
                     className="flex items-center gap-1 text-green-400"
                   >
                     <Check className="h-3 w-3" />
                     <span>Saved</span>
                   </motion.div>
                 )}
                 {saveStatus === 'error' && (
                   <motion.div
                     key="error"
                     initial={{ opacity: 0 }}
                     animate={{ opacity: 1 }}
                     exit={{ opacity: 0 }}
                     className="flex items-center gap-1 text-red-400"
                   >
                     <X className="h-3 w-3" />
                     <span>Error</span>
                   </motion.div>
                 )}
               </AnimatePresence>
             </div>
          </div>
        </div>

        {/* Tabs */}
        <Tabs value={currentPageId} onValueChange={setCurrentPageId} className="flex-1 flex flex-col overflow-hidden">
          <TabsList className="w-full justify-start rounded-none border-b border-white/10 bg-transparent p-0">
            {pages.map(page => (
              <TabsTrigger
                key={page.id}
                value={page.id}
                className="rounded-none border-b-2 border-transparent data-[state=active]:border-primary data-[state=active]:text-primary data-[state=active]:bg-primary/5 px-6 py-3 text-white/60 hover:text-white transition-colors"
              >
                {page.title}
              </TabsTrigger>
            ))}
          </TabsList>

          {/* Content for each tab */}
          {pages.map(page => (
            <TabsContent
              key={page.id}
              value={page.id}
              className="flex-1 overflow-y-auto p-6 space-y-6 mt-0 custom-scrollbar"
            >
              {/* Page Title */}
              <div className="space-y-2">
                <Label htmlFor="page-title" className="text-xs font-medium text-white/70 uppercase tracking-wider">
                  Page Title
                </Label>
                <Input
                  id="page-title"
                  value={page.content.title}
                  onChange={(e) => updatePageContent('title', e.target.value)}
                  placeholder="Enter page title"
                  className="w-full bg-white/5 border-white/10 text-white placeholder:text-white/20 focus:border-primary/50 focus:ring-0"
                />
              </div>

              {/* Heading */}
              <div className="space-y-2">
                <Label htmlFor="heading" className="text-xs font-medium text-white/70 uppercase tracking-wider">
                  Heading
                </Label>
                <Input
                  id="heading"
                  value={page.content.heading}
                  onChange={(e) => updatePageContent('heading', e.target.value)}
                  placeholder="Enter heading"
                  className="w-full bg-white/5 border-white/10 text-white placeholder:text-white/20 focus:border-primary/50 focus:ring-0"
                />
              </div>

              {/* Main Content */}
              <div className="space-y-2">
                <Label htmlFor="content" className="text-xs font-medium text-white/70 uppercase tracking-wider">
                  Content
                </Label>
                <Textarea
                  id="content"
                  value={page.content.body}
                  onChange={(e) => updatePageContent('body', e.target.value)}
                  placeholder="Enter your content here..."
                  className="w-full min-h-[200px] resize-none bg-white/5 border-white/10 text-white placeholder:text-white/20 focus:border-primary/50 focus:ring-0"
                  rows={10}
                />
                <p className="text-xs text-white/30 text-right">
                  {page.content.body.length} characters
                </p>
              </div>

              {/* Featured Image */}
              <div className="space-y-2">
                <Label className="text-xs font-medium text-white/70 uppercase tracking-wider">Featured Image</Label>
                <div className="border-2 border-dashed border-white/10 rounded-xl p-4 hover:border-white/20 hover:bg-white/5 transition-all group">
                  {page.content.image ? (
                    <div className="space-y-3">
                      <div className="relative rounded-lg overflow-hidden">
                         <img
                           src={page.content.image}
                           alt="Preview"
                           className="w-full h-32 object-cover"
                         />
                         <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                           <Button
                             variant="destructive"
                             size="sm"
                             onClick={() => updatePageContent('image', '')}
                             className="h-8"
                           >
                             Remove
                           </Button>
                         </div>
                      </div>
                    </div>
                  ) : (
                    <label className="flex flex-col items-center gap-3 cursor-pointer py-4">
                      <div className="p-3 rounded-full bg-white/5 group-hover:bg-white/10 transition-colors">
                        <Upload className="h-5 w-5 text-white/50 group-hover:text-white" />
                      </div>
                      <div className="text-center">
                         <span className="text-sm text-white/70 group-hover:text-white transition-colors">
                           Click to upload image
                         </span>
                         <p className="text-xs text-white/30 mt-1">
                           PNG, JPG up to 10MB
                         </p>
                      </div>
                      <input
                        type="file"
                        accept="image/*"
                        onChange={handleImageUpload}
                        className="hidden"
                      />
                    </label>
                  )}
                </div>
              </div>
            </TabsContent>
          ))}
        </Tabs>

        {/* Action Buttons */}
        <div className="p-4 border-t border-white/10 space-y-3 bg-black/20">
          <Button
            onClick={handleSave}
            disabled={!isDirty || saveStatus === 'saving'}
            className="w-full bg-primary hover:bg-primary/90 text-white"
          >
            {saveStatus === 'saving' ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Saving...
              </>
            ) : (
              <>
                <Save className="mr-2 h-4 w-4" />
                Save Changes
              </>
            )}
          </Button>
          
          {onPublish && (
            <Button
              onClick={onPublish}
              variant="outline"
              className="w-full border-white/10 bg-white/5 hover:bg-white/10 text-white hover:text-white"
            >
              <Eye className="mr-2 h-4 w-4" />
              Publish
            </Button>
          )}
        </div>
      </motion.div>

      {/* Right Side - Live Preview Panel */}
      <div className="flex-1 flex flex-col relative z-10">
        {/* Preview Toolbar */}
        <div className="bg-black/40 backdrop-blur-xl border-b border-white/10 p-3 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-sm font-medium text-white/70">
              Live Preview
            </span>
            <span className="px-2 py-0.5 rounded-full bg-white/10 text-[10px] text-white/50 border border-white/5">
               Read-only
            </span>
          </div>

          <div className="flex items-center gap-2">
            {/* Device Selector */}
            <div className="flex items-center gap-1 bg-white/5 rounded-lg p-1 border border-white/5">
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setDevice('desktop')}
                className={cn(
                  "h-7 w-7 rounded-md transition-all",
                  device === 'desktop' ? "bg-white/10 text-white" : "text-white/40 hover:text-white hover:bg-white/5"
                )}
              >
                <Monitor className="h-3.5 w-3.5" />
              </Button>
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setDevice('tablet')}
                className={cn(
                  "h-7 w-7 rounded-md transition-all",
                  device === 'tablet' ? "bg-white/10 text-white" : "text-white/40 hover:text-white hover:bg-white/5"
                )}
              >
                <Tablet className="h-3.5 w-3.5" />
              </Button>
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setDevice('mobile')}
                className={cn(
                  "h-7 w-7 rounded-md transition-all",
                  device === 'mobile' ? "bg-white/10 text-white" : "text-white/40 hover:text-white hover:bg-white/5"
                )}
              >
                <Smartphone className="h-3.5 w-3.5" />
              </Button>
            </div>

            <div className="w-px h-4 bg-white/10 mx-1" />

            {/* Refresh */}
            <Button
              variant="ghost"
              size="icon"
              onClick={refreshPreview}
              className="h-8 w-8 text-white/50 hover:text-white hover:bg-white/5"
            >
              <RotateCcw className="h-4 w-4" />
            </Button>

            {/* Open in new tab */}
            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8 text-white/50 hover:text-white hover:bg-white/5"
            >
              <ExternalLink className="h-4 w-4" />
            </Button>
          </div>
        </div>

        {/* Preview Area */}
        <div className="flex-1 flex items-center justify-center p-8 overflow-hidden bg-black/20">
          <motion.div
            key={`${device}-${previewKey}`}
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.2 }}
            className={cn(
              'bg-black shadow-2xl overflow-hidden border border-white/10 relative',
              device === 'desktop' && 'w-full h-full rounded-lg',
              device === 'tablet' && 'rounded-xl',
              device === 'mobile' && 'rounded-3xl border-[8px] border-black'
            )}
            style={{
              width: dimensions.width,
              height: dimensions.height,
              maxWidth: '100%',
              maxHeight: '100%',
            }}
          >
            {/* Live Preview Content */}
            <div className="h-full overflow-auto custom-scrollbar bg-black">
              <PreviewContent page={currentPage} />
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  );
}

// Preview Content Component
function PreviewContent({ page }: { page: Page }) {
  return (
    <div className="min-h-full bg-black text-white font-sans selection:bg-primary/30">
      {/* Navigation */}
      <nav className="border-b border-white/10 bg-black/50 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center gap-2">
               <Sparkles className="h-5 w-5 text-primary" />
               <span className="text-lg font-bold tracking-tight">Velora</span>
            </div>
            <div className="flex items-center gap-8">
              <a href="#" className="text-sm text-white/70 hover:text-white transition-colors">Home</a>
              <a href="#" className="text-sm text-white/70 hover:text-white transition-colors">About</a>
              <a href="#" className="text-sm text-white/70 hover:text-white transition-colors">Contact</a>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <div className="relative overflow-hidden">
         <div className="absolute inset-0 bg-gradient-to-b from-primary/10 to-transparent opacity-50" />
         <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24 relative z-10">
           <div className="text-center space-y-8">
             {page.content.image && (
               <motion.div
                 initial={{ opacity: 0, scale: 0.95 }}
                 animate={{ opacity: 1, scale: 1 }}
                 className="flex justify-center mb-12"
               >
                 <div className="relative rounded-2xl overflow-hidden shadow-2xl border border-white/10 group">
                    <div className="absolute inset-0 bg-gradient-to-tr from-primary/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
                    <img
                      src={page.content.image}
                      alt={page.content.heading}
                      className="w-full max-w-3xl h-[400px] object-cover"
                    />
                 </div>
               </motion.div>
             )}

             <motion.h1
               initial={{ opacity: 0, y: 20 }}
               animate={{ opacity: 1, y: 0 }}
               transition={{ delay: 0.1 }}
               className="text-5xl md:text-7xl font-bold tracking-tight"
             >
               <span className="bg-clip-text text-transparent bg-gradient-to-r from-white via-white to-white/50">
                  {page.content.heading || 'Your Heading Here'}
               </span>
             </motion.h1>

             <motion.p
               initial={{ opacity: 0, y: 20 }}
               animate={{ opacity: 1, y: 0 }}
               transition={{ delay: 0.2 }}
               className="text-xl text-white/60 max-w-2xl mx-auto leading-relaxed"
             >
               {page.content.body || 'Your content will appear here...'}
             </motion.p>

             <motion.div
               initial={{ opacity: 0, y: 20 }}
               animate={{ opacity: 1, y: 0 }}
               transition={{ delay: 0.3 }}
               className="flex justify-center gap-4 pt-4"
             >
               <button className="px-8 py-4 bg-white text-black rounded-full font-medium hover:bg-white/90 transition-all hover:scale-105">
                 Get Started
               </button>
               <button className="px-8 py-4 bg-white/5 text-white rounded-full font-medium border border-white/10 hover:bg-white/10 transition-all">
                 Learn More
               </button>
             </motion.div>
           </div>
         </div>
      </div>

      {/* Features Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24 border-t border-white/5">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {[1, 2, 3].map((i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 + i * 0.1 }}
              className="p-8 rounded-3xl bg-white/5 border border-white/5 hover:bg-white/10 transition-colors group"
            >
              <div className="w-12 h-12 bg-primary/20 rounded-2xl flex items-center justify-center mb-6 text-primary group-hover:scale-110 transition-transform">
                <Zap className="h-6 w-6" />
              </div>
              <h3 className="text-xl font-semibold text-white mb-3">
                Feature {i}
              </h3>
              <p className="text-white/50 leading-relaxed">
                Experience the power of our platform with this amazing feature that changes everything.
              </p>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  );
}
