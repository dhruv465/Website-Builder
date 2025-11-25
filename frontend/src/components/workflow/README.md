# Workflow Components

This directory contains components for workflow execution and monitoring.

## Components

### AgentActivityPanel

Main component that displays real-time workflow execution status with agent activities and logs.

**Features:**
- Real-time workflow status updates via WebSocket
- Overall progress tracking with percentage and estimated time
- Agent status cards showing individual agent progress
- Tabbed interface for agents and logs
- Workflow cancellation functionality
- Error handling with retry options
- Connection state indicator

**Usage:**
```tsx
import { AgentActivityPanel } from '@/components/workflow';
import { WorkflowProvider } from '@/lib/context';

function MyComponent() {
  return (
    <WorkflowProvider>
      <AgentActivityPanel
        onCancel={() => console.log('Workflow cancelled')}
        showLogs={true}
      />
    </WorkflowProvider>
  );
}
```

**Props:**
- `onCancel?: () => void` - Callback when workflow is cancelled
- `showLogs?: boolean` - Whether to show logs tab (default: true)
- `className?: string` - Additional CSS classes

### AgentStatusCard

Displays the status of an individual agent with progress, duration, and error information.

**Features:**
- Status indicator icon (pending, executing, completed, failed)
- Status badge with color coding
- Progress bar for executing agents
- Duration tracking
- Error message display
- Start/end timestamps

**Usage:**
```tsx
import { AgentStatusCard } from '@/components/workflow';

const agent = {
  name: 'code_generation_agent',
  status: 'executing',
  progress: 65,
  startTime: '2024-01-01T12:00:00Z',
};

<AgentStatusCard agent={agent} />
```

**Props:**
- `agent: AgentStatus` - Agent status object

### LogViewer

Scrollable log viewer with filtering and search capabilities.

**Features:**
- Real-time log display with auto-scroll
- Search functionality
- Level filtering (info, warning, error)
- Agent filtering
- Log export to text file
- Syntax highlighting by log level
- Timestamp formatting

**Usage:**
```tsx
import { LogViewer } from '@/components/workflow';

const logs = [
  {
    timestamp: '2024-01-01T12:00:00Z',
    level: 'info',
    message: 'Starting workflow',
    agent: 'input_agent',
  },
];

<LogViewer
  logs={logs}
  maxHeight="400px"
  autoScroll={true}
/>
```

**Props:**
- `logs: LogEntry[]` - Array of log entries
- `maxHeight?: string` - Maximum height of log viewer (default: '400px')
- `autoScroll?: boolean` - Auto-scroll to bottom on new logs (default: true)

### ErrorAlert

Alert component for displaying workflow errors with retry and dismiss actions.

**Features:**
- Destructive alert styling
- Error message display
- Retry button with loading state
- Dismiss button
- Customizable labels

**Usage:**
```tsx
import { ErrorAlert } from '@/components/workflow';

<ErrorAlert
  error="Failed to connect to backend"
  onRetry={() => console.log('Retrying...')}
  onDismiss={() => console.log('Dismissed')}
  isRetrying={false}
/>
```

**Props:**
- `error: string` - Error message to display
- `onRetry?: () => void` - Callback for retry action
- `onDismiss?: () => void` - Callback for dismiss action
- `retryLabel?: string` - Label for retry button (default: 'Retry')
- `dismissLabel?: string` - Label for dismiss button (default: 'Dismiss')
- `isRetrying?: boolean` - Whether retry is in progress (default: false)

## Context

### WorkflowContext

React Context for managing workflow state and WebSocket connections.

**Features:**
- Workflow creation and submission
- Real-time WebSocket updates
- Agent status tracking
- Log aggregation
- Workflow cancellation
- Error handling

**Usage:**
```tsx
import { WorkflowProvider, useWorkflow } from '@/lib/context';

// Wrap your app with WorkflowProvider
function App() {
  return (
    <WorkflowProvider>
      <YourComponents />
    </WorkflowProvider>
  );
}

// Use the workflow context in components
function MyComponent() {
  const {
    workflowState,
    agentStatuses,
    startCreateWorkflow,
    cancelWorkflow,
  } = useWorkflow();

  const handleCreate = async () => {
    const response = await startCreateWorkflow({
      session_id: 'session-123',
      requirements: 'Create a landing page',
      framework: 'react',
    });
    
    if (response) {
      console.log('Workflow started:', response.workflow_id);
    }
  };

  return (
    <div>
      <button onClick={handleCreate}>Start Workflow</button>
      {workflowState && (
        <p>Status: {workflowState.status}</p>
      )}
    </div>
  );
}
```

## WebSocket Integration

The workflow components use WebSocket for real-time updates. The WebSocket client automatically:
- Connects when a workflow is started
- Handles reconnection with exponential backoff
- Sends heartbeat pings to keep connection alive
- Processes incoming messages (workflow status, agent status, logs)
- Disconnects when workflow completes or is cancelled

## Type Definitions

All workflow-related types are defined in `src/lib/types/workflow.ts`:

- `WorkflowState` - Current workflow state
- `AgentStatus` - Individual agent status
- `LogEntry` - Log entry structure
- `WebSocketMessage` - Incoming WebSocket messages
- `WebSocketCommand` - Outgoing WebSocket commands

## Styling

All components use ShadCN UI components and Tailwind CSS for styling. They support:
- Dark mode via next-themes
- Responsive design
- Accessibility features (ARIA labels, keyboard navigation)
- Smooth animations with Framer Motion

## Testing

Test the workflow components with:

```bash
npm run test
```

Example test:
```tsx
import { render, screen } from '@testing-library/react';
import { AgentStatusCard } from './AgentStatusCard';

test('renders agent status card', () => {
  const agent = {
    name: 'test_agent',
    status: 'executing',
    progress: 50,
  };
  
  render(<AgentStatusCard agent={agent} />);
  expect(screen.getByText('Test Agent')).toBeInTheDocument();
  expect(screen.getByText('50%')).toBeInTheDocument();
});
```
