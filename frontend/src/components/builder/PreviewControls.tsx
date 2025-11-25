import React from 'react';
import { ZoomIn, ZoomOut, RotateCw, Camera, Maximize2, Minimize2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import { Separator } from '@/components/ui/separator';
import { cn } from '@/lib/utils';

interface PreviewControlsProps {
  zoom: number;
  onZoomChange: (zoom: number) => void;
  onRefresh: () => void;
  onScreenshot: () => void;
  onFullscreenToggle: () => void;
  isFullscreen: boolean;
  className?: string;
}

export const PreviewControls: React.FC<PreviewControlsProps> = ({
  zoom,
  onZoomChange,
  onRefresh,
  onScreenshot,
  onFullscreenToggle,
  isFullscreen,
  className,
}) => {
  const handleZoomIn = () => {
    onZoomChange(zoom + 10);
  };

  const handleZoomOut = () => {
    onZoomChange(zoom - 10);
  };

  const handleZoomReset = () => {
    onZoomChange(100);
  };

  return (
    <TooltipProvider>
      <div className={cn('flex items-center gap-1', className)}>
        {/* Zoom Controls */}
        <Tooltip>
          <TooltipTrigger asChild>
            <Button
              variant="ghost"
              size="icon"
              onClick={handleZoomOut}
              disabled={zoom <= 25}
              aria-label="Zoom out"
            >
              <ZoomOut className="h-4 w-4" />
            </Button>
          </TooltipTrigger>
          <TooltipContent>
            <p>Zoom out</p>
          </TooltipContent>
        </Tooltip>

        <Button
          variant="ghost"
          size="sm"
          onClick={handleZoomReset}
          className="min-w-[60px] font-mono text-xs"
          aria-label={`Current zoom: ${zoom}%`}
        >
          {zoom}%
        </Button>

        <Tooltip>
          <TooltipTrigger asChild>
            <Button
              variant="ghost"
              size="icon"
              onClick={handleZoomIn}
              disabled={zoom >= 200}
              aria-label="Zoom in"
            >
              <ZoomIn className="h-4 w-4" />
            </Button>
          </TooltipTrigger>
          <TooltipContent>
            <p>Zoom in</p>
          </TooltipContent>
        </Tooltip>

        <Separator orientation="vertical" className="h-6 mx-1" />

        {/* Refresh */}
        <Tooltip>
          <TooltipTrigger asChild>
            <Button
              variant="ghost"
              size="icon"
              onClick={onRefresh}
              aria-label="Refresh preview"
            >
              <RotateCw className="h-4 w-4" />
            </Button>
          </TooltipTrigger>
          <TooltipContent>
            <p>Refresh preview</p>
          </TooltipContent>
        </Tooltip>

        {/* Screenshot */}
        <Tooltip>
          <TooltipTrigger asChild>
            <Button
              variant="ghost"
              size="icon"
              onClick={onScreenshot}
              aria-label="Capture screenshot"
            >
              <Camera className="h-4 w-4" />
            </Button>
          </TooltipTrigger>
          <TooltipContent>
            <p>Capture screenshot</p>
          </TooltipContent>
        </Tooltip>

        <Separator orientation="vertical" className="h-6 mx-1" />

        {/* Fullscreen */}
        <Tooltip>
          <TooltipTrigger asChild>
            <Button
              variant="ghost"
              size="icon"
              onClick={onFullscreenToggle}
              aria-label={isFullscreen ? 'Exit fullscreen' : 'Enter fullscreen'}
            >
              {isFullscreen ? (
                <Minimize2 className="h-4 w-4" />
              ) : (
                <Maximize2 className="h-4 w-4" />
              )}
            </Button>
          </TooltipTrigger>
          <TooltipContent>
            <p>{isFullscreen ? 'Exit fullscreen' : 'Enter fullscreen'}</p>
          </TooltipContent>
        </Tooltip>
      </div>
    </TooltipProvider>
  );
};
