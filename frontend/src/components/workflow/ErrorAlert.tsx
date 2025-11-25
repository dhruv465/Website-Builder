import { AlertTriangle, RefreshCw, X } from 'lucide-react';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import { AppError } from '@/lib/types';
import { getUserFriendlyMessage } from '@/lib/utils/errors';

interface ErrorAlertProps {
  error: AppError | null;
  onRetry?: () => void;
  onDismiss?: () => void;
  className?: string;
}

export function ErrorAlert({ error, onRetry, onDismiss, className }: ErrorAlertProps) {
  if (!error) return null;

  const { title, message, action } = getUserFriendlyMessage(error);

  return (
    <Alert variant="destructive" className={className}>
      <AlertTriangle className="h-4 w-4" />
      <AlertTitle className="flex items-center justify-between">
        <span>{title}</span>
        {onDismiss && (
          <Button
            variant="ghost"
            size="sm"
            onClick={onDismiss}
            className="h-6 w-6 p-0 hover:bg-transparent"
          >
            <X className="h-4 w-4" />
          </Button>
        )}
      </AlertTitle>
      <AlertDescription>
        <div className="mt-2 space-y-3">
          <p className="text-sm">{message}</p>
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
        </div>
      </AlertDescription>
    </Alert>
  );
}
