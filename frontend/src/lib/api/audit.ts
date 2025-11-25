import { apiClient, retryRequest } from './client';
import { Audit, AuditRunRequest } from '../types';
import { isAudit } from '../utils/validators';

/**
 * Run audit for a site
 */
export async function runAudit(data: AuditRunRequest): Promise<Audit> {
  const response = await retryRequest(() =>
    apiClient.post<Audit>('/api/audit/run', data)
  );
  
  if (!isAudit(response.data)) {
    throw new Error('Invalid audit response');
  }
  
  return response.data;
}

/**
 * Get audit by ID
 */
export async function getAudit(auditId: string): Promise<Audit> {
  const response = await retryRequest(() =>
    apiClient.get<Audit>(`/api/audit/${auditId}`)
  );
  
  if (!isAudit(response.data)) {
    throw new Error('Invalid audit response');
  }
  
  return response.data;
}

/**
 * Get all audits for a site
 */
export async function getSiteAudits(siteId: string): Promise<Audit[]> {
  const response = await retryRequest(() =>
    apiClient.get<Audit[]>(`/api/audit/site/${siteId}`)
  );
  
  if (!Array.isArray(response.data)) {
    throw new Error('Invalid audits response');
  }
  
  return response.data;
}
