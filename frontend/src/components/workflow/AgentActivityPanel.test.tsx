import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { AgentStatusCard } from './AgentStatusCard';
import { LogViewer } from './LogViewer';
import { ErrorAlert } from './ErrorAlert';
import type { AgentStatus, LogEntry } from '../../lib/types';
import { ErrorType } from '../../lib/types/api';

describe('AgentStatusCard', () => {
  const mockAgent: AgentStatus = {
    name: 'code_generation_agent',
    status: 'executing',
    progress: 50,
    startTime: '2024-01-01T12:00:00Z',
  };

  it('renders agent status card with executing status', () => {
    render(<AgentStatusCard agent={mockAgent} />);

    expect(screen.getByText('Code Generation Agent')).toBeInTheDocument();
    expect(screen.getByText('Executing')).toBeInTheDocument();
    expect(screen.getByText('50%')).toBeInTheDocument();
  });

  it('renders completed agent status', () => {
    const completedAgent: AgentStatus = {
      name: 'input_agent',
      status: 'completed',
      startTime: '2024-01-01T12:00:00Z',
      endTime: '2024-01-01T12:00:30Z',
    };

    render(<AgentStatusCard agent={completedAgent} />);

    expect(screen.getByText('Input Agent')).toBeInTheDocument();
    expect(screen.getByText('Completed')).toBeInTheDocument();
  });

  it('displays error message for failed agent', () => {
    const failedAgent: AgentStatus = {
      name: 'test_agent',
      status: 'failed',
      error: 'Test error message',
      startTime: '2024-01-01T12:00:00Z',
      endTime: '2024-01-01T12:00:30Z',
    };

    render(<AgentStatusCard agent={failedAgent} />);

    expect(screen.getByText('Test error message')).toBeInTheDocument();
  });
});

describe('LogViewer', () => {
  const mockLogs: LogEntry[] = [
    {
      timestamp: '2024-01-01T12:00:00.000Z',
      level: 'info',
      message: 'Starting workflow',
      agent: 'input_agent',
    },
    {
      timestamp: '2024-01-01T12:00:01.000Z',
      level: 'warning',
      message: 'Warning message',
      agent: 'code_generation_agent',
    },
    {
      timestamp: '2024-01-01T12:00:02.000Z',
      level: 'error',
      message: 'Error occurred',
      agent: 'deployment_agent',
    },
  ];

  it('renders log viewer with logs', () => {
    render(<LogViewer logs={mockLogs} />);

    expect(screen.getByText('Workflow Logs')).toBeInTheDocument();
    expect(screen.getByText('Starting workflow')).toBeInTheDocument();
    expect(screen.getByText('Warning message')).toBeInTheDocument();
    expect(screen.getByText('Error occurred')).toBeInTheDocument();
  });

  it('displays correct log count', () => {
    render(<LogViewer logs={mockLogs} />);

    expect(screen.getByText('3 / 3')).toBeInTheDocument();
  });

  it('shows empty state when no logs', () => {
    render(<LogViewer logs={[]} />);

    expect(screen.getByText('No logs yet')).toBeInTheDocument();
  });
});

describe('ErrorAlert', () => {
  it('renders error alert with message', () => {
    const error = {
      type: ErrorType.API_ERROR,
      message: 'Test error message',
      recoverable: true,
      retryable: true,
    };
    render(<ErrorAlert error={error} />);

    expect(screen.getByRole('alert')).toBeInTheDocument();
  });

  it('shows retry button when onRetry is provided and error is retryable', () => {
    const onRetry = () => {};
    const error = {
      type: ErrorType.API_ERROR,
      message: 'Test error',
      recoverable: true,
      retryable: true,
    };
    render(<ErrorAlert error={error} onRetry={onRetry} />);

    expect(screen.getByRole('button', { name: /retry/i })).toBeInTheDocument();
  });

  it('shows dismiss button when onDismiss is provided', () => {
    const onDismiss = () => {};
    const error = {
      type: ErrorType.API_ERROR,
      message: 'Test error',
      recoverable: true,
      retryable: false,
    };
    render(<ErrorAlert error={error} onDismiss={onDismiss} />);

    // The dismiss button is rendered as an X icon button
    const buttons = screen.getAllByRole('button');
    expect(buttons.length).toBeGreaterThan(0);
  });
});
