import { Moon, Sun, Download, Upload, LogOut } from 'lucide-react';
import { useTheme } from '../theme-provider';
import { useSession } from '../../lib/context/SessionContext';
import { useKeyboardShortcut } from '../../lib/hooks/useKeyboardShortcut';
import KeyboardShortcutsDialog from './KeyboardShortcutsDialog';
import MobileMenu from './MobileMenu';
import { Button } from '../ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '../ui/dropdown-menu';
import { useState } from 'react';

export default function Header() {
  const { theme, setTheme } = useTheme();
  const { session, exportSession, importSession, clearSession } = useSession();
  const [isImporting, setIsImporting] = useState(false);

  const handleExportSession = () => {
    try {
      const data = exportSession();
      const blob = new Blob([data], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `session-${session?.id}-${new Date().toISOString()}.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Failed to export session:', error);
    }
  };

  const handleImportSession = () => {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = 'application/json';
    input.onchange = async (e) => {
      const file = (e.target as HTMLInputElement).files?.[0];
      if (file) {
        try {
          setIsImporting(true);
          const text = await file.text();
          await importSession(text);
        } catch (error) {
          console.error('Failed to import session:', error);
        } finally {
          setIsImporting(false);
        }
      }
    };
    input.click();
  };

  const toggleTheme = () => {
    setTheme(theme === 'dark' ? 'light' : 'dark');
  };

  // Keyboard shortcut for theme toggle (Ctrl+Shift+T)
  useKeyboardShortcut(toggleTheme, {
    key: 't',
    ctrlKey: true,
    shiftKey: true,
  });

  return (
    <header 
      className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60"
      role="banner"
    >
      <div className="flex h-14 sm:h-16 items-center justify-between px-3 sm:px-4 md:px-6">
        <div className="flex items-center gap-2 sm:gap-3">
          {/* Mobile menu button */}
          <MobileMenu />
          
          <h1 className="text-base sm:text-lg md:text-xl font-bold truncate">
            Website Builder
          </h1>
          {session && (
            <span className="hidden sm:inline text-xs text-muted-foreground" aria-label={`Current session ID: ${session.id}`}>
              Session: {session.id.slice(0, 8)}...
            </span>
          )}
        </div>

        <div className="flex items-center gap-1 sm:gap-2" role="toolbar" aria-label="Header controls">
          <div className="hidden sm:block">
            <KeyboardShortcutsDialog />
          </div>
          
          <Button
            variant="ghost"
            size="icon"
            onClick={toggleTheme}
            aria-label={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode (Ctrl+Shift+T)`}
            title={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode (Ctrl+Shift+T)`}
            className="h-9 w-9 sm:h-10 sm:w-10"
          >
            {theme === 'dark' ? (
              <Sun className="h-4 w-4 sm:h-5 sm:w-5" aria-hidden="true" />
            ) : (
              <Moon className="h-4 w-4 sm:h-5 sm:w-5" aria-hidden="true" />
            )}
          </Button>

          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button 
                variant="ghost" 
                size="sm" 
                aria-label="Session menu"
                className="hidden xs:inline-flex h-9 px-2 sm:px-3"
              >
                <span className="hidden sm:inline">Session</span>
                <span className="sm:hidden">•••</span>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-56">
              <DropdownMenuLabel>Session Controls</DropdownMenuLabel>
              <DropdownMenuSeparator />
              <DropdownMenuItem onClick={handleExportSession}>
                <Download className="mr-2 h-4 w-4" aria-hidden="true" />
                Export Session
              </DropdownMenuItem>
              <DropdownMenuItem onClick={handleImportSession} disabled={isImporting}>
                <Upload className="mr-2 h-4 w-4" aria-hidden="true" />
                {isImporting ? 'Importing...' : 'Import Session'}
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem onClick={clearSession} className="text-destructive">
                <LogOut className="mr-2 h-4 w-4" aria-hidden="true" />
                Clear Session
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>
    </header>
  );
}
