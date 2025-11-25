// Deployment-related types

export interface DeploymentConfig {
  platform: 'vercel';
  projectName?: string;
  environmentVariables?: Record<string, string>;
  buildCommand?: string;
  outputDirectory?: string;
}

export interface DeploymentLogEntry {
  timestamp: string;
  level: 'info' | 'warning' | 'error';
  message: string;
  metadata?: Record<string, any>;
}

export interface DeploymentProgress {
  stage: 'initializing' | 'building' | 'deploying' | 'finalizing' | 'complete' | 'failed';
  progress: number;
  message: string;
}

// WebSocket message types for deployment
export type DeploymentWebSocketMessage =
  | { type: 'deployment.status'; deployment_id: string; status: string; progress?: number }
  | { type: 'deployment.log'; deployment_id: string; log: DeploymentLogEntry }
  | { type: 'deployment.complete'; deployment_id: string; url: string }
  | { type: 'deployment.error'; deployment_id: string; error: string };
