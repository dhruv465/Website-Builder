import { apiClient, retryRequest } from './client';
import { WorkflowResponse, WorkflowState } from '../types';
import { isWorkflowResponse } from '../utils/validators';

export interface CreateWorkflowRequest {
  session_id: string;
  requirements: string;
  framework?: string;
  design_style?: string;
  features?: string[];
}

export interface UpdateWorkflowRequest {
  session_id: string;
  site_id: string;
  requirements: string;
  framework?: string;
  design_style?: string;
  changes?: string;
}

/**
 * Start CREATE_SITE workflow
 */
export async function createWorkflow(
  data: CreateWorkflowRequest
): Promise<WorkflowResponse> {
  const response = await retryRequest(() =>
    apiClient.post<WorkflowResponse>('/api/workflows/create', data)
  );
  
  if (!isWorkflowResponse(response.data)) {
    throw new Error('Invalid workflow response');
  }
  
  return response.data;
}

/**
 * Start UPDATE_SITE workflow
 */
export async function updateWorkflow(
  data: UpdateWorkflowRequest
): Promise<WorkflowResponse> {
  const response = await retryRequest(() =>
    apiClient.post<WorkflowResponse>('/api/workflows/update', data)
  );
  
  if (!isWorkflowResponse(response.data)) {
    throw new Error('Invalid workflow response');
  }
  
  return response.data;
}

/**
 * Get workflow status
 */
export async function getWorkflowStatus(
  workflowId: string
): Promise<WorkflowState> {
  const response = await retryRequest(() =>
    apiClient.get<WorkflowState>(`/api/workflows/${workflowId}/status`)
  );
  
  return response.data;
}

/**
 * Cancel workflow
 */
export async function cancelWorkflow(workflowId: string): Promise<void> {
  await retryRequest(() => apiClient.delete(`/api/workflows/${workflowId}`));
}
