import { Component, ErrorInfo, ReactNode } from 'react';
import { useNavigate } from 'react-router-dom';
import { AlertTriangle, Home, ArrowLeft, RefreshCw } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { logError, createError } from '@/lib/utils/errors';
import { ErrorType } from '@/lib/types';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
  routeName?: string;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

class RouteErrorBoundaryClass extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
  };

  public static getDerivedStateFromError(error: Error): State {
    return {
      hasError: true,
      error,
    };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    const appError = createError(
      ErrorType.UNKNOWN_ERROR,
      error.message,
      { errorInfo, route: this.props.routeName }
    );
    
    logError(appError, `Route: ${this.props.routeName || 'Unknown'}`);
  }

  private handleReset = () => {
    this.setState({
      hasError: false,
      error: null,
    });
  };

  public render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return <RouteErrorFallback error={this.state.error} onReset={this.handleReset} />;
    }

    return this.props.children;
  }
}

// Fallback component with navigation
interface RouteErrorFallbackProps {
  error: Error | null;
  onReset: () => void;
}

function RouteErrorFallback({ error, onReset }: RouteErrorFallbackProps) {
  const navigate = useNavigate();

  const handleGoBack = () => {
    onReset();
    navigate(-1);
  };

  const handleGoHome = () => {
    onReset();
    navigate('/');
  };

  return (
    <div className="flex min-h-[60vh] items-center justify-center p-4">
      <Card className="w-full max-w-lg">
        <CardHeader>
          <div className="flex items-center gap-2">
            <AlertTriangle className="h-6 w-6 text-destructive" />
            <CardTitle>Something went wrong</CardTitle>
          </div>
          <CardDescription>
            This page encountered an error. You can try going back or returning to the home page.
          </CardDescription>
        </CardHeader>
        {error && (
          <CardContent>
            <div className="rounded-md bg-muted p-3">
              <p className="text-sm font-mono text-muted-foreground">{error.message}</p>
            </div>
          </CardContent>
        )}
        <CardFooter className="flex gap-2">
          <Button onClick={onReset} variant="default">
            <RefreshCw className="mr-2 h-4 w-4" />
            Try Again
          </Button>
          <Button onClick={handleGoBack} variant="outline">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Go Back
          </Button>
          <Button onClick={handleGoHome} variant="outline">
            <Home className="mr-2 h-4 w-4" />
            Home
          </Button>
        </CardFooter>
      </Card>
    </div>
  );
}

// Functional wrapper with hooks
export function RouteErrorBoundary({ children, routeName, fallback }: Props) {
  return (
    <RouteErrorBoundaryClass routeName={routeName} fallback={fallback}>
      {children}
    </RouteErrorBoundaryClass>
  );
}

// Specific error boundaries for different sections
export function BuilderErrorBoundary({ children }: { children: ReactNode }) {
  return (
    <RouteErrorBoundary routeName="Builder">
      {children}
    </RouteErrorBoundary>
  );
}

export function ProjectsErrorBoundary({ children }: { children: ReactNode }) {
  return (
    <RouteErrorBoundary routeName="Projects">
      {children}
    </RouteErrorBoundary>
  );
}

export function AuditErrorBoundary({ children }: { children: ReactNode }) {
  return (
    <RouteErrorBoundary routeName="Audit">
      {children}
    </RouteErrorBoundary>
  );
}

export function DeploymentErrorBoundary({ children }: { children: ReactNode }) {
  return (
    <RouteErrorBoundary routeName="Deployment">
      {children}
    </RouteErrorBoundary>
  );
}
