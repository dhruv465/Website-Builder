import { describe, it, expect } from 'vitest';
import {
  isSession,
  isSite,
  isAudit,
  isDeployment,
  isWorkflowResponse,
  isWebSocketMessage,
  isValidEmail,
  isValidUrl,
  isValidUuid,
} from './validators';

describe('Validator Utilities', () => {
  describe('isSession', () => {
    it('validates correct session object', () => {
      const session = {
        id: 'session-1',
        created_at: '2024-01-01T00:00:00Z',
        last_accessed_at: '2024-01-01T00:00:00Z',
        preferences: {},
        sites: [],
      };

      expect(isSession(session)).toBe(true);
    });

    it('rejects invalid session object', () => {
      const invalid = {
        id: 'session-1',
        created_at: '2024-01-01T00:00:00Z',
      };

      expect(isSession(invalid)).toBe(false);
    });

    it('rejects null', () => {
      expect(isSession(null)).toBeFalsy();
    });

    it('rejects non-object', () => {
      expect(isSession('string')).toBe(false);
    });
  });

  describe('isSite', () => {
    it('validates correct site object', () => {
      const site = {
        id: 'site-1',
        session_id: 'session-1',
        name: 'My Site',
        framework: 'react',
        design_style: 'modern',
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
        versions: [],
        audits: [],
        deployments: [],
      };

      expect(isSite(site)).toBe(true);
    });

    it('rejects invalid site object', () => {
      const invalid = {
        id: 'site-1',
        name: 'My Site',
      };

      expect(isSite(invalid)).toBe(false);
    });
  });

  describe('isAudit', () => {
    it('validates correct audit object', () => {
      const audit = {
        id: 'audit-1',
        site_id: 'site-1',
        timestamp: '2024-01-01T00:00:00Z',
        seo: { score: 85, issues: [], passed_checks: 8, total_checks: 10 },
        accessibility: { score: 90, issues: [], passed_checks: 9, total_checks: 10 },
        performance: { score: 80, issues: [], passed_checks: 8, total_checks: 10 },
        overall_score: 85,
      };

      expect(isAudit(audit)).toBe(true);
    });

    it('rejects invalid audit object', () => {
      const invalid = {
        id: 'audit-1',
        site_id: 'site-1',
      };

      expect(isAudit(invalid)).toBe(false);
    });
  });

  describe('isDeployment', () => {
    it('validates correct deployment object', () => {
      const deployment = {
        id: 'deploy-1',
        site_id: 'site-1',
        url: 'https://example.com',
        status: 'success',
        platform: 'vercel',
        created_at: '2024-01-01T00:00:00Z',
      };

      expect(isDeployment(deployment)).toBe(true);
    });

    it('rejects invalid deployment object', () => {
      const invalid = {
        id: 'deploy-1',
        url: 'https://example.com',
      };

      expect(isDeployment(invalid)).toBe(false);
    });
  });

  describe('isWorkflowResponse', () => {
    it('validates correct workflow response', () => {
      const response = {
        workflow_id: 'workflow-1',
        status: 'running',
      };

      expect(isWorkflowResponse(response)).toBe(true);
    });

    it('rejects invalid workflow response', () => {
      const invalid = {
        workflow_id: 'workflow-1',
      };

      expect(isWorkflowResponse(invalid)).toBe(false);
    });
  });

  describe('isWebSocketMessage', () => {
    it('validates correct WebSocket message', () => {
      const message = {
        type: 'workflow.status',
        data: {},
      };

      expect(isWebSocketMessage(message)).toBe(true);
    });

    it('rejects invalid WebSocket message', () => {
      const invalid = {
        data: {},
      };

      expect(isWebSocketMessage(invalid)).toBe(false);
    });
  });

  describe('isValidEmail', () => {
    it('validates correct email addresses', () => {
      expect(isValidEmail('test@example.com')).toBe(true);
      expect(isValidEmail('user.name@domain.co.uk')).toBe(true);
      expect(isValidEmail('user+tag@example.com')).toBe(true);
    });

    it('rejects invalid email addresses', () => {
      expect(isValidEmail('invalid')).toBe(false);
      expect(isValidEmail('invalid@')).toBe(false);
      expect(isValidEmail('@example.com')).toBe(false);
      expect(isValidEmail('invalid@domain')).toBe(false);
    });
  });

  describe('isValidUrl', () => {
    it('validates correct URLs', () => {
      expect(isValidUrl('https://example.com')).toBe(true);
      expect(isValidUrl('http://localhost:3000')).toBe(true);
      expect(isValidUrl('https://sub.domain.com/path?query=value')).toBe(true);
    });

    it('rejects invalid URLs', () => {
      expect(isValidUrl('invalid')).toBe(false);
      expect(isValidUrl('not a url')).toBe(false);
      expect(isValidUrl('//example.com')).toBe(false);
    });
  });

  describe('isValidUuid', () => {
    it('validates correct UUIDs', () => {
      expect(isValidUuid('123e4567-e89b-12d3-a456-426614174000')).toBe(true);
      expect(isValidUuid('550e8400-e29b-41d4-a716-446655440000')).toBe(true);
    });

    it('rejects invalid UUIDs', () => {
      expect(isValidUuid('invalid')).toBe(false);
      expect(isValidUuid('123-456-789')).toBe(false);
      expect(isValidUuid('123e4567-e89b-12d3-a456')).toBe(false);
    });
  });
});
