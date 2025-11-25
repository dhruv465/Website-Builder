import { useState } from 'react';
import { Search, X } from 'lucide-react';
import * as LucideIcons from 'lucide-react';
import { Input } from '@/components/ui/input';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';

interface IconPickerProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSelectIcon: (iconName: string) => void;
}

export function IconPicker({ open, onOpenChange, onSelectIcon }: IconPickerProps) {
  const [search, setSearch] = useState('');

  // Get all Lucide icons
  const allIcons = Object.keys(LucideIcons).filter(
    (key) => key !== 'createLucideIcon' && key !== 'default'
  );

  // Filter icons based on search
  const filteredIcons = allIcons.filter((iconName) =>
    iconName.toLowerCase().includes(search.toLowerCase())
  );

  const handleSelectIcon = (iconName: string) => {
    onSelectIcon(iconName);
    onOpenChange(false);
    setSearch('');
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[80vh]">
        <DialogHeader>
          <DialogTitle>Select an Icon</DialogTitle>
        </DialogHeader>

        <div className="space-y-4">
          {/* Search */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search icons..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="pl-10"
            />
            {search && (
              <Button
                variant="ghost"
                size="sm"
                className="absolute right-1 top-1/2 transform -translate-y-1/2 h-7 w-7 p-0"
                onClick={() => setSearch('')}
              >
                <X className="h-4 w-4" />
              </Button>
            )}
          </div>

          {/* Icon Grid */}
          <ScrollArea className="h-[400px]">
            <div className="grid grid-cols-8 gap-2 p-2">
              {filteredIcons.map((iconName) => {
                const IconComponent = (LucideIcons as any)[iconName];
                
                return (
                  <button
                    key={iconName}
                    onClick={() => handleSelectIcon(iconName)}
                    className="flex flex-col items-center justify-center p-3 rounded-lg hover:bg-accent transition-colors group"
                    title={iconName}
                  >
                    <IconComponent className="h-6 w-6 text-foreground group-hover:text-primary transition-colors" />
                    <span className="text-[10px] text-muted-foreground mt-1 truncate w-full text-center">
                      {iconName}
                    </span>
                  </button>
                );
              })}
            </div>

            {filteredIcons.length === 0 && (
              <div className="text-center py-12 text-muted-foreground">
                No icons found matching "{search}"
              </div>
            )}
          </ScrollArea>

          <div className="text-xs text-muted-foreground text-center">
            {filteredIcons.length} icons available
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
