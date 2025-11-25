import { ReactNode } from 'react';
import { TopNavigation } from '@/components/layout/TopNavigation';

interface StudioLayoutProps {
  children: ReactNode;
  sidebar?: ReactNode;
  rightPanel?: ReactNode;
}

export default function StudioLayout({ children, sidebar, rightPanel }: StudioLayoutProps) {
  return (
    <div className="flex flex-col h-screen w-full bg-background text-foreground overflow-hidden font-sans selection:bg-primary/20">
      {/* Top Navigation */}
      <TopNavigation />

      {/* Main Workspace Area */}
      <div className="flex flex-1 overflow-hidden">
        {/* Left Sidebar - Navigation & Chat */}
        {sidebar && (
          <aside className="w-[280px] hidden md:flex flex-col border-r border-border bg-card/50 z-20">
            {sidebar}
          </aside>
        )}

        {/* Center Canvas Area */}
        <main className="flex-1 flex flex-col min-w-0 bg-secondary/30 relative overflow-hidden">
          {children}
        </main>

        {/* Right Panel - Properties & Assistant */}
        {rightPanel && (
          <div className="hidden xl:block z-20 bg-card/50">
            {rightPanel}
          </div>
        )}
      </div>
    </div>
  );
}
