import React, { useState } from 'react';
import { CodeEditor, CodeDiffViewer } from '@/components/builder';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import AnimatedPage from '@/components/shared/AnimatedPage';
import { Code2, GitCompare, Save, Eye } from 'lucide-react';
import { toast } from 'sonner';

const sampleHtml = `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Sample Website</title>
  <link rel="stylesheet" href="styles.css">
</head>
<body>
  <header>
    <h1>Welcome to My Website</h1>
    <nav>
      <ul>
        <li><a href="#home">Home</a></li>
        <li><a href="#about">About</a></li>
        <li><a href="#contact">Contact</a></li>
      </ul>
    </nav>
  </header>
  
  <main>
    <section id="home">
      <h2>Home Section</h2>
      <p>This is a sample website built with HTML, CSS, and JavaScript.</p>
    </section>
    
    <section id="about">
      <h2>About Section</h2>
      <p>Learn more about us here.</p>
    </section>
  </main>
  
  <footer>
    <p>&copy; 2024 My Website. All rights reserved.</p>
  </footer>
  
  <script src="script.js"></script>
</body>
</html>`;

const sampleCss = `* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  line-height: 1.6;
  color: #333;
  background-color: #f4f4f4;
}

header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 2rem;
  text-align: center;
}

header h1 {
  margin-bottom: 1rem;
  font-size: 2.5rem;
}

nav ul {
  list-style: none;
  display: flex;
  justify-content: center;
  gap: 2rem;
}

nav a {
  color: white;
  text-decoration: none;
  font-weight: 500;
  transition: opacity 0.3s;
}

nav a:hover {
  opacity: 0.8;
}

main {
  max-width: 1200px;
  margin: 2rem auto;
  padding: 0 2rem;
}

section {
  background: white;
  padding: 2rem;
  margin-bottom: 2rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

section h2 {
  color: #667eea;
  margin-bottom: 1rem;
}

footer {
  background: #333;
  color: white;
  text-align: center;
  padding: 1rem;
  margin-top: 2rem;
}`;

const sampleJs = `// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
  console.log('Website loaded successfully!');
  
  // Smooth scrolling for navigation links
  const navLinks = document.querySelectorAll('nav a');
  
  navLinks.forEach(link => {
    link.addEventListener('click', function(e) {
      e.preventDefault();
      const targetId = this.getAttribute('href');
      const targetSection = document.querySelector(targetId);
      
      if (targetSection) {
        targetSection.scrollIntoView({
          behavior: 'smooth',
          block: 'start'
        });
      }
    });
  });
  
  // Add animation on scroll
  const sections = document.querySelectorAll('section');
  
  const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -100px 0px'
  };
  
  const observer = new IntersectionObserver(function(entries) {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.style.opacity = '1';
        entry.target.style.transform = 'translateY(0)';
      }
    });
  }, observerOptions);
  
  sections.forEach(section => {
    section.style.opacity = '0';
    section.style.transform = 'translateY(20px)';
    section.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
    observer.observe(section);
  });
});

// Example function
function greetUser(name) {
  return \`Hello, \${name}! Welcome to our website.\`;
}

console.log(greetUser('Visitor'));`;

const modifiedHtml = sampleHtml.replace(
  '<h1>Welcome to My Website</h1>',
  '<h1>Welcome to My Awesome Website</h1>'
);

const modifiedCss = sampleCss.replace(
  'background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);',
  'background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);'
);

const modifiedJs = sampleJs.replace(
  "console.log('Website loaded successfully!');",
  "console.log('Website loaded successfully!');\n  console.log('Version 2.0');"
);

export const CodeEditorTestPage: React.FC = () => {
  const [htmlCode, setHtmlCode] = useState(sampleHtml);
  const [cssCode, setCssCode] = useState(sampleCss);
  const [jsCode, setJsCode] = useState(sampleJs);
  const [showPreview, setShowPreview] = useState(false);

  const handleSave = () => {
    toast.success('Code saved successfully!', {
      description: 'Your changes have been saved.',
    });
  };

  const handlePreview = () => {
    setShowPreview(!showPreview);
  };

  const generatePreviewHtml = () => {
    return `
      <!DOCTYPE html>
      <html>
        <head>
          <style>${cssCode}</style>
        </head>
        <body>
          ${htmlCode.replace(/<script.*?<\/script>/gs, '')}
          <script>${jsCode}</script>
        </body>
      </html>
    `;
  };

  return (
    <AnimatedPage>
      <div className="container mx-auto py-8 px-4">
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-2">Code Editor Test Page</h1>
          <p className="text-muted-foreground">
            Test the Monaco Editor integration with syntax highlighting, code completion, and validation
          </p>
        </div>

        <div className="grid gap-6">
          {/* Code Editor Section */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="flex items-center gap-2">
                    <Code2 className="h-5 w-5" />
                    Code Editor
                  </CardTitle>
                  <CardDescription>
                    Edit HTML, CSS, and JavaScript with full IDE features
                  </CardDescription>
                </div>
                <div className="flex gap-2">
                  <Button onClick={handlePreview} variant="outline" size="sm">
                    <Eye className="h-4 w-4 mr-2" />
                    {showPreview ? 'Hide' : 'Show'} Preview
                  </Button>
                  <Button onClick={handleSave} size="sm">
                    <Save className="h-4 w-4 mr-2" />
                    Save Changes
                  </Button>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex gap-2 flex-wrap">
                  <Badge variant="secondary">Syntax Highlighting</Badge>
                  <Badge variant="secondary">Code Completion</Badge>
                  <Badge variant="secondary">Error Detection</Badge>
                  <Badge variant="secondary">Auto-formatting</Badge>
                  <Badge variant="secondary">Keyboard Shortcuts</Badge>
                </div>
                
                <CodeEditor
                  htmlCode={htmlCode}
                  cssCode={cssCode}
                  jsCode={jsCode}
                  onHtmlChange={setHtmlCode}
                  onCssChange={setCssCode}
                  onJsChange={setJsCode}
                  height="500px"
                  showToolbar={true}
                  enableFormatting={true}
                  enableValidation={true}
                />

                {showPreview && (
                  <div className="mt-4">
                    <h3 className="text-lg font-semibold mb-2">Live Preview</h3>
                    <div className="border rounded-lg overflow-hidden">
                      <iframe
                        srcDoc={generatePreviewHtml()}
                        className="w-full h-[400px] bg-white"
                        title="Code Preview"
                        sandbox="allow-scripts"
                      />
                    </div>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Code Diff Viewer Section */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <GitCompare className="h-5 w-5" />
                Code Diff Viewer
              </CardTitle>
              <CardDescription>
                Compare code changes between versions side-by-side
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex gap-2 flex-wrap">
                  <Badge variant="secondary">Side-by-Side Comparison</Badge>
                  <Badge variant="secondary">Inline Diff</Badge>
                  <Badge variant="secondary">Change Statistics</Badge>
                  <Badge variant="secondary">Syntax Highlighting</Badge>
                </div>
                
                <CodeDiffViewer
                  originalHtml={sampleHtml}
                  modifiedHtml={modifiedHtml}
                  originalCss={sampleCss}
                  modifiedCss={modifiedCss}
                  originalJs={sampleJs}
                  modifiedJs={modifiedJs}
                  height="500px"
                />
              </div>
            </CardContent>
          </Card>

          {/* Features Documentation */}
          <Card>
            <CardHeader>
              <CardTitle>Editor Features</CardTitle>
              <CardDescription>
                Comprehensive list of available features and keyboard shortcuts
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Tabs defaultValue="features">
                <TabsList>
                  <TabsTrigger value="features">Features</TabsTrigger>
                  <TabsTrigger value="shortcuts">Keyboard Shortcuts</TabsTrigger>
                  <TabsTrigger value="languages">Language Support</TabsTrigger>
                </TabsList>

                <TabsContent value="features" className="space-y-4">
                  <div className="grid md:grid-cols-2 gap-4">
                    <div>
                      <h4 className="font-semibold mb-2">Editing Features</h4>
                      <ul className="space-y-1 text-sm text-muted-foreground">
                        <li>• Syntax highlighting for HTML, CSS, and JavaScript</li>
                        <li>• IntelliSense and code completion</li>
                        <li>• Real-time error detection and validation</li>
                        <li>• Auto-formatting with Prettier integration</li>
                        <li>• Bracket matching and auto-closing</li>
                        <li>• Code folding and minimap</li>
                      </ul>
                    </div>
                    <div>
                      <h4 className="font-semibold mb-2">Additional Features</h4>
                      <ul className="space-y-1 text-sm text-muted-foreground">
                        <li>• Multi-cursor editing</li>
                        <li>• Find and replace with regex support</li>
                        <li>• Line numbers and gutter indicators</li>
                        <li>• Word wrap and scroll beyond last line</li>
                        <li>• Mouse wheel zoom</li>
                        <li>• Context menu with common actions</li>
                      </ul>
                    </div>
                  </div>
                </TabsContent>

                <TabsContent value="shortcuts" className="space-y-4">
                  <div className="grid md:grid-cols-2 gap-4">
                    <div>
                      <h4 className="font-semibold mb-2">Common Shortcuts</h4>
                      <ul className="space-y-1 text-sm">
                        <li className="flex justify-between">
                          <span>Save</span>
                          <code className="bg-muted px-2 py-1 rounded">Ctrl/Cmd + S</code>
                        </li>
                        <li className="flex justify-between">
                          <span>Format Code</span>
                          <code className="bg-muted px-2 py-1 rounded">Ctrl/Cmd + Shift + F</code>
                        </li>
                        <li className="flex justify-between">
                          <span>Find</span>
                          <code className="bg-muted px-2 py-1 rounded">Ctrl/Cmd + F</code>
                        </li>
                        <li className="flex justify-between">
                          <span>Replace</span>
                          <code className="bg-muted px-2 py-1 rounded">Ctrl/Cmd + H</code>
                        </li>
                      </ul>
                    </div>
                    <div>
                      <h4 className="font-semibold mb-2">Advanced Shortcuts</h4>
                      <ul className="space-y-1 text-sm">
                        <li className="flex justify-between">
                          <span>Multi-cursor</span>
                          <code className="bg-muted px-2 py-1 rounded">Alt + Click</code>
                        </li>
                        <li className="flex justify-between">
                          <span>Comment Line</span>
                          <code className="bg-muted px-2 py-1 rounded">Ctrl/Cmd + /</code>
                        </li>
                        <li className="flex justify-between">
                          <span>Duplicate Line</span>
                          <code className="bg-muted px-2 py-1 rounded">Shift + Alt + Down</code>
                        </li>
                        <li className="flex justify-between">
                          <span>Go to Line</span>
                          <code className="bg-muted px-2 py-1 rounded">Ctrl/Cmd + G</code>
                        </li>
                      </ul>
                    </div>
                  </div>
                </TabsContent>

                <TabsContent value="languages" className="space-y-4">
                  <div className="grid md:grid-cols-3 gap-4">
                    <div>
                      <h4 className="font-semibold mb-2">HTML</h4>
                      <ul className="space-y-1 text-sm text-muted-foreground">
                        <li>• Tag auto-completion</li>
                        <li>• Attribute suggestions</li>
                        <li>• HTML5 validation</li>
                        <li>• Emmet abbreviations</li>
                      </ul>
                    </div>
                    <div>
                      <h4 className="font-semibold mb-2">CSS</h4>
                      <ul className="space-y-1 text-sm text-muted-foreground">
                        <li>• Property suggestions</li>
                        <li>• Color picker</li>
                        <li>• CSS linting</li>
                        <li>• Vendor prefix warnings</li>
                      </ul>
                    </div>
                    <div>
                      <h4 className="font-semibold mb-2">JavaScript</h4>
                      <ul className="space-y-1 text-sm text-muted-foreground">
                        <li>• ES2020+ support</li>
                        <li>• Syntax validation</li>
                        <li>• IntelliSense</li>
                        <li>• JSDoc support</li>
                      </ul>
                    </div>
                  </div>
                </TabsContent>
              </Tabs>
            </CardContent>
          </Card>
        </div>
      </div>
    </AnimatedPage>
  );
};
