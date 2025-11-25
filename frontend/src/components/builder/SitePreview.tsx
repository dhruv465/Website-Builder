import React, { useState, useRef, useEffect, useCallback } from 'react';
import { cn } from '@/lib/utils';
import { 
  Monitor, 
  Laptop, 
  Tablet, 
  Smartphone, 
  RotateCcw, 
  Maximize, 
  Minimize,
  ZoomIn,
  ZoomOut
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Separator } from '@/components/ui/separator';

export type ViewportSize = 'mobile' | 'tablet' | 'laptop' | 'desktop';

export interface SitePreviewProps {
  htmlCode: string;
  cssCode?: string;
  jsCode?: string;
  onElementSelect?: (element: HTMLElement) => void;
  viewport?: ViewportSize;
  editable?: boolean;
  className?: string;
}

export const SitePreview: React.FC<SitePreviewProps> = ({
  htmlCode,
  cssCode = '',
  jsCode = '',
  onElementSelect,
  viewport: initialViewport = 'desktop',
  editable = false,
  className,
}) => {
  const iframeRef = useRef<HTMLIFrameElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [viewport, setViewport] = useState<ViewportSize>(initialViewport);
  const [zoom, setZoom] = useState(100);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [iframeKey, setIframeKey] = useState(0);

  // Viewport dimensions based on spec
  const viewportDimensions = {
    mobile: { width: 375, height: 667, label: 'Mobile' },
    tablet: { width: 768, height: 1024, label: 'Tablet' },
    laptop: { width: 1280, height: 800, label: 'Laptop' },
    desktop: { width: 1440, height: 900, label: 'Desktop' },
  };

  // Inject code into iframe
  const injectCode = useCallback(() => {
    const iframe = iframeRef.current;
    if (!iframe || !iframe.contentWindow) return;

    const doc = iframe.contentDocument || iframe.contentWindow.document;
    
    const fullHtml = `
      <!DOCTYPE html>
      <html lang="en">
        <head>
          <meta charset="UTF-8">
          <meta name="viewport" content="width=device-width, initial-scale=1.0">
          <title>Preview</title>
          <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { font-family: system-ui, -apple-system, sans-serif; }
            ${cssCode}
          </style>
        </head>
        <body>
          ${htmlCode}
          <script>
            document.addEventListener('click', (e) => {
              const target = e.target.closest('a');
              if (target && target.href) e.preventDefault();
            });
            ${jsCode}
          </script>
        </body>
      </html>
    `;

    doc.open();
    doc.write(fullHtml);
    doc.close();
  }, [htmlCode, cssCode, jsCode]);

  useEffect(() => {
    injectCode();
  }, [injectCode, iframeKey]);

  const handleRefresh = () => setIframeKey(prev => prev + 1);

  const toggleFullscreen = () => {
    if (!document.fullscreenElement) {
      containerRef.current?.requestFullscreen();
      setIsFullscreen(true);
    } else {
      document.exitFullscreen();
      setIsFullscreen(false);
    }
  };

  const currentDimensions = viewportDimensions[viewport];

  return (
    <div 
      ref={containerRef}
      className={cn(
        "flex flex-col h-full bg-muted/30",
        isFullscreen && "fixed inset-0 z-50 bg-background",
        className
      )}
    >
      {/* Top Toolbar */}
      <div className="h-14 bg-background/80 backdrop-blur-sm border-b border-border flex items-center justify-between px-4 shrink-0">
        {/* Device Selector */}
        <div className="flex items-center gap-1 bg-muted/50 p-1 rounded-lg border border-border/50">
          <Button
            variant={viewport === 'mobile' ? 'secondary' : 'ghost'}
            size="icon"
            className="h-8 w-8 rounded-md transition-all"
            onClick={() => setViewport('mobile')}
            title="Mobile (375px)"
          >
            <Smartphone className="h-4 w-4" />
          </Button>
          <Button
            variant={viewport === 'tablet' ? 'secondary' : 'ghost'}
            size="icon"
            className="h-8 w-8 rounded-md transition-all"
            onClick={() => setViewport('tablet')}
            title="Tablet (768px)"
          >
            <Tablet className="h-4 w-4" />
          </Button>
          <Button
            variant={viewport === 'laptop' ? 'secondary' : 'ghost'}
            size="icon"
            className="h-8 w-8 rounded-md transition-all"
            onClick={() => setViewport('laptop')}
            title="Laptop (1280px)"
          >
            <Laptop className="h-4 w-4" />
          </Button>
          <Button
            variant={viewport === 'desktop' ? 'secondary' : 'ghost'}
            size="icon"
            className="h-8 w-8 rounded-md transition-all"
            onClick={() => setViewport('desktop')}
            title="Desktop (1440px)"
          >
            <Monitor className="h-4 w-4" />
          </Button>
        </div>

        {/* Zoom Control */}
        <div className="flex items-center gap-2 bg-muted/50 p-1 rounded-lg border border-border/50">
          <Button
            variant="ghost"
            size="icon"
            className="h-8 w-8"
            onClick={() => setZoom(z => Math.max(25, z - 25))}
            disabled={zoom <= 25}
          >
            <ZoomOut className="h-4 w-4" />
          </Button>
          <div className="h-4 w-[1px] bg-border" />
          <span className="text-xs font-medium w-10 text-center text-muted-foreground">{zoom}%</span>
          <div className="h-4 w-[1px] bg-border" />
          <Button
            variant="ghost"
            size="icon"
            className="h-8 w-8"
            onClick={() => setZoom(z => Math.min(200, z + 25))}
            disabled={zoom >= 200}
          >
            <ZoomIn className="h-4 w-4" />
          </Button>
        </div>

        {/* Actions */}
        <div className="flex items-center gap-2">
          <Button variant="ghost" size="icon" className="h-8 w-8 text-muted-foreground hover:text-foreground" onClick={handleRefresh} title="Refresh">
            <RotateCcw className="h-4 w-4" />
          </Button>
          <Separator orientation="vertical" className="h-6" />
          <Button variant="ghost" size="icon" className="h-8 w-8 text-muted-foreground hover:text-foreground" onClick={toggleFullscreen} title="Fullscreen">
            {isFullscreen ? <Minimize className="h-4 w-4" /> : <Maximize className="h-4 w-4" />}
          </Button>
        </div>
      </div>

      {/* Canvas Area */}
      <div className="flex-1 overflow-auto p-8 flex items-start justify-center bg-secondary/20">
        <div 
          className="bg-background shadow-xl transition-all duration-300 origin-top ring-1 ring-border/50"
          style={{
            width: currentDimensions.width,
            height: currentDimensions.height,
            transform: `scale(${zoom / 100})`,
            marginBottom: `${(currentDimensions.height * (zoom / 100)) - currentDimensions.height}px`,
            marginRight: `${(currentDimensions.width * (zoom / 100)) - currentDimensions.width}px`
          }}
        >
          <iframe
            key={iframeKey}
            ref={iframeRef}
            title="Site Preview"
            className="w-full h-full border-0 bg-white"
            sandbox="allow-scripts allow-same-origin"
          />
        </div>
      </div>
    </div>
  );
};
