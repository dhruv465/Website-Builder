import React, { useState, useRef } from 'react';
import { WYSIWYGEditor } from './WYSIWYGEditor';
import { SitePreview } from './SitePreview';
import { VersionHistory } from './VersionHistory';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { CheckCircle2, AlertCircle } from 'lucide-react';
import { SiteVersion } from '@/lib/types/api';

export const WYSIWYGEditorExample: React.FC = () => {
  const iframeRef = useRef<HTMLIFrameElement>(null);
  
  // Sample site data
  const [siteId] = useState('sample-site-123');
  const [htmlCode, setHtmlCode] = useState(`
    <div style="padding: 40px; max-width: 800px; margin: 0 auto;">
      <h1 style="color: #1a1a1a; margin-bottom: 20px;">Welcome to WYSIWYG Editor</h1>
      <p style="color: #666; font-size: 18px; line-height: 1.6; margin-bottom: 20px;">
        Click on any element to edit it. You can change text content, colors, font sizes, and alignment.
      </p>
      <div style="background: #f5f5f5; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
        <h2 style="color: #333; margin-bottom: 10px;">Features</h2>
        <ul style="color: #666; line-height: 1.8;">
          <li>Real-time text editing</li>
          <li>Style customization (color, size, alignment)</li>
          <li>Undo/Redo functionality</li>
          <li>Element deletion</li>
          <li>Auto-save to backend</li>
        </ul>
      </div>
      <button style="background: #0070f3; color: white; padding: 12px 24px; border: none; border-radius: 6px; cursor: pointer; font-size: 16px;">
        Click to Edit Me
      </button>
    </div>
  `);
  
  const [cssCode, setCssCode] = useState(`
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
    button:hover {
      background: #0051cc !important;
    }
  `);
  
  const [jsCode] = useState('');
  
  const [saveStatus, setSaveStatus] = useState<'idle' | 'success' | 'error'>('idle');
  const [saveMessage, setSaveMessage] = useState('');

  // Sample version history
  const [versions] = useState<SiteVersion[]>([
    {
      id: 'v1',
      version_number: 1,
      html_code: htmlCode,
      css_code: cssCode,
      js_code: jsCode,
      created_at: new Date(Date.now() - 3600000).toISOString(),
      change_description: 'Initial version',
    },
    {
      id: 'v2',
      version_number: 2,
      html_code: htmlCode,
      css_code: cssCode,
      js_code: jsCode,
      created_at: new Date(Date.now() - 1800000).toISOString(),
      change_description: 'Updated heading text',
    },
    {
      id: 'v3',
      version_number: 3,
      html_code: htmlCode,
      css_code: cssCode,
      js_code: jsCode,
      created_at: new Date().toISOString(),
      change_description: 'Current version',
    },
  ]);

  const handleCodeUpdate = (html: string, css?: string) => {
    setHtmlCode(html);
    if (css !== undefined) setCssCode(css);
  };

  const handleSaveSuccess = () => {
    setSaveStatus('success');
    setSaveMessage('Changes saved successfully!');
    setTimeout(() => setSaveStatus('idle'), 3000);
  };

  const handleSaveError = (error: Error) => {
    setSaveStatus('error');
    setSaveMessage(`Save failed: ${error.message}`);
    setTimeout(() => setSaveStatus('idle'), 5000);
  };

  const handleVersionRestore = (version: SiteVersion) => {
    setHtmlCode(version.html_code);
    setCssCode(version.css_code || '');
    setSaveStatus('success');
    setSaveMessage(`Restored to version ${version.version_number}`);
    setTimeout(() => setSaveStatus('idle'), 3000);
  };

  const handleVersionPreview = (version: SiteVersion) => {
    // In a real implementation, this would open a preview modal
    console.log('Preview version:', version);
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>WYSIWYG Editor Demo</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground mb-4">
            This demo showcases the WYSIWYG editor functionality. Click on any element in the preview
            to edit its content and styles. Changes are tracked in the version history.
          </p>

          {/* Save Status Alert */}
          {saveStatus !== 'idle' && (
            <Alert className="mb-4" variant={saveStatus === 'success' ? 'default' : 'destructive'}>
              {saveStatus === 'success' ? (
                <CheckCircle2 className="h-4 w-4" />
              ) : (
                <AlertCircle className="h-4 w-4" />
              )}
              <AlertDescription>{saveMessage}</AlertDescription>
            </Alert>
          )}

          <Tabs defaultValue="editor" className="w-full">
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="editor">Editor</TabsTrigger>
              <TabsTrigger value="history">Version History</TabsTrigger>
            </TabsList>

            <TabsContent value="editor" className="space-y-4">
              {/* WYSIWYG Editor Controls */}
              <WYSIWYGEditor
                siteId={siteId}
                iframeRef={iframeRef}
                htmlCode={htmlCode}
                cssCode={cssCode}
                jsCode={jsCode}
                onCodeUpdate={handleCodeUpdate}
                onSaveSuccess={handleSaveSuccess}
                onSaveError={handleSaveError}
              />

              {/* Site Preview */}
              <div className="border rounded-lg overflow-hidden" style={{ height: '600px' }}>
                <SitePreview
                  htmlCode={htmlCode}
                  cssCode={cssCode}
                  jsCode={jsCode}
                  editable={true}
                  viewport="desktop"
                />
              </div>
            </TabsContent>

            <TabsContent value="history">
              <VersionHistory
                versions={versions}
                currentVersionId="v3"
                onVersionRestore={handleVersionRestore}
                onVersionPreview={handleVersionPreview}
              />
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>

      {/* Instructions */}
      <Card>
        <CardHeader>
          <CardTitle>How to Use</CardTitle>
        </CardHeader>
        <CardContent>
          <ol className="list-decimal list-inside space-y-2 text-sm text-muted-foreground">
            <li>Click on any element in the preview to select it</li>
            <li>Use the toolbar to edit text content or modify styles</li>
            <li>Click the edit icon to change text content</li>
            <li>Use the color picker to change text color</li>
            <li>Adjust font size using the dropdown</li>
            <li>Change text alignment with the alignment buttons</li>
            <li>Delete elements using the trash icon</li>
            <li>Use Undo/Redo buttons to navigate edit history</li>
            <li>Click Save to persist changes to the backend</li>
            <li>View version history in the History tab</li>
          </ol>
        </CardContent>
      </Card>
    </div>
  );
};
