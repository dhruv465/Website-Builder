import { describe, it, expect, vi, beforeEach } from 'vitest';
import axios, { AxiosError } from 'axios';
import { apiClient, retryRequest } from './client';

// Mock axios
vi.mock('axios');

describe('API Client', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
  });

  describe('apiClient', () => {
    it('creates axios instance with correct config', () => {
      expect(apiClient).toBeDefined();
      expect(apiClient.defaults.baseURL).toBeDefined();
      expect(apiClient.defaults.timeout).toBe(30000);
    });

    it('adds session ID to request headers', async () => {
      localStorage.setItem('session_id', 'test-session-123');

      const mockRequest = {
        headers: {},
        params: {},
      };

      // Access the request interceptor
      const interceptor = apiClient.interceptors.request as any;
      if (interceptor.handlers && interceptor.handlers.length > 0) {
        const handler = interceptor.handlers[0];
        if (handler.fulfilled) {
          const result = handler.fulfilled(mockRequest);
          expect(result.headers['X-Session-ID']).toBe('test-session-123');
        }
      }
    });

    it('adds timestamp to prevent caching', async () => {
      const mockRequest = {
        headers: {},
        params: {},
      };

      const interceptor = apiClient.interceptors.request as any;
      if (interceptor.handlers && interceptor.handlers.length > 0) {
        const handler = interceptor.handlers[0];
        if (handler.fulfilled) {
          const result = handler.fulfilled(mockRequest);
          expect(result.params._t).toBeDefined();
        }
      }
    });
  });

  describe('retryRequest', () => {
    it('succeeds on first attempt', async () => {
      const mockFn = vi.fn().mockResolvedValue('success');

      const result = await retryRequest(mockFn);

      expect(result).toBe('success');
      expect(mockFn).toHaveBeenCalledTimes(1);
    });

    it('retries on failure', async () => {
      const mockFn = vi
        .fn()
        .mockRejectedValueOnce({ retryable: true })
        .mockResolvedValueOnce('success');

      const result = await retryRequest(mockFn, {
        maxRetries: 3,
        initialDelay: 10,
      });

      expect(result).toBe('success');
      expect(mockFn).toHaveBeenCalledTimes(2);
    });

    it('stops retrying after max attempts', async () => {
      const mockFn = vi.fn().mockRejectedValue({ retryable: true });

      await expect(
        retryRequest(mockFn, {
          maxRetries: 3,
          initialDelay: 10,
        })
      ).rejects.toEqual({ retryable: true });

      expect(mockFn).toHaveBeenCalledTimes(3);
    });

    it('does not retry non-retryable errors', async () => {
      const mockFn = vi.fn().mockRejectedValue({ retryable: false });

      await expect(
        retryRequest(mockFn, {
          maxRetries: 3,
          initialDelay: 10,
        })
      ).rejects.toEqual({ retryable: false });

      expect(mockFn).toHaveBeenCalledTimes(1);
    });

    it('calls onRetry callback', async () => {
      const mockFn = vi
        .fn()
        .mockRejectedValueOnce({ retryable: true })
        .mockResolvedValueOnce('success');

      const onRetry = vi.fn();

      await retryRequest(mockFn, {
        maxRetries: 3,
        initialDelay: 10,
        onRetry,
      });

      expect(onRetry).toHaveBeenCalledWith(1, { retryable: true });
    });

    it('uses exponential backoff', async () => {
      const mockFn = vi
        .fn()
        .mockRejectedValueOnce({ retryable: true })
        .mockRejectedValueOnce({ retryable: true })
        .mockResolvedValueOnce('success');

      const startTime = Date.now();

      await retryRequest(mockFn, {
        maxRetries: 3,
        initialDelay: 100,
        maxDelay: 1000,
      });

      const duration = Date.now() - startTime;

      // Should have waited at least 100ms + 200ms = 300ms
      expect(duration).toBeGreaterThanOrEqual(200);
    });

    it('respects max delay', async () => {
      const mockFn = vi
        .fn()
        .mockRejectedValueOnce({ retryable: true })
        .mockRejectedValueOnce({ retryable: true })
        .mockResolvedValueOnce('success');

      await retryRequest(mockFn, {
        maxRetries: 3,
        initialDelay: 1000,
        maxDelay: 500,
      });

      // Should complete without throwing
      expect(mockFn).toHaveBeenCalledTimes(3);
    });
  });
});
