import React, { createContext, useContext, useState, useCallback, useEffect } from 'react';
import { useWebSocket } from '../hooks/useWebSocket';
import { createWorkflow, updateWorkflow, cancelWorkflow as cancelWorkflowApi } from '../api/workflows';
import type {
  WorkflowResponse,
  WorkflowState,
  AgentStatus,
  LogEntry,
  WebSocketMessage,
  CreateWorkflowRequest,
  UpdateWorkflowRequest,
} from '../types';
import { ConnectionState } from '../websocket/client';

interface WorkflowContextValue {
  // Current workflow state
  workflowState: WorkflowState | null;
  
  // Agent statuses
  agentStatuses: Map<string, AgentStatus>;
  
  // Connection state
  connectionState: ConnectionState;
  
  // Loading states
  isCreating: boolean;
  isUpdating: boolean;
  isCancelling: boolean;
  
  // Error state
  error: string | null;
  
  // Actions
  startCreateWorkflow: (request: CreateWorkflowRequest) => Promise<WorkflowResponse | null>;
  startUpdateWorkflow: (request: UpdateWorkflowRequest) => Promise<WorkflowResponse | null>;
  cancelWorkflow: () => Promise<void>;
  clearError: () => void;
  reset: () => void;
}

const WorkflowContext = createContext<WorkflowContextValue | undefined>(undefined);

interface WorkflowProviderProps {
  children: React.ReactNode;
}

export function WorkflowProvider({ children }: WorkflowProviderProps) {
  const [workflowState, setWorkflowState] = useState<WorkflowState | null>(null);
  const [agentStatuses, setAgentStatuses] = useState<Map<string, AgentStatus>>(new Map());
  const [isCreating, setIsCreating] = useState(false);
  const [isUpdating, setIsUpdating] = useState(false);
  const [isCancelling, setIsCancelling] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // WebSocket connection
  const { state: connectionState, connect, disconnect, send } = useWebSocket({
    onMessage: handleWebSocketMessage,
  });

  // Handle incoming WebSocket messages
  function handleWebSocketMessage(message: WebSocketMessage) {
    switch (message.type) {
      case 'workflow.status':
        setWorkflowState(message.data);
        break;

      case 'workflow.complete':
        if (workflowState) {
          setWorkflowState({
            ...workflowState,
            status: 'completed',
            progress_percentage: 100,
          });
        }
        break;

      case 'workflow.error':
        setError(message.error);
        if (workflowState) {
          setWorkflowState({
            ...workflowState,
            status: 'failed',
          });
        }
        break;

      case 'agent.status':
        updateAgentStatus(message.agent, message.status, message.metadata);
        break;

      case 'log.entry':
        addLogEntry(message.log);
        break;

      case 'pong':
        // Heartbeat response - no action needed
        break;
    }
  }

  // Update agent status
  function updateAgentStatus(agentName: string, status: string, metadata?: any) {
    setAgentStatuses((prev) => {
      const newMap = new Map(prev);
      const existing = newMap.get(agentName);
      
      const agentStatus: AgentStatus = {
        name: agentName,
        status: status as AgentStatus['status'],
        progress: metadata?.progress,
        startTime: existing?.startTime || (status === 'executing' ? new Date().toISOString() : undefined),
        endTime: status === 'completed' || status === 'failed' ? new Date().toISOString() : undefined,
        error: metadata?.error,
      };
      
      newMap.set(agentName, agentStatus);
      return newMap;
    });
  }

  // Add log entry to workflow state
  function addLogEntry(log: LogEntry) {
    setWorkflowState((prev) => {
      if (!prev) return prev;
      
      return {
        ...prev,
        logs: [...prev.logs, log],
      };
    });
  }

  // Start CREATE_SITE workflow
  const startCreateWorkflow = useCallback(
    async (request: CreateWorkflowRequest): Promise<WorkflowResponse | null> => {
      setIsCreating(true);
      setError(null);
      
      try {
        const response = await createWorkflow(request);
        
        // Initialize workflow state
        setWorkflowState({
          workflow_id: response.workflow_id,
          status: 'pending',
          completed_agents: [],
          progress_percentage: 0,
          logs: [],
        });
        
        // Connect to WebSocket for real-time updates
        connect(response.workflow_id);
        
        return response;
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Failed to create workflow';
        setError(errorMessage);
        return null;
      } finally {
        setIsCreating(false);
      }
    },
    [connect]
  );

  // Start UPDATE_SITE workflow
  const startUpdateWorkflow = useCallback(
    async (request: UpdateWorkflowRequest): Promise<WorkflowResponse | null> => {
      setIsUpdating(true);
      setError(null);
      
      try {
        const response = await updateWorkflow(request);
        
        // Initialize workflow state
        setWorkflowState({
          workflow_id: response.workflow_id,
          status: 'pending',
          completed_agents: [],
          progress_percentage: 0,
          logs: [],
        });
        
        // Connect to WebSocket for real-time updates
        connect(response.workflow_id);
        
        return response;
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Failed to update workflow';
        setError(errorMessage);
        return null;
      } finally {
        setIsUpdating(false);
      }
    },
    [connect]
  );

  // Cancel workflow
  const cancelWorkflow = useCallback(async () => {
    if (!workflowState?.workflow_id) return;
    
    setIsCancelling(true);
    
    try {
      // Send cancel command via WebSocket
      send({ type: 'workflow.cancel', workflow_id: workflowState.workflow_id });
      
      // Also call API endpoint
      await cancelWorkflowApi(workflowState.workflow_id);
      
      // Update local state
      setWorkflowState((prev) => {
        if (!prev) return prev;
        return {
          ...prev,
          status: 'cancelled',
        };
      });
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to cancel workflow';
      setError(errorMessage);
    } finally {
      setIsCancelling(false);
    }
  }, [workflowState?.workflow_id, send]);

  // Clear error
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  // Reset workflow state
  const reset = useCallback(() => {
    setWorkflowState(null);
    setAgentStatuses(new Map());
    setError(null);
    disconnect();
  }, [disconnect]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      disconnect();
    };
  }, [disconnect]);

  const value: WorkflowContextValue = {
    workflowState,
    agentStatuses,
    connectionState,
    isCreating,
    isUpdating,
    isCancelling,
    error,
    startCreateWorkflow,
    startUpdateWorkflow,
    cancelWorkflow,
    clearError,
    reset,
  };

  return <WorkflowContext.Provider value={value}>{children}</WorkflowContext.Provider>;
}

/**
 * Hook to access workflow context
 */
export function useWorkflow() {
  const context = useContext(WorkflowContext);
  
  if (context === undefined) {
    throw new Error('useWorkflow must be used within a WorkflowProvider');
  }
  
  return context;
}
