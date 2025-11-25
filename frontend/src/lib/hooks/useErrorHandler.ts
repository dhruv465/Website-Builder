import { useCallback } from 'react';
import { AppError } from '../types';
import { showErrorToast, logError } from '../utils/errors';

interface UseErrorHandlerOptions {
  context?: string;
  onError?: (error: AppError) => void;
  showToast?: boolean;
}

export function useErrorHandler(options: UseErrorHandlerOptions = {}) {
  const { context, onError, showToast = true } = options;

  const handleError = useCallback(
    (error: AppError, retryFn?: () => void) => {
      // Log the error
      logError(error, context);

      // Show toast notification
      if (showToast) {
        showErrorToast(error, retryFn);
      }

      // Call custom error handler
      if (onError) {
        onError(error);
      }
    },
    [context, onError, showToast]
  );

  return { handleError };
}
