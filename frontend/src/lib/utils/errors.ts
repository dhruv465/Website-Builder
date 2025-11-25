import { AxiosError } from 'axios';
import { toast } from 'sonner';
import { AppError, ErrorType } from '../types';

// Re-export ErrorType for convenience
export { ErrorType } from '../types';

/**
 * Convert Axios error to AppError
 */
export function handleApiError(error: AxiosError): AppError {
  if (error.response) {
    // Server responded with error status
    const status = error.response.status;
    const data = error.response.data as any;

    if (status >= 400 && status < 500) {
      return {
        type: ErrorType.VALIDATION_ERROR,
        message: data?.detail || data?.message || 'Invalid request',
        details: data,
        recoverable: true,
        retryable: false,
      };
    }

    if (status >= 500) {
      return {
        type: ErrorType.API_ERROR,
        message: data?.detail || 'Server error occurred',
        details: data,
        recoverable: true,
        retryable: true,
      };
    }
  }

  if (error.request) {
    // Request made but no response
    return {
      type: ErrorType.NETWORK_ERROR,
      message: 'Network error. Please check your connection.',
      details: error.message,
      recoverable: true,
      retryable: true,
    };
  }

  // Something else happened
  return {
    type: ErrorType.UNKNOWN_ERROR,
    message: error.message || 'An unexpected error occurred',
    details: error,
    recoverable: false,
    retryable: false,
  };
}

/**
 * Convert WebSocket error to AppError
 */
export function handleWebSocketError(error: Event): AppError {
  return {
    type: ErrorType.WEBSOCKET_ERROR,
    message: 'WebSocket connection error',
    details: error,
    recoverable: true,
    retryable: true,
  };
}

/**
 * Create a generic error
 */
export function createError(
  type: ErrorType,
  message: string,
  details?: any
): AppError {
  return {
    type,
    message,
    details,
    recoverable: type !== ErrorType.UNKNOWN_ERROR,
    retryable: type === ErrorType.NETWORK_ERROR || type === ErrorType.API_ERROR,
  };
}

/**
 * Get user-friendly error message with actionable guidance
 */
export function getUserFriendlyMessage(error: AppError): {
  title: string;
  message: string;
  action?: string;
} {
  switch (error.type) {
    case ErrorType.NETWORK_ERROR:
      return {
        title: 'Connection Error',
        message: 'Unable to connect to the server. Please check your internet connection.',
        action: 'Retry',
      };
    case ErrorType.VALIDATION_ERROR:
      return {
        title: 'Invalid Input',
        message: error.message || 'Please check your input and try again.',
        action: 'Fix Input',
      };
    case ErrorType.API_ERROR:
      return {
        title: 'Server Error',
        message: 'The server encountered an error. Please try again in a moment.',
        action: 'Retry',
      };
    case ErrorType.WEBSOCKET_ERROR:
      return {
        title: 'Connection Lost',
        message: 'Real-time connection was interrupted. Attempting to reconnect...',
        action: 'Reconnect',
      };
    case ErrorType.UNKNOWN_ERROR:
      return {
        title: 'Unexpected Error',
        message: error.message || 'Something went wrong. Please refresh the page.',
        action: 'Refresh',
      };
    default:
      return {
        title: 'Error',
        message: error.message || 'An error occurred',
      };
  }
}

/**
 * Show error toast notification
 */
export function showErrorToast(error: AppError, onRetry?: () => void): void {
  const { title, message, action } = getUserFriendlyMessage(error);

  if (error.retryable && onRetry) {
    toast.error(title, {
      description: message,
      action: {
        label: action || 'Retry',
        onClick: onRetry,
      },
      duration: 5000,
    });
  } else {
    toast.error(title, {
      description: message,
      duration: 4000,
    });
  }
}

/**
 * Show success toast notification
 */
export function showSuccessToast(message: string, description?: string): void {
  toast.success(message, {
    description,
    duration: 3000,
  });
}

/**
 * Show info toast notification
 */
export function showInfoToast(message: string, description?: string): void {
  toast.info(message, {
    description,
    duration: 3000,
  });
}

/**
 * Show warning toast notification
 */
export function showWarningToast(message: string, description?: string): void {
  toast.warning(message, {
    description,
    duration: 4000,
  });
}

/**
 * Log error for debugging
 */
export function logError(error: AppError, context?: string): void {
  const timestamp = new Date().toISOString();
  const logEntry = {
    timestamp,
    context,
    type: error.type,
    message: error.message,
    details: error.details,
    recoverable: error.recoverable,
    retryable: error.retryable,
  };

  // Log to console in development
  if (import.meta.env.DEV) {
    console.error('[Error Log]', logEntry);
  }

  // In production, you could send to error tracking service
  // Example: Sentry, LogRocket, etc.
  // sendToErrorTracking(logEntry);
}
