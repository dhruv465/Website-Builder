import React from 'react';
import { X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

interface ElementHighlightProps {
  rect: DOMRect;
  zoom: number;
  onClose: () => void;
  className?: string;
}

export const ElementHighlight: React.FC<ElementHighlightProps> = ({
  rect,
  zoom,
  onClose,
  className,
}) => {
  // Adjust position and size based on zoom
  const scale = zoom / 100;
  const adjustedRect = {
    top: rect.top * scale,
    left: rect.left * scale,
    width: rect.width * scale,
    height: rect.height * scale,
  };

  return (
    <>
      {/* Highlight Border */}
      <div
        className={cn(
          'absolute pointer-events-none border-2 border-primary bg-primary/10 transition-all duration-200',
          className
        )}
        style={{
          top: `${adjustedRect.top}px`,
          left: `${adjustedRect.left}px`,
          width: `${adjustedRect.width}px`,
          height: `${adjustedRect.height}px`,
        }}
      >
        {/* Element Info Badge */}
        <div className="absolute -top-6 left-0 flex items-center gap-1 bg-primary text-primary-foreground text-xs px-2 py-1 rounded shadow-md pointer-events-auto">
          <span className="font-mono">
            {Math.round(rect.width)} × {Math.round(rect.height)}
          </span>
          <Button
            variant="ghost"
            size="icon"
            className="h-4 w-4 p-0 hover:bg-primary-foreground/20"
            onClick={onClose}
            aria-label="Clear selection"
          >
            <X className="h-3 w-3" />
          </Button>
        </div>
      </div>

      {/* Corner Handles */}
      {['top-left', 'top-right', 'bottom-left', 'bottom-right'].map((corner) => {
        const positions = {
          'top-left': { top: -2, left: -2 },
          'top-right': { top: -2, right: -2 },
          'bottom-left': { bottom: -2, left: -2 },
          'bottom-right': { bottom: -2, right: -2 },
        };

        return (
          <div
            key={corner}
            className="absolute w-2 h-2 bg-primary border border-background rounded-full pointer-events-none"
            style={{
              top: adjustedRect.top,
              left: adjustedRect.left,
              width: `${adjustedRect.width}px`,
              height: `${adjustedRect.height}px`,
              ...positions[corner as keyof typeof positions],
            }}
          />
        );
      })}
    </>
  );
};
