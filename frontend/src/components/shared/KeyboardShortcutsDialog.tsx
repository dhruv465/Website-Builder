import { useState } from 'react';
import { Keyboard } from 'lucide-react';
import { useKeyboardShortcut } from '@/lib/hooks/useKeyboardShortcut';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '../ui/dialog';
import { Button } from '../ui/button';

interface Shortcut {
  keys: string;
  description: string;
  category: string;
}

const shortcuts: Shortcut[] = [
  {
    keys: 'Ctrl + Shift + T',
    description: 'Toggle theme (light/dark)',
    category: 'General',
  },
  {
    keys: 'Ctrl + S',
    description: 'Save current work',
    category: 'General',
  },
  {
    keys: 'Esc',
    description: 'Close dialog or modal',
    category: 'General',
  },
  {
    keys: 'Tab',
    description: 'Navigate to next element',
    category: 'Navigation',
  },
  {
    keys: 'Shift + Tab',
    description: 'Navigate to previous element',
    category: 'Navigation',
  },
  {
    keys: '?',
    description: 'Show keyboard shortcuts',
    category: 'Help',
  },
];

export default function KeyboardShortcutsDialog() {
  const [open, setOpen] = useState(false);

  // Show shortcuts dialog with ? key
  useKeyboardShortcut(
    () => setOpen(true),
    {
      key: '?',
      shiftKey: true,
    }
  );

  const categories = Array.from(new Set(shortcuts.map((s) => s.category)));

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button
          variant="ghost"
          size="icon"
          aria-label="Show keyboard shortcuts"
          title="Show keyboard shortcuts (?)"
        >
          <Keyboard className="h-5 w-5" aria-hidden="true" />
        </Button>
      </DialogTrigger>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>Keyboard Shortcuts</DialogTitle>
          <DialogDescription>
            Use these keyboard shortcuts to navigate and interact with the application more efficiently.
          </DialogDescription>
        </DialogHeader>
        
        <div className="space-y-6">
          {categories.map((category) => (
            <div key={category}>
              <h3 className="mb-3 text-sm font-semibold text-muted-foreground">
                {category}
              </h3>
              <div className="space-y-2">
                {shortcuts
                  .filter((s) => s.category === category)
                  .map((shortcut, index) => (
                    <div
                      key={index}
                      className="flex items-center justify-between rounded-lg border p-3"
                    >
                      <span className="text-sm">{shortcut.description}</span>
                      <kbd className="rounded bg-muted px-2 py-1 text-xs font-semibold">
                        {shortcut.keys}
                      </kbd>
                    </div>
                  ))}
              </div>
            </div>
          ))}
        </div>
      </DialogContent>
    </Dialog>
  );
}
