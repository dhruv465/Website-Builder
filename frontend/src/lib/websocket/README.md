# WebSocket Client

This module provides a robust WebSocket client with automatic reconnection, heartbeat mechanism, and React hooks for easy integration.

## Features

- **Automatic Reconnection**: Exponential backoff strategy with configurable max attempts
- **Heartbeat/Ping Mechanism**: Keeps connection alive and detects dead connections
- **Type-Safe Messages**: Full TypeScript support for message types
- **Event Emitter Pattern**: Subscribe to messages and state changes
- **Connection State Management**: Track connection status (connecting, connected, disconnected, error)
- **React Hook**: Easy integration with React components

## Usage

### Using the React Hook (Recommended)

```tsx
import { useWebSocket } from '@/lib/hooks/useWebSocket';
import { useEffect } from 'react';

function WorkflowMonitor({ workflowId }: { workflowId: string }) {
  const { state, isConnected, connect, disconnect, send, lastMessage } = useWebSocket({
    onMessage: (message) => {
      console.log('Received message:', message);
      
      // Handle different message types
      switch (message.type) {
        case 'workflow.status':
          console.log('Workflow status:', message.data);
          break;
        case 'workflow.complete':
          console.log('Workflow completed:', message.data);
          break;
        case 'workflow.error':
          console.error('Workflow error:', message.error);
          break;
        case 'agent.status':
          console.log('Agent status:', message.agent, message.status);
          break;
        case 'log.entry':
          console.log('Log:', message.log);
          break;
      }
    },
    onStateChange: (state) => {
      console.log('Connection state:', state);
    }
  });

  // Connect on mount, disconnect on unmount
  useEffect(() => {
    connect(workflowId);
    return () => disconnect();
  }, [workflowId, connect, disconnect]);

  // Cancel workflow
  const handleCancel = () => {
    send({ type: 'workflow.cancel', workflow_id: workflowId });
  };

  return (
    <div>
      <p>Connection Status: {state}</p>
      <p>Connected: {isConnected ? 'Yes' : 'No'}</p>
      {lastMessage && (
        <p>Last Message: {lastMessage.type}</p>
      )}
      <button onClick={handleCancel} disabled={!isConnected}>
        Cancel Workflow
      </button>
    </div>
  );
}
```

### Using the WebSocket Client Directly

```typescript
import { WebSocketClient, ConnectionState } from '@/lib/websocket';

// Create client instance
const client = new WebSocketClient('ws://localhost:8000');

// Subscribe to messages
const unsubscribeMessages = client.subscribe((message) => {
  console.log('Received:', message);
});

// Subscribe to state changes
const unsubscribeState = client.onStateChange((state) => {
  console.log('State:', state);
  
  if (state === ConnectionState.CONNECTED) {
    console.log('Connected!');
  }
});

// Connect to a workflow
client.connect('workflow-123');

// Send a command
client.send({ type: 'ping' });

// Cancel a workflow
client.send({ 
  type: 'workflow.cancel', 
  workflow_id: 'workflow-123' 
});

// Check connection status
if (client.isConnected()) {
  console.log('WebSocket is connected');
}

// Disconnect
client.disconnect();

// Clean up subscriptions
unsubscribeMessages();
unsubscribeState();
```

## Message Types

### Incoming Messages (from server)

```typescript
type WebSocketMessage =
  | { type: 'pong' }
  | { type: 'workflow.status'; data: WorkflowState }
  | { type: 'workflow.complete'; data: any }
  | { type: 'workflow.error'; error: string }
  | { type: 'agent.status'; agent: string; status: string; metadata?: any }
  | { type: 'log.entry'; log: LogEntry };
```

### Outgoing Commands (to server)

```typescript
type WebSocketCommand =
  | { type: 'ping' }
  | { type: 'workflow.cancel'; workflow_id: string };
```

## Connection States

```typescript
enum ConnectionState {
  CONNECTING = 'connecting',
  CONNECTED = 'connected',
  DISCONNECTED = 'disconnected',
  ERROR = 'error',
}
```

## Configuration

### Environment Variables

```env
VITE_WS_URL=ws://localhost:8000
```

### Reconnection Settings

The client uses exponential backoff for reconnection:
- Max attempts: 5
- Initial delay: 2 seconds
- Max delay: 30 seconds
- Formula: `Math.min(1000 * Math.pow(2, attempts), 30000)`

### Heartbeat Settings

- Ping interval: 30 seconds
- Pong timeout: 10 seconds

## Advanced Usage

### Multiple Subscriptions

```typescript
const { subscribe } = useWebSocket();

useEffect(() => {
  // Subscribe to workflow updates
  const unsubscribe1 = subscribe((message) => {
    if (message.type === 'workflow.status') {
      updateWorkflowState(message.data);
    }
  });

  // Subscribe to logs
  const unsubscribe2 = subscribe((message) => {
    if (message.type === 'log.entry') {
      addLog(message.log);
    }
  });

  return () => {
    unsubscribe1();
    unsubscribe2();
  };
}, [subscribe]);
```

### Manual Reconnection

```typescript
const client = new WebSocketClient('ws://localhost:8000');

// Reset reconnection attempts before manual reconnect
client.resetReconnectAttempts();
client.connect('workflow-123');
```

## Error Handling

The WebSocket client handles errors gracefully:

1. **Connection Errors**: Automatically attempts to reconnect
2. **Message Parse Errors**: Logs error and continues
3. **Handler Errors**: Catches and logs errors in message/state handlers
4. **Heartbeat Timeout**: Closes connection and triggers reconnection

## Best Practices

1. **Always disconnect on unmount**: Prevent memory leaks
2. **Use the React hook**: Simplifies lifecycle management
3. **Handle all message types**: Use switch statements for type safety
4. **Monitor connection state**: Show UI feedback for connection status
5. **Implement error boundaries**: Catch and handle WebSocket errors gracefully
