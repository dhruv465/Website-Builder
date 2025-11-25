import React, { createContext, useContext, useEffect, useState, useCallback } from 'react';
import { Session, UserPreferences } from '../types';
import {
  createSession,
  getSession,
  updateSession,
  updateSessionPreferences,
} from '../api/sessions';

// Session storage key
const SESSION_ID_KEY = 'session_id';

interface SessionContextValue {
  session: Session | null;
  isLoading: boolean;
  error: Error | null;
  createNewSession: () => Promise<void>;
  loadSession: (sessionId: string) => Promise<void>;
  updateSessionData: (data: Partial<Session>) => Promise<void>;
  updatePreferences: (preferences: UserPreferences) => Promise<void>;
  exportSession: () => string;
  importSession: (data: string) => Promise<void>;
  clearSession: () => void;
  refreshSession: () => Promise<void>;
}

const SessionContext = createContext<SessionContextValue | undefined>(undefined);

interface SessionProviderProps {
  children: React.ReactNode;
}

export function SessionProvider({ children }: SessionProviderProps) {
  const [session, setSession] = useState<Session | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  /**
   * Create a new session
   */
  const createNewSession = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);
      
      const newSession = await createSession();
      setSession(newSession);
      
      // Persist session ID to localStorage
      localStorage.setItem(SESSION_ID_KEY, newSession.id);
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to create session');
      setError(error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, []);

  /**
   * Load an existing session by ID
   */
  const loadSession = useCallback(async (sessionId: string) => {
    try {
      setIsLoading(true);
      setError(null);
      
      const loadedSession = await getSession(sessionId);
      setSession(loadedSession);
      
      // Persist session ID to localStorage
      localStorage.setItem(SESSION_ID_KEY, loadedSession.id);
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to load session');
      setError(error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, []);

  /**
   * Refresh current session data
   */
  const refreshSession = useCallback(async () => {
    if (!session) return;
    // Don't set loading state for background refresh
    try {
      const loadedSession = await getSession(session.id);
      setSession(loadedSession);
    } catch (err) {
      console.error('Failed to refresh session:', err);
    }
  }, [session]);

  /**
   * Update session data
   */
  const updateSessionData = useCallback(async (data: Partial<Session>) => {
    if (!session) {
      throw new Error('No active session');
    }

    try {
      setError(null);
      
      const updatedSession = await updateSession(session.id, data);
      setSession(updatedSession);
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to update session');
      setError(error);
      throw error;
    }
  }, [session]);

  /**
   * Update session preferences
   */
  const updatePreferences = useCallback(async (preferences: UserPreferences) => {
    if (!session) {
      throw new Error('No active session');
    }

    try {
      setError(null);
      
      const updatedSession = await updateSessionPreferences(session.id, preferences);
      setSession(updatedSession);
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to update preferences');
      setError(error);
      throw error;
    }
  }, [session]);

  /**
   * Export session data as JSON string
   */
  const exportSession = useCallback((): string => {
    if (!session) {
      throw new Error('No active session to export');
    }

    const exportData = {
      session,
      exportedAt: new Date().toISOString(),
      version: '1.0',
    };

    return JSON.stringify(exportData, null, 2);
  }, [session]);

  /**
   * Import session data from JSON string
   */
  const importSession = useCallback(async (data: string) => {
    try {
      setIsLoading(true);
      setError(null);

      const importData = JSON.parse(data);
      
      if (!importData.session || !importData.session.id) {
        throw new Error('Invalid session data format');
      }

      // Load the session from the backend to ensure it exists
      await loadSession(importData.session.id);
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to import session');
      setError(error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, [loadSession]);

  /**
   * Clear current session
   */
  const clearSession = useCallback(() => {
    setSession(null);
    setError(null);
    localStorage.removeItem(SESSION_ID_KEY);
  }, []);

  /**
   * Restore session on app load
   */
  useEffect(() => {
    const restoreSession = async () => {
      const storedSessionId = localStorage.getItem(SESSION_ID_KEY);

      if (storedSessionId) {
        try {
          await loadSession(storedSessionId);
        } catch (err) {
          console.error('Failed to restore session:', err);
          // Clear invalid session ID
          localStorage.removeItem(SESSION_ID_KEY);
          setIsLoading(false);
        }
      } else {
        // No stored session, create a new one
        try {
          await createNewSession();
        } catch (err) {
          console.error('Failed to create initial session:', err);
          setIsLoading(false);
        }
      }
    };

    restoreSession();
  }, []); // Empty dependency array - only run on mount

  const value: SessionContextValue = {
    session,
    isLoading,
    error,
    createNewSession,
    loadSession,
    refreshSession,
    updateSessionData,
    updatePreferences,
    exportSession,
    importSession,
    clearSession,
  };

  return (
    <SessionContext.Provider value={value}>
      {children}
    </SessionContext.Provider>
  );
}

/**
 * Custom hook to access session context
 */
export function useSession(): SessionContextValue {
  const context = useContext(SessionContext);
  
  if (context === undefined) {
    throw new Error('useSession must be used within a SessionProvider');
  }
  
  return context;
}
