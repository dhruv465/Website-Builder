import { apiClient, retryRequest } from './client';
import { Session, UserPreferences } from '../types';
import { isSession } from '../utils/validators';

/**
 * Create a new session
 */
export async function createSession(): Promise<Session> {
  const response = await retryRequest(() => apiClient.post<Session>('/api/sessions', {}));
  
  const data = response.data as any;
  const session = data.session || data;
  
  if (!isSession(session)) {
    throw new Error('Invalid session response');
  }
  
  return session;
}

/**
 * Get session by ID
 */
export async function getSession(sessionId: string): Promise<Session> {
  const response = await retryRequest(() =>
    apiClient.get<Session>(`/api/sessions/${sessionId}`)
  );
  
  const data = response.data as any;
  const session = data.session || data;
  
  if (!isSession(session)) {
    throw new Error('Invalid session response');
  }
  
  return session;
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
  
  const dataResponse = response.data as any;
  const session = dataResponse.session || dataResponse;
  
  if (!isSession(session)) {
    throw new Error('Invalid session response');
  }
  
  return session;
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
  
  const dataResponse = response.data as any;
  const session = dataResponse.session || dataResponse;
  
  if (!isSession(session)) {
    throw new Error('Invalid session response');
  }
  
  return session;
}

/**
 * Delete session
 */
export async function deleteSession(sessionId: string): Promise<void> {
  await retryRequest(() => apiClient.delete(`/api/sessions/${sessionId}`));
}
