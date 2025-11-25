import axios, { AxiosInstance, AxiosError, InternalAxiosRequestConfig, AxiosResponse } from 'axios';
import { handleApiError } from '../utils/errors';

// Get API URL from environment variables
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const IS_PRODUCTION = import.meta.env.VITE_ENV === 'production';

/**
 * Generate a unique request ID for tracking
 */
function generateRequestId(): string {
  return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
}

/**
 * Sanitize data to prevent XSS attacks
 */
function sanitizeData(data: any): any {
  if (typeof data === 'string') {
    // Remove potentially dangerous characters
    return data.replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '');
  }
  if (Array.isArray(data)) {
    return data.map(sanitizeData);
  }
  if (data && typeof data === 'object') {
    const sanitized: any = {};
    for (const key in data) {
      sanitized[key] = sanitizeData(data[key]);
    }
    return sanitized;
  }
  return data;
}

/**
 * Rate limit tracker
 */
class RateLimitTracker {
  private limits: Map<string, { remaining: number; reset: number }> = new Map();

  update(endpoint: string, headers: Record<string, string>) {
    const limit = parseInt(headers['x-ratelimit-limit'] || '0');
    const remaining = parseInt(headers['x-ratelimit-remaining'] || '0');
    const reset = parseInt(headers['x-ratelimit-reset'] || '0');

    if (limit > 0) {
      this.limits.set(endpoint, { remaining, reset });
    }
  }

  check(endpoint: string): boolean {
    const limit = this.limits.get(endpoint);
    if (!limit) return true;

    const now = Math.floor(Date.now() / 1000);
    if (now > limit.reset) {
      this.limits.delete(endpoint);
      return true;
    }

    return limit.remaining > 0;
  }

  getRemaining(endpoint: string): number | null {
    const limit = this.limits.get(endpoint);
    return limit ? limit.remaining : null;
  }
}

const rateLimitTracker = new RateLimitTracker();

/**
 * Create and configure Axios instance
 */
const createApiClient = (): AxiosInstance => {
  const client = axios.create({
    baseURL: API_BASE_URL,
    timeout: 30000,
    headers: {
      'Content-Type': 'application/json',
    },
    // Enable credentials for CORS
    withCredentials: false,
  });

  // Request interceptor
  client.interceptors.request.use(
    (config: InternalAxiosRequestConfig) => {
      // Generate unique request ID
      const requestId = generateRequestId();
      if (config.headers) {
        config.headers['X-Request-ID'] = requestId;
      }

      // Add timestamp to prevent caching for GET requests
      if (config.method === 'get') {
        if (config.params) {
          config.params._t = Date.now();
        } else {
          config.params = { _t: Date.now() };
        }
      }

      // Add session ID if available
      const sessionId = localStorage.getItem('session_id');
      if (sessionId && config.headers) {
        config.headers['X-Session-ID'] = sessionId;
      }

      // Check rate limit before sending request
      const endpoint = config.url || '';
      if (!rateLimitTracker.check(endpoint)) {
        const remaining = rateLimitTracker.getRemaining(endpoint);
        console.warn(`Rate limit reached for ${endpoint}. Remaining: ${remaining}`);
      }

      // Sanitize request data in production
      if (IS_PRODUCTION && config.data) {
        config.data = sanitizeData(config.data);
      }

      // Log request in development
      if (!IS_PRODUCTION) {
        console.log(`[API Request] ${config.method?.toUpperCase()} ${config.url}`, {
          requestId,
          data: config.data,
        });
      }

      return config;
    },
    (error: AxiosError) => {
      console.error('[API Request Error]', error);
      return Promise.reject(error);
    }
  );

  // Response interceptor
  client.interceptors.response.use(
    (response: AxiosResponse) => {
      // Update rate limit tracker
      const endpoint = response.config.url || '';
      rateLimitTracker.update(endpoint, response.headers as Record<string, string>);

      // Log response in development
      if (!IS_PRODUCTION) {
        const requestId = response.config.headers?.['X-Request-ID'];
        console.log(`[API Response] ${response.status} ${response.config.url}`, {
          requestId,
          data: response.data,
        });
      }

      return response;
    },
    (error: AxiosError) => {
      // Handle rate limit errors
      if (error.response?.status === 429) {
        const retryAfter = error.response.headers['retry-after'];
        console.warn(`Rate limited. Retry after ${retryAfter} seconds`);
      }

      // Handle authentication errors
      if (error.response?.status === 401) {
        console.warn('Unauthorized. Session may have expired.');
        // Clear invalid session
        localStorage.removeItem('session_id');
      }

      // Handle server errors
      if (error.response?.status && error.response.status >= 500) {
        console.error('Server error:', error.response.status);
      }

      const appError = handleApiError(error);
      
      // Log error in development
      if (!IS_PRODUCTION) {
        console.error('[API Error]', {
          url: error.config?.url,
          status: error.response?.status,
          message: appError.message,
        });
      }

      return Promise.reject(appError);
    }
  );

  return client;
};

// Export singleton instance
export const apiClient = createApiClient();

/**
 * Retry helper for failed requests with exponential backoff
 */
export async function retryRequest<T>(
  requestFn: () => Promise<T>,
  options: {
    maxRetries?: number;
    initialDelay?: number;
    maxDelay?: number;
    onRetry?: (attempt: number, error: any) => void;
  } = {}
): Promise<T> {
  const {
    maxRetries = 3,
    initialDelay = 1000,
    maxDelay = 10000,
    onRetry,
  } = options;

  let lastError: any;

  for (let attempt = 0; attempt < maxRetries; attempt++) {
    try {
      return await requestFn();
    } catch (error: any) {
      lastError = error;

      // Don't retry if not retryable
      if (!error.retryable) {
        throw error;
      }

      // Don't retry on last attempt
      if (attempt === maxRetries - 1) {
        throw error;
      }

      // Calculate delay with exponential backoff
      const delay = Math.min(initialDelay * Math.pow(2, attempt), maxDelay);

      // Call retry callback if provided
      if (onRetry) {
        onRetry(attempt + 1, error);
      }

      // Wait before retrying
      await new Promise((resolve) => setTimeout(resolve, delay));
    }
  }

  throw lastError;
}

/**
 * Create a retryable API call wrapper
 */
export function createRetryableRequest<T>(
  requestFn: () => Promise<T>,
  retryOptions?: Parameters<typeof retryRequest>[1]
) {
  return () => retryRequest(requestFn, retryOptions);
}
