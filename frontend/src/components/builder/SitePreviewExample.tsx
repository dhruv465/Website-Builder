import React, { useState } from 'react';
import { SitePreview } from './SitePreview';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { Code } from 'lucide-react';

// Example HTML/CSS/JS for demonstration
const exampleHTML = `
<div class="hero">
  <h1>Welcome to My Website</h1>
  <p>This is a beautiful landing page built with modern web technologies.</p>
  <button class="cta-button">Get Started</button>
</div>

<section class="features">
  <div class="feature-card">
    <h3>Fast</h3>
    <p>Lightning-fast performance</p>
  </div>
  <div class="feature-card">
    <h3>Secure</h3>
    <p>Enterprise-grade security</p>
  </div>
  <div class="feature-card">
    <h3>Scalable</h3>
    <p>Grows with your business</p>
  </div>
</section>
`;

const exampleCSS = `
.hero {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 80px 20px;
  text-align: center;
  min-height: 400px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

.hero h1 {
  font-size: 3rem;
  margin-bottom: 1rem;
  font-weight: bold;
}

.hero p {
  font-size: 1.25rem;
  margin-bottom: 2rem;
  opacity: 0.9;
}

.cta-button {
  background: white;
  color: #667eea;
  padding: 12px 32px;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.cta-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.2);
}

.features {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 2rem;
  padding: 60px 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.feature-card {
  background: #f8f9fa;
  padding: 2rem;
  border-radius: 12px;
  text-align: center;
  transition: transform 0.2s, box-shadow 0.2s;
}

.feature-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
}

.feature-card h3 {
  font-size: 1.5rem;
  margin-bottom: 0.5rem;
  color: #667eea;
}

.feature-card p {
  color: #6c757d;
}
`;

const exampleJS = `
console.log('Site preview loaded successfully!');

// Add click animation to CTA button
document.querySelector('.cta-button')?.addEventListener('click', function() {
  alert('Button clicked! In a real site, this would navigate somewhere.');
});
`;

export const SitePreviewExample: React.FC = () => {
  const [selectedElement, setSelectedElement] = useState<HTMLElement | null>(null);
  const [showCode, setShowCode] = useState(false);

  const handleElementSelect = (element: HTMLElement) => {
    setSelectedElement(element);
    console.log('Selected element:', {
      tagName: element.tagName,
      className: element.className,
      textContent: element.textContent?.substring(0, 50),
    });
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Site Preview Component</CardTitle>
              <CardDescription>
                Interactive preview with viewport controls, zoom, and element selection
              </CardDescription>
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowCode(!showCode)}
            >
              <Code className="h-4 w-4 mr-2" />
              {showCode ? 'Hide' : 'Show'} Code
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {showCode && (
            <Tabs defaultValue="html" className="mb-4">
              <TabsList>
                <TabsTrigger value="html">HTML</TabsTrigger>
                <TabsTrigger value="css">CSS</TabsTrigger>
                <TabsTrigger value="js">JavaScript</TabsTrigger>
              </TabsList>
              <TabsContent value="html">
                <pre className="bg-muted p-4 rounded-md overflow-auto max-h-[300px] text-xs">
                  <code>{exampleHTML}</code>
                </pre>
              </TabsContent>
              <TabsContent value="css">
                <pre className="bg-muted p-4 rounded-md overflow-auto max-h-[300px] text-xs">
                  <code>{exampleCSS}</code>
                </pre>
              </TabsContent>
              <TabsContent value="js">
                <pre className="bg-muted p-4 rounded-md overflow-auto max-h-[300px] text-xs">
                  <code>{exampleJS}</code>
                </pre>
              </TabsContent>
            </Tabs>
          )}

          <div className="h-[600px] border rounded-lg overflow-hidden">
            <SitePreview
              htmlCode={exampleHTML}
              cssCode={exampleCSS}
              jsCode={exampleJS}
              onElementSelect={handleElementSelect}
              editable={true}
            />
          </div>

          {selectedElement && (
            <div className="mt-4 p-4 bg-muted rounded-md">
              <h4 className="font-semibold mb-2">Selected Element:</h4>
              <div className="text-sm space-y-1">
                <p>
                  <span className="font-medium">Tag:</span> {selectedElement.tagName}
                </p>
                {selectedElement.className && (
                  <p>
                    <span className="font-medium">Class:</span> {selectedElement.className}
                  </p>
                )}
                {selectedElement.textContent && (
                  <p>
                    <span className="font-medium">Text:</span>{' '}
                    {selectedElement.textContent.substring(0, 100)}
                    {selectedElement.textContent.length > 100 ? '...' : ''}
                  </p>
                )}
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};
