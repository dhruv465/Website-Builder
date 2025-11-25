import { useState, useEffect, useCallback } from 'react';
import { Theme } from '../types/theme';
import { mockThemes } from '../data/mockThemes';
import { applyThemeToDocument } from '../utils/themeUtils';
import { useLocalStorage } from './useLocalStorage';

interface UseThemeReturn {
  themes: Theme[];
  selectedTheme: Theme | null;
  isLoading: boolean;
  error: Error | null;
  selectTheme: (theme: Theme) => void;
  applyTheme: (theme: Theme) => Promise<void>;
  clearTheme: () => void;
}

/**
 * Custom hook for theme management
 */
export function useTheme(): UseThemeReturn {
  const [themes, setThemes] = useState<Theme[]>([]);
  const [selectedTheme, setSelectedTheme] = useLocalStorage<Theme | null>('selected-theme', null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  // Load themes on mount
  useEffect(() => {
    const loadThemes = async () => {
      try {
        setIsLoading(true);
        // In production, this would fetch from API
        // const fetchedThemes = await fetchThemes();
        // For now, use mock data
        setThemes(mockThemes);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err : new Error('Failed to load themes'));
      } finally {
        setIsLoading(false);
      }
    };

    loadThemes();
  }, []);

  // Apply selected theme on mount if exists
  useEffect(() => {
    if (selectedTheme) {
      applyThemeToDocument(selectedTheme);
    }
  }, [selectedTheme]);

  const selectTheme = useCallback((theme: Theme) => {
    setSelectedTheme(theme);
  }, [setSelectedTheme]);

  const applyTheme = useCallback(async (theme: Theme) => {
    try {
      // Apply theme to document
      applyThemeToDocument(theme);
      
      // Save as selected theme
      setSelectedTheme(theme);
      
      // In production, this would also call the API to save the theme preference
      // await applyThemeToSite(siteId, theme.id);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Failed to apply theme'));
      throw err;
    }
  }, [setSelectedTheme]);

  const clearTheme = useCallback(() => {
    setSelectedTheme(null);
  }, [setSelectedTheme]);

  return {
    themes,
    selectedTheme,
    isLoading,
    error,
    selectTheme,
    applyTheme,
    clearTheme,
  };
}
