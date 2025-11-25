import { apiClient, retryRequest } from './client';
import { Deployment } from '../types';
import { isDeployment } from '../utils/validators';

export interface DeployRequest {
  site_id: string;
  platform: 'vercel';
  config?: Record<string, any>;
}

/**
 * Deploy site to Vercel
 */
export async function deployToVercel(
  data: DeployRequest
): Promise<Deployment> {
  const response = await retryRequest(() =>
    apiClient.post<Deployment>('/api/deploy/vercel', data)
  );
  
  if (!isDeployment(response.data)) {
    throw new Error('Invalid deployment response');
  }
  
  return response.data;
}

/**
 * Get deployment status
 */
export async function getDeploymentStatus(
  deploymentId: string
): Promise<Deployment> {
  const response = await retryRequest(() =>
    apiClient.get<Deployment>(`/api/deploy/${deploymentId}`)
  );
  
  if (!isDeployment(response.data)) {
    throw new Error('Invalid deployment response');
  }
  
  return response.data;
}

/**
 * Get all deployments for a site
 */
export async function getSiteDeployments(siteId: string): Promise<Deployment[]> {
  const response = await retryRequest(() =>
    apiClient.get<Deployment[]>(`/api/deploy/site/${siteId}`)
  );
  
  if (!Array.isArray(response.data)) {
    throw new Error('Invalid deployments response');
  }
  
  return response.data;
}
