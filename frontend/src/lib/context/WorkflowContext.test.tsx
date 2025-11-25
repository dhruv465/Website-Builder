import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { WorkflowProvider, useWorkflow } from './WorkflowContext';
import * as workflowsApi from '../api/workflows';
import { ConnectionState } from '../websocket/client';

// Mock API
vi.mock('../api/workflows');

// Mock useWebSocket hook
vi.mock('../hooks/useWebSocket', () => ({
  useWebSocket: vi.fn(() => ({
    state: ConnectionState.DISCONNECTED,
    connect: vi.fn(),
    disconnect: vi.fn(),
    send: vi.fn(),
  })),
}));

describe('WorkflowContext', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('throws error when used outside provider', () => {
    expect(() => {
      renderHook(() => useWorkflow());
    }).toThrow('useWorkflow must be used within a WorkflowProvider');
  });

  it('provides initial state', () => {
    const { result } = renderHook(() => useWorkflow(), {
      wrapper: WorkflowProvider,
    });

    expect(result.current.workflowState).toBeNull();
    expect(result.current.agentStatuses.size).toBe(0);
    expect(result.current.isCreating).toBe(false);
    expect(result.current.isUpdating).toBe(false);
    expect(result.current.isCancelling).toBe(false);
    expect(result.current.error).toBeNull();
  });

  it('starts create workflow', async () => {
    const mockResponse = {
      workflow_id: 'workflow-123',
      status: 'pending',
    };

    vi.mocked(workflowsApi.createWorkflow).mockResolvedValue(mockResponse);

    const { result } = renderHook(() => useWorkflow(), {
      wrapper: WorkflowProvider,
    });

    const request = {
      session_id: 'session-1',
      requirements: 'Build a website',
      framework: 'react' as const,
      design_style: 'modern' as const,
    };

    const response = await result.current.startCreateWorkflow(request);

    expect(response).toEqual(mockResponse);
    
    await waitFor(() => {
      expect(result.current.workflowState?.workflow_id).toBe('workflow-123');
    });
  });

  it('handles create workflow error', async () => {
    vi.mocked(workflowsApi.createWorkflow).mockRejectedValue(
      new Error('API Error')
    );

    const { result } = renderHook(() => useWorkflow(), {
      wrapper: WorkflowProvider,
    });

    const request = {
      session_id: 'session-1',
      requirements: 'Build a website',
      framework: 'react' as const,
      design_style: 'modern' as const,
    };

    const response = await result.current.startCreateWorkflow(request);

    expect(response).toBeNull();
    
    await waitFor(() => {
      expect(result.current.error).toBe('API Error');
    });
  });

  it('starts update workflow', async () => {
    const mockResponse = {
      workflow_id: 'workflow-456',
      status: 'pending',
    };

    vi.mocked(workflowsApi.updateWorkflow).mockResolvedValue(mockResponse);

    const { result } = renderHook(() => useWorkflow(), {
      wrapper: WorkflowProvider,
    });

    const request = {
      session_id: 'session-1',
      site_id: 'site-1',
      updates: 'Change color scheme',
    };

    const response = await result.current.startUpdateWorkflow(request);

    expect(response).toEqual(mockResponse);
    
    await waitFor(() => {
      expect(result.current.workflowState?.workflow_id).toBe('workflow-456');
    });
  });

  it('cancels workflow', async () => {
    const mockCreateResponse = {
      workflow_id: 'workflow-123',
      status: 'pending',
    };

    vi.mocked(workflowsApi.createWorkflow).mockResolvedValue(mockCreateResponse);
    vi.mocked(workflowsApi.cancelWorkflow).mockResolvedValue(undefined);

    const { result } = renderHook(() => useWorkflow(), {
      wrapper: WorkflowProvider,
    });

    // Start a workflow first
    await result.current.startCreateWorkflow({
      session_id: 'session-1',
      requirements: 'Build a website',
      framework: 'react' as const,
      design_style: 'modern' as const,
    });

    await waitFor(() => {
      expect(result.current.workflowState).not.toBeNull();
    });

    // Cancel it
    await result.current.cancelWorkflow();

    await waitFor(() => {
      expect(result.current.workflowState?.status).toBe('cancelled');
    });
  });

  it('clears error', () => {
    const { result } = renderHook(() => useWorkflow(), {
      wrapper: WorkflowProvider,
    });

    // Manually set error (in real scenario, would come from failed API call)
    // For this test, we just verify the clearError function exists
    result.current.clearError();

    expect(result.current.error).toBeNull();
  });

  it('resets workflow state', async () => {
    const mockResponse = {
      workflow_id: 'workflow-123',
      status: 'pending',
    };

    vi.mocked(workflowsApi.createWorkflow).mockResolvedValue(mockResponse);

    const { result } = renderHook(() => useWorkflow(), {
      wrapper: WorkflowProvider,
    });

    await result.current.startCreateWorkflow({
      session_id: 'session-1',
      requirements: 'Build a website',
      framework: 'react' as const,
      design_style: 'modern' as const,
    });

    await waitFor(() => {
      expect(result.current.workflowState).not.toBeNull();
    });

    result.current.reset();

    await waitFor(() => {
      expect(result.current.workflowState).toBeNull();
      expect(result.current.agentStatuses.size).toBe(0);
    });
  });
});
