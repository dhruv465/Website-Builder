import { useState, useCallback } from 'react';
import { AppError } from '../types';
import { retryRequest } from '../api/client';
import { useErrorHandler } from './useErrorHandler';

interface UseApiCallOptions<T> {
  onSuccess?: (data: T) => void;
  onError?: (error: AppError) => void;
  showErrorToast?: boolean;
  retryable?: boolean;
  maxRetries?: number;
  context?: string;
}

interface UseApiCallResult<T> {
  data: T | null;
  error: AppError | null;
  loading: boolean;
  execute: (...args: any[]) => Promise<T | null>;
  reset: () => void;
  retry: () => Promise<T | null>;
}

export function useApiCall<T>(
  apiFunction: (...args: any[]) => Promise<T>,
  options: UseApiCallOptions<T> = {}
): UseApiCallResult<T> {
  const {
    onSuccess,
    onError,
    showErrorToast = true,
    retryable = true,
    maxRetries = 3,
    context,
  } = options;

  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState<AppError | null>(null);
  const [loading, setLoading] = useState(false);
  const [lastArgs, setLastArgs] = useState<any[]>([]);

  const { handleError } = useErrorHandler({
    context,
    onError,
    showToast: showErrorToast,
  });

  const execute = useCallback(
    async (...args: any[]): Promise<T | null> => {
      setLoading(true);
      setError(null);
      setLastArgs(args);

      try {
        let result: T;

        if (retryable) {
          result = await retryRequest(
            () => apiFunction(...args),
            {
              maxRetries,
              onRetry: (attempt, retryError) => {
                console.log(`Retry attempt ${attempt} after error:`, retryError);
              },
            }
          );
        } else {
          result = await apiFunction(...args);
        }

        setData(result);
        setLoading(false);

        if (onSuccess) {
          onSuccess(result);
        }

        return result;
      } catch (err: any) {
        const appError = err as AppError;
        setError(appError);
        setLoading(false);
        handleError(appError, retryable ? () => execute(...args) : undefined);
        return null;
      }
    },
    [apiFunction, retryable, maxRetries, onSuccess, handleError]
  );

  const retry = useCallback(async (): Promise<T | null> => {
    if (lastArgs.length === 0) {
      console.warn('No previous arguments to retry with');
      return null;
    }
    return execute(...lastArgs);
  }, [execute, lastArgs]);

  const reset = useCallback(() => {
    setData(null);
    setError(null);
    setLoading(false);
    setLastArgs([]);
  }, []);

  return {
    data,
    error,
    loading,
    execute,
    reset,
    retry,
  };
}
