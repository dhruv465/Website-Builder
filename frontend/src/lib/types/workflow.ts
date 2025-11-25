// Workflow-related types

export interface WorkflowResponse {
  workflow_id: string;
  status: string;
  result?: any;
  error?: string;
  metrics?: WorkflowMetrics;
}

export interface WorkflowMetrics {
  total_duration: number;
  agent_durations: Record<string, number>;
  llm_calls: number;
  llm_tokens_used: number;
  error_count: number;
  retry_count: number;
}

export interface WorkflowState {
  workflow_id: string;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
  current_agent?: string;
  completed_agents: string[];
  progress_percentage: number;
  logs: LogEntry[];
}

export interface AgentStatus {
  name: string;
  status: 'pending' | 'executing' | 'completed' | 'failed';
  progress?: number;
  startTime?: string;
  endTime?: string;
  error?: string;
}

export interface LogEntry {
  timestamp: string;
  level: 'info' | 'warning' | 'error';
  message: string;
  agent: string;
  metadata?: Record<string, any>;
}

// WebSocket message types
export type WebSocketMessage =
  | { type: 'pong' }
  | { type: 'workflow.status'; data: WorkflowState }
  | { type: 'workflow.complete'; data: any }
  | { type: 'workflow.error'; error: string }
  | { type: 'agent.status'; agent: string; status: string; metadata?: any }
  | { type: 'log.entry'; log: LogEntry };

export type WebSocketCommand =
  | { type: 'ping' }
  | { type: 'workflow.cancel'; workflow_id: string };
