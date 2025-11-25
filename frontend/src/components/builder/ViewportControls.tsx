import React from 'react';
import { Monitor, Tablet, Smartphone } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import { cn } from '@/lib/utils';
import { ViewportSize } from './SitePreview';

interface ViewportControlsProps {
  viewport: ViewportSize;
  onViewportChange: (viewport: ViewportSize) => void;
  className?: string;
}

export const ViewportControls: React.FC<ViewportControlsProps> = ({
  viewport,
  onViewportChange,
  className,
}) => {
  const viewports: Array<{ value: ViewportSize; icon: React.ReactNode; label: string }> = [
    { value: 'mobile', icon: <Smartphone className="h-4 w-4" />, label: 'Mobile (375px)' },
    { value: 'tablet', icon: <Tablet className="h-4 w-4" />, label: 'Tablet (768px)' },
    { value: 'desktop', icon: <Monitor className="h-4 w-4" />, label: 'Desktop (1440px)' },
  ];

  return (
    <TooltipProvider>
      <div className={cn('flex items-center gap-1', className)}>
        {viewports.map(({ value, icon, label }) => (
          <Tooltip key={value}>
            <TooltipTrigger asChild>
              <Button
                variant={viewport === value ? 'default' : 'ghost'}
                size="icon"
                onClick={() => onViewportChange(value)}
                aria-label={label}
                aria-pressed={viewport === value}
              >
                {icon}
              </Button>
            </TooltipTrigger>
            <TooltipContent>
              <p>{label}</p>
            </TooltipContent>
          </Tooltip>
        ))}
      </div>
    </TooltipProvider>
  );
};
