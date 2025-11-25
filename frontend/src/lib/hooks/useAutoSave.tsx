import { useEffect, useRef, useState, useCallback } from 'react';

export interface UseAutoSaveOptions<T> {
  data: T;
  onSave: (data: T) => Promise<void> | void;
  interval?: number; // in milliseconds, default 30000 (30 seconds)
  enabled?: boolean;
  debounceDelay?: number; // in milliseconds, default 1000
}

export interface UseAutoSaveReturn {
  isSaving: boolean;
  lastSaved: Date | null;
  error: Error | null;
  saveNow: () => Promise<void>;
  isDirty: boolean;
}

/**
 * Custom hook for auto-saving data at regular intervals with debouncing.
 * 
 * @param options - Configuration options
 * @returns Object containing save status and manual save function
 * 
 * @example
 * ```tsx
 * const { isSaving, lastSaved, saveNow, isDirty } = useAutoSave({
 *   data: { htmlCode, cssCode, jsCode },
 *   onSave: async (data) => {
 *     await api.updateSite(siteId, data);
 *   },
 *   interval: 30000, // 30 seconds
 *   enabled: true,
 * });
 * 
 * return (
 *   <div>
 *     {isSaving && <span>Saving...</span>}
 *     {lastSaved && <span>Last saved: {lastSaved.toLocaleTimeString()}</span>}
 *     {isDirty && <span>Unsaved changes</span>}
 *     <button onClick={saveNow}>Save Now</button>
 *   </div>
 * );
 * ```
 */
export function useAutoSave<T>({
  data,
  onSave,
  interval = 30000,
  enabled = true,
  debounceDelay = 1000,
}: UseAutoSaveOptions<T>): UseAutoSaveReturn {
  const [isSaving, setIsSaving] = useState(false);
  const [lastSaved, setLastSaved] = useState<Date | null>(null);
  const [error, setError] = useState<Error | null>(null);
  const [isDirty, setIsDirty] = useState(false);

  const lastDataRef = useRef<T>(data);
  const saveTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const debounceTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  const performSave = useCallback(async () => {
    if (!enabled || isSaving) return;

    try {
      setIsSaving(true);
      setError(null);
      await onSave(data);
      setLastSaved(new Date());
      setIsDirty(false);
      lastDataRef.current = data;
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Save failed'));
      console.error('Auto-save error:', err);
    } finally {
      setIsSaving(false);
    }
  }, [data, onSave, enabled, isSaving]);

  const saveNow = useCallback(async () => {
    // Clear any pending saves
    if (debounceTimeoutRef.current) {
      clearTimeout(debounceTimeoutRef.current);
      debounceTimeoutRef.current = null;
    }
    if (saveTimeoutRef.current) {
      clearTimeout(saveTimeoutRef.current);
      saveTimeoutRef.current = null;
    }

    await performSave();
  }, [performSave]);

  // Detect changes and mark as dirty
  useEffect(() => {
    const hasChanged = JSON.stringify(data) !== JSON.stringify(lastDataRef.current);
    if (hasChanged && !isDirty) {
      setIsDirty(true);
    }
  }, [data, isDirty]);

  // Debounced auto-save on data change
  useEffect(() => {
    if (!enabled || !isDirty) return;

    // Clear existing debounce timeout
    if (debounceTimeoutRef.current) {
      clearTimeout(debounceTimeoutRef.current);
    }

    // Set new debounce timeout
    debounceTimeoutRef.current = setTimeout(() => {
      performSave();
    }, debounceDelay);

    return () => {
      if (debounceTimeoutRef.current) {
        clearTimeout(debounceTimeoutRef.current);
      }
    };
  }, [data, enabled, isDirty, debounceDelay, performSave]);

  // Interval-based auto-save
  useEffect(() => {
    if (!enabled || interval <= 0) return;

    saveTimeoutRef.current = setInterval(() => {
      if (isDirty) {
        performSave();
      }
    }, interval);

    return () => {
      if (saveTimeoutRef.current) {
        clearInterval(saveTimeoutRef.current);
      }
    };
  }, [enabled, interval, isDirty, performSave]);

  // Save on unmount if dirty
  useEffect(() => {
    return () => {
      if (isDirty && enabled) {
        // Synchronous save on unmount
        onSave(data);
      }
    };
  }, []);

  return {
    isSaving,
    lastSaved,
    error,
    saveNow,
    isDirty,
  };
}

/**
 * Component to display auto-save status
 */
export interface AutoSaveIndicatorProps {
  isSaving: boolean;
  lastSaved: Date | null;
  isDirty: boolean;
  error: Error | null;
}

export function AutoSaveIndicator({
  isSaving,
  lastSaved,
  isDirty,
  error,
}: AutoSaveIndicatorProps) {
  if (error) {
    return (
      <div className="flex items-center gap-2 text-sm text-destructive">
        <span className="h-2 w-2 rounded-full bg-destructive" />
        <span>Save failed</span>
      </div>
    );
  }

  if (isSaving) {
    return (
      <div className="flex items-center gap-2 text-sm text-muted-foreground">
        <span className="h-2 w-2 rounded-full bg-primary animate-pulse" />
        <span>Saving...</span>
      </div>
    );
  }

  if (isDirty) {
    return (
      <div className="flex items-center gap-2 text-sm text-muted-foreground">
        <span className="h-2 w-2 rounded-full bg-amber-500" />
        <span>Unsaved changes</span>
      </div>
    );
  }

  if (lastSaved) {
    return (
      <div className="flex items-center gap-2 text-sm text-muted-foreground">
        <span className="h-2 w-2 rounded-full bg-green-500" />
        <span>Saved {formatTimeSince(lastSaved)}</span>
      </div>
    );
  }

  return null;
}

function formatTimeSince(date: Date): string {
  const seconds = Math.floor((new Date().getTime() - date.getTime()) / 1000);

  if (seconds < 60) return 'just now';
  if (seconds < 120) return '1 minute ago';
  if (seconds < 3600) return `${Math.floor(seconds / 60)} minutes ago`;
  if (seconds < 7200) return '1 hour ago';
  return `${Math.floor(seconds / 3600)} hours ago`;
}
