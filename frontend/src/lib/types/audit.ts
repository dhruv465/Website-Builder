// Audit-specific types (re-export from api.ts for convenience)

export type { Audit, CategoryScore, Issue } from './api';

export interface AuditRunRequest {
  site_id: string;
  categories?: ('seo' | 'accessibility' | 'performance')[];
}

export interface AuditExportFormat {
  format: 'json' | 'pdf';
  audit_id: string;
}
