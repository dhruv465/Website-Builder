import { Outlet, useLocation } from 'react-router-dom';
import { AnimatePresence } from 'framer-motion';
import { ErrorBoundary } from '../components/error-boundary';

export default function RootLayout() {
  const location = useLocation();

  return (
    <ErrorBoundary>
      <div className="min-h-screen bg-background text-foreground">
        <AnimatePresence mode="wait" initial={false}>
          <Outlet key={location.pathname} />
        </AnimatePresence>
      </div>
    </ErrorBoundary>
  );
}
