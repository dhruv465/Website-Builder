import React from 'react';
import { ChevronRight, Eye, Share2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Separator } from '@/components/ui/separator';

interface TopNavigationProps {
  title?: string;
  onPreview?: () => void;
  onPublish?: () => void;
}

export function TopNavigation({ 
  title = "Untitled Project", 
  onPreview, 
  onPublish 
}: TopNavigationProps) {
  return (
    <header className="h-16 bg-background/80 backdrop-blur-sm border-b border-border px-6 flex items-center justify-between sticky top-0 z-header">
      {/* Left Section: Breadcrumbs */}
      <div className="flex items-center gap-2">
        <div className="flex items-center text-sm text-muted-foreground">
          <Button variant="ghost" size="sm" className="h-8 px-2 text-muted-foreground hover:text-foreground">
            Dashboard
          </Button>
          <ChevronRight className="h-4 w-4 text-muted-foreground/50" />
          <Button variant="ghost" size="sm" className="h-8 px-2 font-medium text-foreground">
            {title}
          </Button>
        </div>
      </div>

      {/* Center Section: Page Title */}
      <div className="absolute left-1/2 transform -translate-x-1/2 hidden md:block">
        <h1 className="text-sm font-semibold text-foreground/80 tracking-tight">
          Website Builder
        </h1>
      </div>

      {/* Right Section: Actions */}
      <div className="flex items-center gap-3">
        <Button 
          variant="outline" 
          size="sm" 
          className="h-9 gap-2"
          onClick={onPreview}
        >
          <Eye className="h-4 w-4" />
          Preview
        </Button>
        
        <Button 
          size="sm" 
          className="h-9 gap-2 bg-primary text-primary-foreground hover:bg-primary-hover shadow-sm"
          onClick={onPublish}
        >
          <Share2 className="h-4 w-4" />
          Publish
        </Button>

        <Separator orientation="vertical" className="h-6 mx-1" />

        <Avatar className="h-8 w-8 cursor-pointer ring-2 ring-transparent hover:ring-primary/20 transition-all">
          <AvatarImage src="https://github.com/shadcn.png" />
          <AvatarFallback>CN</AvatarFallback>
        </Avatar>
      </div>
    </header>
  );
}
