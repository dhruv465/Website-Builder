import {
  Session,
  Site,
  Audit,
  Deployment,
  WorkflowResponse,
  WebSocketMessage,
} from '../types';

/**
 * Type guard for Session
 */
export function isSession(obj: any): obj is Session {
  return (
    obj &&
    typeof obj === 'object' &&
    typeof obj.id === 'string' &&
    typeof obj.created_at === 'string' &&
    typeof obj.last_accessed_at === 'string' &&
    typeof obj.preferences === 'object' &&
    Array.isArray(obj.sites)
  );
}

/**
 * Type guard for Site
 */
export function isSite(obj: any): obj is Site {
  return (
    obj &&
    typeof obj === 'object' &&
    typeof obj.id === 'string' &&
    typeof obj.session_id === 'string' &&
    typeof obj.name === 'string' &&
    typeof obj.framework === 'string' &&
    typeof obj.design_style === 'string' &&
    typeof obj.created_at === 'string' &&
    typeof obj.updated_at === 'string' &&
    Array.isArray(obj.versions) &&
    Array.isArray(obj.audits) &&
    Array.isArray(obj.deployments)
  );
}

/**
 * Type guard for Audit
 */
export function isAudit(obj: any): obj is Audit {
  return (
    obj &&
    typeof obj === 'object' &&
    typeof obj.id === 'string' &&
    typeof obj.site_id === 'string' &&
    typeof obj.timestamp === 'string' &&
    typeof obj.seo === 'object' &&
    typeof obj.accessibility === 'object' &&
    typeof obj.performance === 'object' &&
    typeof obj.overall_score === 'number'
  );
}

/**
 * Type guard for Deployment
 */
export function isDeployment(obj: any): obj is Deployment {
  return (
    obj &&
    typeof obj === 'object' &&
    typeof obj.id === 'string' &&
    typeof obj.site_id === 'string' &&
    typeof obj.url === 'string' &&
    typeof obj.status === 'string' &&
    typeof obj.platform === 'string' &&
    typeof obj.created_at === 'string'
  );
}

/**
 * Type guard for WorkflowResponse
 */
export function isWorkflowResponse(obj: any): obj is WorkflowResponse {
  return (
    obj &&
    typeof obj === 'object' &&
    typeof obj.workflow_id === 'string' &&
    typeof obj.status === 'string'
  );
}

/**
 * Type guard for WebSocketMessage
 */
export function isWebSocketMessage(obj: any): obj is WebSocketMessage {
  return obj && typeof obj === 'object' && typeof obj.type === 'string';
}

/**
 * Validate email format
 */
export function isValidEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

/**
 * Validate URL format
 */
export function isValidUrl(url: string): boolean {
  try {
    new URL(url);
    return true;
  } catch {
    return false;
  }
}

/**
 * Validate UUID format
 */
export function isValidUuid(uuid: string): boolean {
  const uuidRegex =
    /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
  return uuidRegex.test(uuid);
}
