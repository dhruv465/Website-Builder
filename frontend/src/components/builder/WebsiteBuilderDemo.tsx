import { Link } from 'react-router-dom';
import { ExternalLink, Code, Layout, Smartphone } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

export function WebsiteBuilderDemo() {
  return (
    <div className="container mx-auto py-12 px-4 max-w-6xl">
      <div className="space-y-8">
        {/* Header */}
        <div className="text-center space-y-4">
          <h1 className="text-4xl font-bold text-gray-900 dark:text-white">
            Website Builder Interface
          </h1>
          <p className="text-xl text-gray-600 dark:text-gray-300 max-w-3xl mx-auto">
            A professional split-screen website builder with live preview, multi-page editing, 
            and real-time updates.
          </p>
          <div className="flex justify-center gap-4 pt-4">
            <Link to="/dashboard/website-builder">
              <Button size="lg" className="gap-2">
                <ExternalLink className="h-5 w-5" />
                Open Builder
              </Button>
            </Link>
            <a 
              href="https://github.com/yourusername/website-builder" 
              target="_blank" 
              rel="noopener noreferrer"
            >
              <Button size="lg" variant="outline" className="gap-2">
                <Code className="h-5 w-5" />
                View Code
              </Button>
            </a>
          </div>
        </div>

        {/* Features Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 pt-8">
          <Card>
            <CardHeader>
              <div className="w-12 h-12 bg-blue-100 dark:bg-blue-900 rounded-lg flex items-center justify-center mb-2">
                <Layout className="h-6 w-6 text-blue-600 dark:text-blue-400" />
              </div>
              <CardTitle>Split-Screen Layout</CardTitle>
              <CardDescription>
                Edit content on the left, see live preview on the right
              </CardDescription>
            </CardHeader>
          </Card>

          <Card>
            <CardHeader>
              <div className="w-12 h-12 bg-green-100 dark:bg-green-900 rounded-lg flex items-center justify-center mb-2">
                <Smartphone className="h-6 w-6 text-green-600 dark:text-green-400" />
              </div>
              <CardTitle>Responsive Preview</CardTitle>
              <CardDescription>
                Test your site on desktop, tablet, and mobile viewports
              </CardDescription>
            </CardHeader>
          </Card>

          <Card>
            <CardHeader>
              <div className="w-12 h-12 bg-purple-100 dark:bg-purple-900 rounded-lg flex items-center justify-center mb-2">
                <span className="text-2xl">⚡</span>
              </div>
              <CardTitle>Real-Time Updates</CardTitle>
              <CardDescription>
                See changes instantly as you type with auto-save
              </CardDescription>
            </CardHeader>
          </Card>

          <Card>
            <CardHeader>
              <div className="w-12 h-12 bg-orange-100 dark:bg-orange-900 rounded-lg flex items-center justify-center mb-2">
                <span className="text-2xl">📝</span>
              </div>
              <CardTitle>Multi-Page Editing</CardTitle>
              <CardDescription>
                Switch between pages with tab-based navigation
              </CardDescription>
            </CardHeader>
          </Card>

          <Card>
            <CardHeader>
              <div className="w-12 h-12 bg-pink-100 dark:bg-pink-900 rounded-lg flex items-center justify-center mb-2">
                <span className="text-2xl">🖼️</span>
              </div>
              <CardTitle>Image Upload</CardTitle>
              <CardDescription>
                Drag-and-drop image uploading with instant preview
              </CardDescription>
            </CardHeader>
          </Card>

          <Card>
            <CardHeader>
              <div className="w-12 h-12 bg-yellow-100 dark:bg-yellow-900 rounded-lg flex items-center justify-center mb-2">
                <span className="text-2xl">💾</span>
              </div>
              <CardTitle>Auto-Save</CardTitle>
              <CardDescription>
                Automatic saving with visual status indicators
              </CardDescription>
            </CardHeader>
          </Card>
        </div>

        {/* Code Example */}
        <Card className="mt-8">
          <CardHeader>
            <CardTitle>Quick Start</CardTitle>
            <CardDescription>
              Get started with the Website Builder Interface in minutes
            </CardDescription>
          </CardHeader>
          <CardContent>
            <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto">
              <code>{`import { WebsiteBuilderInterface } from '@/components/builder';

function MyBuilderPage() {
  const handleSave = async (pages) => {
    await api.savePages(pages);
  };

  return (
    <WebsiteBuilderInterface
      projectName="My Website"
      onSave={handleSave}
      onPublish={() => console.log('Publishing...')}
      autoSaveInterval={3000}
    />
  );
}`}</code>
            </pre>
          </CardContent>
        </Card>

        {/* Key Features List */}
        <Card>
          <CardHeader>
            <CardTitle>Key Features</CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2 text-gray-700 dark:text-gray-300">
              <li className="flex items-start gap-2">
                <span className="text-green-500 mt-1">✓</span>
                <span>Split-screen editor with live preview panel</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-green-500 mt-1">✓</span>
                <span>Tab-based navigation for multiple pages/sections</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-green-500 mt-1">✓</span>
                <span>Real-time preview updates as you type</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-green-500 mt-1">✓</span>
                <span>Responsive device preview (Desktop/Tablet/Mobile)</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-green-500 mt-1">✓</span>
                <span>Auto-save with visual status indicators</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-green-500 mt-1">✓</span>
                <span>Image upload with drag-and-drop support</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-green-500 mt-1">✓</span>
                <span>Character count for content fields</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-green-500 mt-1">✓</span>
                <span>Smooth animations with Framer Motion</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-green-500 mt-1">✓</span>
                <span>Dark mode support</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-green-500 mt-1">✓</span>
                <span>TypeScript with full type safety</span>
              </li>
            </ul>
          </CardContent>
        </Card>

        {/* CTA */}
        <div className="text-center pt-8">
          <Link to="/dashboard/website-builder">
            <Button size="lg" className="gap-2">
              <ExternalLink className="h-5 w-5" />
              Try it Now
            </Button>
          </Link>
        </div>
      </div>
    </div>
  );
}
