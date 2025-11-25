import { AlertTriangle, WifiOff, ServerCrash, AlertCircle, RefreshCw } from 'lucide-react';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import { AppError, ErrorType } from '@/lib/types';
import { getUserFriendlyMessage } from '@/lib/utils/errors';

interface ErrorDisplayProps {
  error: AppError;
  onRetry?: () => void;
  onDismiss?: () => void;
  className?: string;
}

export function ErrorDisplay({ error, onRetry, onDismiss, className }: ErrorDisplayProps) {
  const { title, message, action } = getUserFriendlyMessage(error);

  const getIcon = () => {
    switch (error.type) {
      case ErrorType.NETWORK_ERROR:
        return <WifiOff className="h-4 w-4" />;
      case ErrorType.API_ERROR:
        return <ServerCrash className="h-4 w-4" />;
      case ErrorType.WEBSOCKET_ERROR:
        return <WifiOff className="h-4 w-4" />;
      case ErrorType.VALIDATION_ERROR:
        return <AlertCircle className="h-4 w-4" />;
      default:
        return <AlertTriangle className="h-4 w-4" />;
    }
  };

  return (
    <Alert variant="destructive" className={className}>
      {getIcon()}
      <AlertTitle>{title}</AlertTitle>
      <AlertDescription>
        <div className="mt-2 space-y-3">
          <p>{message}</p>
          {(error.retryable || onDismiss) && (
            <div className="flex gap-2">
              {error.retryable && onRetry && (
                <Button
                  size="sm"
                  variant="outline"
                  onClick={onRetry}
                  className="bg-background hover:bg-accent"
                >
                  <RefreshCw className="mr-2 h-3 w-3" />
                  {action || 'Retry'}
                </Button>
              )}
              {onDismiss && (
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={onDismiss}
                  className="text-foreground hover:bg-accent"
                >
                  Dismiss
                </Button>
              )}
            </div>
          )}
        </div>
      </AlertDescription>
    </Alert>
  );
}

// Inline error display for forms and smaller components
interface InlineErrorProps {
  message: string;
  className?: string;
}

export function InlineError({ message, className }: InlineErrorProps) {
  return (
    <div className={`flex items-center gap-2 text-sm text-destructive ${className}`}>
      <AlertCircle className="h-4 w-4" />
      <span>{message}</span>
    </div>
  );
}

// Network error specific display
interface NetworkErrorProps {
  onRetry?: () => void;
  className?: string;
}

export function NetworkError({ onRetry, className }: NetworkErrorProps) {
  return (
    <div className={`flex flex-col items-center justify-center gap-4 p-8 text-center ${className}`}>
      <WifiOff className="h-12 w-12 text-muted-foreground" />
      <div className="space-y-2">
        <h3 className="text-lg font-semibold">Connection Lost</h3>
        <p className="text-sm text-muted-foreground">
          Unable to connect to the server. Please check your internet connection.
        </p>
      </div>
      {onRetry && (
        <Button onClick={onRetry} variant="default">
          <RefreshCw className="mr-2 h-4 w-4" />
          Try Again
        </Button>
      )}
    </div>
  );
}

// Empty state with error context
interface EmptyStateErrorProps {
  title: string;
  message: string;
  onAction?: () => void;
  actionLabel?: string;
  className?: string;
}

export function EmptyStateError({
  title,
  message,
  onAction,
  actionLabel = 'Try Again',
  className,
}: EmptyStateErrorProps) {
  return (
    <div className={`flex flex-col items-center justify-center gap-4 p-8 text-center ${className}`}>
      <AlertTriangle className="h-12 w-12 text-muted-foreground" />
      <div className="space-y-2">
        <h3 className="text-lg font-semibold">{title}</h3>
        <p className="text-sm text-muted-foreground">{message}</p>
      </div>
      {onAction && (
        <Button onClick={onAction} variant="default">
          {actionLabel}
        </Button>
      )}
    </div>
  );
}
