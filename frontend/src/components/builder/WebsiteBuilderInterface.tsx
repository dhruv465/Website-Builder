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
  X
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

  const currentPage = pages.find(p => p.id === currentPageId) || pages[0];

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
    <div className="flex h-screen bg-gray-50 dark:bg-gray-950">
      {/* Left Sidebar - Editor Panel */}
      <motion.div
        initial={{ x: -20, opacity: 0 }}
        animate={{ x: 0, opacity: 1 }}
        className="w-[400px] bg-white dark:bg-gray-900 border-r border-gray-200 dark:border-gray-800 flex flex-col overflow-hidden"
      >
        {/* Header */}
        <div className="p-4 border-b border-gray-200 dark:border-gray-800">
          <div className="flex items-center gap-2 mb-3">
            {onBack && (
              <Button
                variant="ghost"
                size="icon"
                onClick={onBack}
                className="h-8 w-8"
              >
                <ArrowLeft className="h-4 w-4" />
              </Button>
            )}
            <h1 className="text-lg font-semibold text-gray-900 dark:text-white">
              {projectName}
            </h1>
          </div>
          
          {/* Save Status */}
          <div className="flex items-center gap-2 text-sm">
            <AnimatePresence mode="wait">
              {saveStatus === 'saving' && (
                <motion.div
                  key="saving"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="flex items-center gap-1 text-gray-500"
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
                  className="flex items-center gap-1 text-green-600 dark:text-green-400"
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
                  className="flex items-center gap-1 text-red-600 dark:text-red-400"
                >
                  <X className="h-3 w-3" />
                  <span>Error saving</span>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>

        {/* Tabs */}
        <Tabs value={currentPageId} onValueChange={setCurrentPageId} className="flex-1 flex flex-col overflow-hidden">
          <TabsList className="w-full justify-start rounded-none border-b border-gray-200 dark:border-gray-800 bg-transparent p-0">
            {pages.map(page => (
              <TabsTrigger
                key={page.id}
                value={page.id}
                className="rounded-none border-b-2 border-transparent data-[state=active]:border-blue-600 data-[state=active]:bg-transparent px-6 py-3"
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
              className="flex-1 overflow-y-auto p-6 space-y-6 mt-0"
            >
              {/* Page Title */}
              <div className="space-y-2">
                <Label htmlFor="page-title" className="text-sm font-medium">
                  Page Title
                </Label>
                <Input
                  id="page-title"
                  value={page.content.title}
                  onChange={(e) => updatePageContent('title', e.target.value)}
                  placeholder="Enter page title"
                  className="w-full"
                />
              </div>

              {/* Heading */}
              <div className="space-y-2">
                <Label htmlFor="heading" className="text-sm font-medium">
                  Heading
                </Label>
                <Input
                  id="heading"
                  value={page.content.heading}
                  onChange={(e) => updatePageContent('heading', e.target.value)}
                  placeholder="Enter heading"
                  className="w-full"
                />
              </div>

              {/* Main Content */}
              <div className="space-y-2">
                <Label htmlFor="content" className="text-sm font-medium">
                  Content
                </Label>
                <Textarea
                  id="content"
                  value={page.content.body}
                  onChange={(e) => updatePageContent('body', e.target.value)}
                  placeholder="Enter your content here..."
                  className="w-full min-h-[200px] resize-none"
                  rows={10}
                />
                <p className="text-xs text-gray-500">
                  {page.content.body.length} characters
                </p>
              </div>

              {/* Featured Image */}
              <div className="space-y-2">
                <Label className="text-sm font-medium">Featured Image</Label>
                <div className="border-2 border-dashed border-gray-300 dark:border-gray-700 rounded-lg p-4 hover:border-gray-400 dark:hover:border-gray-600 transition-colors">
                  {page.content.image ? (
                    <div className="space-y-3">
                      <img
                        src={page.content.image}
                        alt="Preview"
                        className="w-full h-32 object-cover rounded"
                      />
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => updatePageContent('image', '')}
                        className="w-full"
                      >
                        Remove Image
                      </Button>
                    </div>
                  ) : (
                    <label className="flex flex-col items-center gap-2 cursor-pointer">
                      <Upload className="h-8 w-8 text-gray-400" />
                      <span className="text-sm text-gray-600 dark:text-gray-400">
                        Click to upload or drag and drop
                      </span>
                      <span className="text-xs text-gray-500">
                        PNG, JPG, GIF up to 10MB
                      </span>
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
        <div className="p-4 border-t border-gray-200 dark:border-gray-800 space-y-2">
          <Button
            onClick={handleSave}
            disabled={!isDirty || saveStatus === 'saving'}
            className="w-full"
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
              className="w-full"
            >
              <Eye className="mr-2 h-4 w-4" />
              Publish
            </Button>
          )}
        </div>
      </motion.div>

      {/* Right Side - Live Preview Panel */}
      <div className="flex-1 flex flex-col bg-gray-100 dark:bg-gray-900">
        {/* Preview Toolbar */}
        <div className="bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-800 p-3 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
              Preview
            </span>
          </div>

          <div className="flex items-center gap-2">
            {/* Device Selector */}
            <div className="flex items-center gap-1 bg-gray-100 dark:bg-gray-800 rounded-lg p-1">
              <Button
                variant={device === 'desktop' ? 'default' : 'ghost'}
                size="icon"
                onClick={() => setDevice('desktop')}
                className="h-8 w-8"
              >
                <Monitor className="h-4 w-4" />
              </Button>
              <Button
                variant={device === 'tablet' ? 'default' : 'ghost'}
                size="icon"
                onClick={() => setDevice('tablet')}
                className="h-8 w-8"
              >
                <Tablet className="h-4 w-4" />
              </Button>
              <Button
                variant={device === 'mobile' ? 'default' : 'ghost'}
                size="icon"
                onClick={() => setDevice('mobile')}
                className="h-8 w-8"
              >
                <Smartphone className="h-4 w-4" />
              </Button>
            </div>

            {/* Refresh */}
            <Button
              variant="ghost"
              size="icon"
              onClick={refreshPreview}
              className="h-8 w-8"
            >
              <RotateCcw className="h-4 w-4" />
            </Button>

            {/* Open in new tab */}
            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8"
            >
              <ExternalLink className="h-4 w-4" />
            </Button>
          </div>
        </div>

        {/* Preview Area */}
        <div className="flex-1 flex items-center justify-center p-8 overflow-auto">
          <motion.div
            key={`${device}-${previewKey}`}
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.2 }}
            className={cn(
              'bg-white dark:bg-gray-950 shadow-2xl overflow-hidden',
              device === 'desktop' && 'w-full h-full rounded-lg',
              device === 'tablet' && 'rounded-xl',
              device === 'mobile' && 'rounded-2xl'
            )}
            style={{
              width: dimensions.width,
              height: dimensions.height,
              maxWidth: '100%',
              maxHeight: '100%',
            }}
          >
            {/* Live Preview Content */}
            <div className="h-full overflow-auto">
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
    <div className="min-h-full bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
      {/* Navigation */}
      <nav className="bg-white dark:bg-gray-900 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <span className="text-xl font-bold text-gray-900 dark:text-white">
                Logo
              </span>
            </div>
            <div className="flex items-center gap-6">
              <a href="#" className="text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white">
                Home
              </a>
              <a href="#" className="text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white">
                About
              </a>
              <a href="#" className="text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white">
                Contact
              </a>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="text-center space-y-8">
          {page.content.image && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex justify-center"
            >
              <img
                src={page.content.image}
                alt={page.content.heading}
                className="w-full max-w-2xl h-64 object-cover rounded-2xl shadow-xl"
              />
            </motion.div>
          )}

          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="text-5xl font-bold text-gray-900 dark:text-white"
          >
            {page.content.heading || 'Your Heading Here'}
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="text-xl text-gray-600 dark:text-gray-300 max-w-3xl mx-auto leading-relaxed"
          >
            {page.content.body || 'Your content will appear here...'}
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="flex justify-center gap-4"
          >
            <button className="px-8 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors">
              Get Started
            </button>
            <button className="px-8 py-3 bg-white dark:bg-gray-800 text-gray-900 dark:text-white rounded-lg font-medium border border-gray-300 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors">
              Learn More
            </button>
          </motion.div>
        </div>
      </div>

      {/* Features Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {[1, 2, 3].map((i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 + i * 0.1 }}
              className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-lg"
            >
              <div className="w-12 h-12 bg-blue-100 dark:bg-blue-900 rounded-lg flex items-center justify-center mb-4">
                <span className="text-2xl">✨</span>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                Feature {i}
              </h3>
              <p className="text-gray-600 dark:text-gray-300">
                Description of feature {i} goes here.
              </p>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  );
}
