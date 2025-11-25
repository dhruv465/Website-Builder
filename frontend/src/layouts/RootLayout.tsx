import { Outlet, useLocation } from 'react-router-dom';
import { AnimatePresence } from 'framer-motion';
import { ErrorBoundary } from '../components/error-boundary';

export default function RootLayout() {
  const location = useLocation();

  return (
    <ErrorBoundary>
      <div className="min-h-screen bg-background text-foreground">
        <a 
          href="#main-content" 
          className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 z-50 px-4 py-2 bg-primary text-primary-foreground rounded-md shadow-lg"
        >
          Skip to content
        </a>
        <AnimatePresence mode="wait" initial={false}>
          <main id="main-content" className="min-h-screen">
            <Outlet key={location.pathname} />
          </main>
        </AnimatePresence>
      </div>
    </ErrorBoundary>
  );
}
