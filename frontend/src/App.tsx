import { RouterProvider } from 'react-router-dom';
import { SessionProvider } from './lib/context/SessionContext';
import { WorkflowProvider } from './lib/context/WorkflowContext';
import { ThemeProvider } from './components/theme-provider';
import { ErrorBoundary } from './components/error-boundary';
import { ToastProvider } from './components/shared';
import { router } from './router';

function App() {
  return (
    <ErrorBoundary showDetails={import.meta.env.DEV}>
      <ThemeProvider defaultTheme="dark" storageKey="website-builder-theme">
        <SessionProvider>
          <WorkflowProvider>
            <RouterProvider router={router} />
            <ToastProvider />
          </WorkflowProvider>
        </SessionProvider>
      </ThemeProvider>
    </ErrorBoundary>
  );
}

export default App;
