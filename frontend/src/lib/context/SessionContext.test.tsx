import { describe, it, expect, beforeEach, vi } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { SessionProvider, useSession } from './SessionContext';
import * as sessionsApi from '../api/sessions';
import { Session, UserPreferences } from '../types';

// Mock the sessions API
vi.mock('../api/sessions');

const mockSession: Session = {
  id: 'test-session-id',
  created_at: '2024-01-01T00:00:00Z',
  last_accessed_at: '2024-01-01T00:00:00Z',
  preferences: {
    default_color_scheme: 'light',
    design_style: 'modern',
  },
  sites: [],
};

describe('SessionContext', () => {
  beforeEach(() => {
    // Clear localStorage before each test
    localStorage.clear();
    
    // Reset all mocks
    vi.clearAllMocks();
    
    // Setup default mock implementations
    vi.mocked(sessionsApi.createSession).mockResolvedValue(mockSession);
    vi.mocked(sessionsApi.getSession).mockResolvedValue(mockSession);
    vi.mocked(sessionsApi.updateSession).mockResolvedValue(mockSession);
    vi.mocked(sessionsApi.updateSessionPreferences).mockResolvedValue(mockSession);
  });

  it('should create a new session on mount when no stored session exists', async () => {
    const { result } = renderHook(() => useSession(), {
      wrapper: SessionProvider,
    });

    expect(result.current.isLoading).toBe(true);

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.session).toEqual(mockSession);
    expect(sessionsApi.createSession).toHaveBeenCalledTimes(1);
    expect(localStorage.getItem('session_id')).toBe(mockSession.id);
  });

  it('should restore session from localStorage on mount', async () => {
    localStorage.setItem('session_id', 'existing-session-id');

    const { result } = renderHook(() => useSession(), {
      wrapper: SessionProvider,
    });

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(sessionsApi.getSession).toHaveBeenCalledWith('existing-session-id');
    expect(result.current.session).toEqual(mockSession);
  });

  it('should update session preferences', async () => {
    const { result } = renderHook(() => useSession(), {
      wrapper: SessionProvider,
    });

    await waitFor(() => {
      expect(result.current.session).not.toBeNull();
    });

    const newPreferences: UserPreferences = {
      default_color_scheme: 'dark',
      design_style: 'minimal',
    };

    await result.current.updatePreferences(newPreferences);

    expect(sessionsApi.updateSessionPreferences).toHaveBeenCalledWith(
      mockSession.id,
      newPreferences
    );
  });

  it('should export session data', async () => {
    const { result } = renderHook(() => useSession(), {
      wrapper: SessionProvider,
    });

    await waitFor(() => {
      expect(result.current.session).not.toBeNull();
    });

    const exportedData = result.current.exportSession();
    const parsed = JSON.parse(exportedData);

    expect(parsed.session).toEqual(mockSession);
    expect(parsed.version).toBe('1.0');
    expect(parsed.exportedAt).toBeDefined();
  });

  it('should clear session', async () => {
    const { result } = renderHook(() => useSession(), {
      wrapper: SessionProvider,
    });

    await waitFor(() => {
      expect(result.current.session).not.toBeNull();
    });

    result.current.clearSession();

    await waitFor(() => {
      expect(result.current.session).toBeNull();
    });
    
    expect(localStorage.getItem('session_id')).toBeNull();
  });
});
