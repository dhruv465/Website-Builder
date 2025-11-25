import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Separator } from '@/components/ui/separator';
import {
  ErrorDisplay,
  InlineError,
  NetworkError,
  EmptyStateError,
  ConnectionStatus,
  InlineConnectionStatus,
} from '@/components/shared';
import { ErrorAlert } from '@/components/workflow';
import { AppError, ErrorType } from '@/lib/types';
import {
  showErrorToast,
  showSuccessToast,
  showInfoToast,
  showWarningToast,
  createError,
} from '@/lib/utils/errors';
import { useApiCall } from '@/lib/hooks/useApiCall';
import { ConnectionState } from '@/lib/websocket/client';

export default function ErrorHandlingTestPage() {
  const [selectedError, setSelectedError] = useState<AppError | null>(null);
  const [connectionStatus, setConnectionStatus] = useState<ConnectionState>(ConnectionState.CONNECTED);

  // Example API call with error handling
  const mockApiCall = async (shouldFail: boolean) => {
    await new Promise((resolve) => setTimeout(resolve, 1000));
    if (shouldFail) {
      throw createError(ErrorType.API_ERROR, 'Mock API error occurred');
    }
    return { success: true, data: 'Mock data' };
  };

  const { loading, execute, error, retry } = useApiCall(mockApiCall, {
    context: 'Test Page',
    showErrorToast: true,
  });

  const handleTestError = (type: ErrorType) => {
    const errors: Record<ErrorType, AppError> = {
      [ErrorType.NETWORK_ERROR]: createError(
        ErrorType.NETWORK_ERROR,
        'Failed to connect to server'
      ),
      [ErrorType.VALIDATION_ERROR]: createError(
        ErrorType.VALIDATION_ERROR,
        'Invalid input provided'
      ),
      [ErrorType.API_ERROR]: createError(ErrorType.API_ERROR, 'Server returned an error'),
      [ErrorType.WEBSOCKET_ERROR]: createError(
        ErrorType.WEBSOCKET_ERROR,
        'WebSocket connection lost'
      ),
      [ErrorType.UNKNOWN_ERROR]: createError(
        ErrorType.UNKNOWN_ERROR,
        'An unexpected error occurred'
      ),
    };

    setSelectedError(errors[type]);
  };

  const handleTestToast = (type: 'error' | 'success' | 'info' | 'warning') => {
    switch (type) {
      case 'error':
        showErrorToast(
          createError(ErrorType.API_ERROR, 'This is an error toast'),
          () => console.log('Retry clicked')
        );
        break;
      case 'success':
        showSuccessToast('Success!', 'Operation completed successfully');
        break;
      case 'info':
        showInfoToast('Information', 'This is an informational message');
        break;
      case 'warning':
        showWarningToast('Warning', 'Please be careful with this action');
        break;
    }
  };

  const cycleConnectionStatus = () => {
    const states: ConnectionState[] = [
      ConnectionState.CONNECTED,
      ConnectionState.CONNECTING,
      ConnectionState.DISCONNECTED,
      ConnectionState.ERROR,
    ];
    const currentIndex = states.indexOf(connectionStatus);
    const nextIndex = (currentIndex + 1) % states.length;
    const nextState = states[nextIndex];
    if (nextState) {
      setConnectionStatus(nextState);
    }
  };

  return (
    <div className="container mx-auto space-y-8 p-8">
      <div>
        <h1 className="text-3xl font-bold">Error Handling System Test</h1>
        <p className="text-muted-foreground">
          Test and demonstrate the error handling and user feedback system
        </p>
      </div>

      <Separator />

      {/* Toast Notifications */}
      <Card>
        <CardHeader>
          <CardTitle>Toast Notifications</CardTitle>
          <CardDescription>Test different types of toast notifications</CardDescription>
        </CardHeader>
        <CardContent className="flex flex-wrap gap-2">
          <Button onClick={() => handleTestToast('error')} variant="destructive">
            Error Toast
          </Button>
          <Button onClick={() => handleTestToast('success')} variant="default">
            Success Toast
          </Button>
          <Button onClick={() => handleTestToast('info')} variant="secondary">
            Info Toast
          </Button>
          <Button onClick={() => handleTestToast('warning')} variant="outline">
            Warning Toast
          </Button>
        </CardContent>
      </Card>

      {/* Error Display Components */}
      <Card>
        <CardHeader>
          <CardTitle>Error Display Components</CardTitle>
          <CardDescription>Test different error display components</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex flex-wrap gap-2">
            <Button onClick={() => handleTestError(ErrorType.NETWORK_ERROR)} variant="outline">
              Network Error
            </Button>
            <Button onClick={() => handleTestError(ErrorType.VALIDATION_ERROR)} variant="outline">
              Validation Error
            </Button>
            <Button onClick={() => handleTestError(ErrorType.API_ERROR)} variant="outline">
              API Error
            </Button>
            <Button onClick={() => handleTestError(ErrorType.WEBSOCKET_ERROR)} variant="outline">
              WebSocket Error
            </Button>
            <Button onClick={() => handleTestError(ErrorType.UNKNOWN_ERROR)} variant="outline">
              Unknown Error
            </Button>
            <Button onClick={() => setSelectedError(null)} variant="ghost">
              Clear
            </Button>
          </div>

          {selectedError && (
            <ErrorDisplay
              error={selectedError}
              onRetry={() => console.log('Retry clicked')}
              onDismiss={() => setSelectedError(null)}
            />
          )}
        </CardContent>
      </Card>

      {/* Inline Error */}
      <Card>
        <CardHeader>
          <CardTitle>Inline Error</CardTitle>
          <CardDescription>Small inline error messages for forms</CardDescription>
        </CardHeader>
        <CardContent>
          <InlineError message="This field is required" />
        </CardContent>
      </Card>

      {/* Network Error Display */}
      <Card>
        <CardHeader>
          <CardTitle>Network Error Display</CardTitle>
          <CardDescription>Full-page network error component</CardDescription>
        </CardHeader>
        <CardContent>
          <NetworkError onRetry={() => console.log('Retry network connection')} />
        </CardContent>
      </Card>

      {/* Empty State Error */}
      <Card>
        <CardHeader>
          <CardTitle>Empty State Error</CardTitle>
          <CardDescription>Error state for empty lists or failed loads</CardDescription>
        </CardHeader>
        <CardContent>
          <EmptyStateError
            title="Failed to Load Projects"
            message="We couldn't load your projects. Please try again."
            onAction={() => console.log('Retry loading')}
            actionLabel="Reload"
          />
        </CardContent>
      </Card>

      {/* Connection Status Indicators */}
      <Card>
        <CardHeader>
          <CardTitle>Connection Status Indicators</CardTitle>
          <CardDescription>WebSocket connection status indicators</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center gap-4">
            <Button onClick={cycleConnectionStatus} variant="outline">
              Cycle Status ({connectionStatus})
            </Button>
            <ConnectionStatus
              status={connectionStatus}
              onReconnect={() => console.log('Reconnect clicked')}
              showLabel
            />
          </div>

          <div className="space-y-2">
            <p className="text-sm font-medium">All States:</p>
            <div className="flex flex-wrap gap-4">
              <InlineConnectionStatus status={ConnectionState.CONNECTED} />
              <InlineConnectionStatus status={ConnectionState.CONNECTING} />
              <InlineConnectionStatus status={ConnectionState.DISCONNECTED} />
              <InlineConnectionStatus status={ConnectionState.ERROR} />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* API Call with Error Handling */}
      <Card>
        <CardHeader>
          <CardTitle>API Call with Retry Logic</CardTitle>
          <CardDescription>Test API calls with automatic error handling and retry</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex gap-2">
            <Button onClick={() => execute(false)} disabled={loading}>
              {loading ? 'Loading...' : 'Successful API Call'}
            </Button>
            <Button onClick={() => execute(true)} disabled={loading} variant="destructive">
              {loading ? 'Loading...' : 'Failed API Call'}
            </Button>
            {error && (
              <Button onClick={retry} variant="outline">
                Retry
              </Button>
            )}
          </div>

          {error && <ErrorAlert error={error} onRetry={retry} onDismiss={() => {}} />}
        </CardContent>
      </Card>

      {/* Error Boundary Test */}
      <Card>
        <CardHeader>
          <CardTitle>Error Boundary Test</CardTitle>
          <CardDescription>
            Test error boundaries (this will break the component tree)
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Button
            onClick={() => {
              throw new Error('Test error boundary');
            }}
            variant="destructive"
          >
            Throw Error
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}
