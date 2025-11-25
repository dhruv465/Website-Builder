import { apiClient, retryRequest } from './client';
import { Site, CodeGenerateRequest, CodeUpdateRequest } from '../types';
import { isSite } from '../utils/validators';

export interface CodeResponse {
  site_id: string;
  html_code: string;
  css_code?: string;
  js_code?: string;
  version_number: number;
}

/**
 * Generate code for a new site
 */
export async function generateCode(
  data: CodeGenerateRequest
): Promise<CodeResponse> {
  const response = await retryRequest(() =>
    apiClient.post<CodeResponse>('/api/code/generate', data)
  );
  
  return response.data;
}

/**
 * Update site code
 */
export async function updateCode(
  data: CodeUpdateRequest
): Promise<CodeResponse> {
  const response = await retryRequest(() =>
    apiClient.put<CodeResponse>('/api/code/update', data)
  );
  
  return response.data;
}

/**
 * Get site code by site ID
 */
export async function getSiteCode(siteId: string): Promise<Site> {
  const response = await retryRequest(() =>
    apiClient.get<Site>(`/api/code/${siteId}`)
  );
  
  if (!isSite(response.data)) {
    throw new Error('Invalid site response');
  }
  
  return response.data;
}
