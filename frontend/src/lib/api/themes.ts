import { apiClient } from './client';
import { Theme, ThemeCustomization } from '../types/theme';

/**
 * Fetch all available themes
 */
export async function fetchThemes(): Promise<Theme[]> {
  const response = await apiClient.get<Theme[]>('/api/themes');
  return response.data;
}

/**
 * Fetch a specific theme by ID
 */
export async function fetchThemeById(themeId: string): Promise<Theme> {
  const response = await apiClient.get<Theme>(`/api/themes/${themeId}`);
  return response.data;
}

/**
 * Apply a theme to a site
 */
export async function applyThemeToSite(
  siteId: string,
  themeId: string,
  customization?: ThemeCustomization
): Promise<{ success: boolean; message: string }> {
  const response = await apiClient.post(`/api/sites/${siteId}/theme`, {
    theme_id: themeId,
    customization,
  });
  return response.data;
}

/**
 * Save a custom theme
 */
export async function saveCustomTheme(theme: Theme): Promise<Theme> {
  const response = await apiClient.post<Theme>('/api/themes/custom', theme);
  return response.data;
}

/**
 * Get themes for a specific session
 */
export async function fetchSessionThemes(sessionId: string): Promise<Theme[]> {
  const response = await apiClient.get<Theme[]>(`/api/sessions/${sessionId}/themes`);
  return response.data;
}

/**
 * Delete a custom theme
 */
export async function deleteCustomTheme(themeId: string): Promise<void> {
  await apiClient.delete(`/api/themes/${themeId}`);
}
