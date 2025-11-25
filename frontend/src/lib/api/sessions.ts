import { apiClient, retryRequest } from './client';
import { Session, UserPreferences } from '../types';
import { isSession } from '../utils/validators';

/**
 * Create a new session
 */
export async function createSession(): Promise<Session> {
  const response = await retryRequest(() => apiClient.post<Session>('/api/sessions'));
  
  if (!isSession(response.data)) {
    throw new Error('Invalid session response');
  }
  
  return response.data;
}

/**
 * Get session by ID
 */
export async function getSession(sessionId: string): Promise<Session> {
  const response = await retryRequest(() =>
    apiClient.get<Session>(`/api/sessions/${sessionId}`)
  );
  
  if (!isSession(response.data)) {
    throw new Error('Invalid session response');
  }
  
  return response.data;
}

/**
 * Update session
 */
export async function updateSession(
  sessionId: string,
  data: Partial<Session>
): Promise<Session> {
  const response = await retryRequest(() =>
    apiClient.put<Session>(`/api/sessions/${sessionId}`, data)
  );
  
  if (!isSession(response.data)) {
    throw new Error('Invalid session response');
  }
  
  return response.data;
}

/**
 * Update session preferences
 */
export async function updateSessionPreferences(
  sessionId: string,
  preferences: UserPreferences
): Promise<Session> {
  const response = await retryRequest(() =>
    apiClient.put<Session>(`/api/sessions/${sessionId}/preferences`, preferences)
  );
  
  if (!isSession(response.data)) {
    throw new Error('Invalid session response');
  }
  
  return response.data;
}

/**
 * Delete session
 */
export async function deleteSession(sessionId: string): Promise<void> {
  await retryRequest(() => apiClient.delete(`/api/sessions/${sessionId}`));
}
