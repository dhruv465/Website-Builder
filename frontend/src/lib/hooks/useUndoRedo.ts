import { useState, useCallback, useRef } from 'react';

export interface HistoryState<T> {
  past: T[];
  present: T;
  future: T[];
}

export interface UseUndoRedoReturn<T> {
  state: T;
  setState: (newState: T | ((prev: T) => T)) => void;
  undo: () => void;
  redo: () => void;
  canUndo: boolean;
  canRedo: boolean;
  reset: (newState: T) => void;
  clear: () => void;
}

const MAX_HISTORY_LENGTH = 50;

/**
 * Custom hook for undo/redo functionality with a maximum history length of 50 steps.
 * 
 * @param initialState - The initial state value
 * @returns Object containing state, setState, undo, redo, and helper flags
 * 
 * @example
 * ```tsx
 * const { state, setState, undo, redo, canUndo, canRedo } = useUndoRedo({
 *   htmlCode: '',
 *   cssCode: '',
 *   jsCode: ''
 * });
 * 
 * // Update state (adds to history)
 * setState({ htmlCode: '<div>Hello</div>', cssCode: '', jsCode: '' });
 * 
 * // Undo last change
 * if (canUndo) undo();
 * 
 * // Redo last undone change
 * if (canRedo) redo();
 * ```
 */
export function useUndoRedo<T>(initialState: T): UseUndoRedoReturn<T> {
  const [history, setHistory] = useState<HistoryState<T>>({
    past: [],
    present: initialState,
    future: [],
  });

  const setState = useCallback((newState: T | ((prev: T) => T)) => {
    setHistory((currentHistory) => {
      const resolvedState = typeof newState === 'function' 
        ? (newState as (prev: T) => T)(currentHistory.present)
        : newState;

      // Don't add to history if state hasn't changed
      if (JSON.stringify(resolvedState) === JSON.stringify(currentHistory.present)) {
        return currentHistory;
      }

      const newPast = [...currentHistory.past, currentHistory.present];
      
      // Limit history length
      if (newPast.length > MAX_HISTORY_LENGTH) {
        newPast.shift();
      }

      return {
        past: newPast,
        present: resolvedState,
        future: [], // Clear future when new state is set
      };
    });
  }, []);

  const undo = useCallback(() => {
    setHistory((currentHistory) => {
      if (currentHistory.past.length === 0) {
        return currentHistory;
      }

      const previous = currentHistory.past[currentHistory.past.length - 1];
      const newPast = currentHistory.past.slice(0, currentHistory.past.length - 1);

      return {
        past: newPast,
        present: previous,
        future: [currentHistory.present, ...currentHistory.future],
      };
    });
  }, []);

  const redo = useCallback(() => {
    setHistory((currentHistory) => {
      if (currentHistory.future.length === 0) {
        return currentHistory;
      }

      const next = currentHistory.future[0];
      const newFuture = currentHistory.future.slice(1);

      return {
        past: [...currentHistory.past, currentHistory.present],
        present: next,
        future: newFuture,
      };
    });
  }, []);

  const reset = useCallback((newState: T) => {
    setHistory({
      past: [],
      present: newState,
      future: [],
    });
  }, []);

  const clear = useCallback(() => {
    setHistory((currentHistory) => ({
      past: [],
      present: currentHistory.present,
      future: [],
    }));
  }, []);

  return {
    state: history.present,
    setState,
    undo,
    redo,
    canUndo: history.past.length > 0,
    canRedo: history.future.length > 0,
    reset,
    clear,
  };
}

/**
 * Hook for keyboard shortcuts for undo/redo
 * 
 * @param undo - Undo callback
 * @param redo - Redo callback
 * @param enabled - Whether shortcuts are enabled
 * 
 * @example
 * ```tsx
 * const { undo, redo } = useUndoRedo(initialState);
 * useUndoRedoShortcuts(undo, redo, true);
 * ```
 */
export function useUndoRedoShortcuts(
  undo: () => void,
  redo: () => void,
  enabled: boolean = true
) {
  const handleKeyDown = useCallback(
    (event: KeyboardEvent) => {
      if (!enabled) return;

      const isMac = navigator.platform.toUpperCase().indexOf('MAC') >= 0;
      const modifierKey = isMac ? event.metaKey : event.ctrlKey;

      if (modifierKey && event.key === 'z') {
        event.preventDefault();
        if (event.shiftKey) {
          redo();
        } else {
          undo();
        }
      } else if (modifierKey && event.key === 'y' && !isMac) {
        // Ctrl+Y for redo on Windows/Linux
        event.preventDefault();
        redo();
      }
    },
    [undo, redo, enabled]
  );

  // Set up keyboard event listener
  if (typeof window !== 'undefined') {
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }
}
