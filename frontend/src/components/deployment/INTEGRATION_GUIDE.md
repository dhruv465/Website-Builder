# Deployment Components Integration Guide

This guide shows how to integrate the deployment components with WebSocket for real-time updates.

## Basic Usage

### Simple Deployment Panel

The easiest way to use the deployment components is with the `DeploymentPanel`:

```tsx
import { DeploymentPanel } from '@/components/deployment';

function MyPage() {
  return (
    <DeploymentPanel 
      siteId="site-123" 
      siteName="My Website"
    />
  );
}
```

### With Initial Data

If you already have deployment data, pass it to avoid an initial fetch:

```tsx
import { DeploymentPanel } from '@/components/deployment';
import { Site } from '@/lib/types';

function ProjectPage({ site }: { site: Site }) {
  return (
    <DeploymentPanel 
      siteId={site.id} 
      siteName={site.name}
      initialDeployments={site.deployments}
    />
  );
}
```

## Advanced Usage with WebSocket

For real-time deployment updates, integrate with the WebSocket client:

### Step 1: Create a Custom Hook

```tsx
// hooks/useDeploymentWebSocket.ts
import { useEffect, useState } from 'react';
import { useWebSocket } from '@/lib/hooks/useWebSocket';
import type { DeploymentLogEntry, DeploymentWebSocketMessage } from '@/lib/types';

export function useDeploymentWebSocket(deploymentId: string | null) {
  const [logs, setLogs] = useState<DeploymentLogEntry[]>([]);
  const [status, setStatus] = useState<string | null>(null);
  const [progress, setProgress] = useState<number>(0);

  const { connect, disconnect, isConnected } = useWebSocket({
    onMessage: (message: DeploymentWebSocketMessage) => {
      switch (message.type) {
        case 'deployment.log':
          if (message.deployment_id === deploymentId) {
            setLogs((prev) => [...prev, message.log]);
          }
          break;

        case 'deployment.status':
          if (message.deployment_id === deploymentId) {
            setStatus(message.status);
            if (message.progress !== undefined) {
              setProgress(message.progress);
            }
          }
          break;

        case 'deployment.complete':
          if (message.deployment_id === deploymentId) {
            setStatus('success');
            setProgress(100);
            setLogs((prev) => [
              ...prev,
              {
                timestamp: new Date().toISOString(),
                level: 'info',
                message: `Deployment complete! Live at: ${message.url}`,
              },
            ]);
          }
          break;

        case 'deployment.error':
          if (message.deployment_id === deploymentId) {
            setStatus('failed');
            setLogs((prev) => [
              ...prev,
              {
                timestamp: new Date().toISOString(),
                level: 'error',
                message: message.error,
              },
            ]);
          }
          break;
      }
    },
  });

  useEffect(() => {
    if (deploymentId) {
      connect(deploymentId);
    }

    return () => {
      disconnect();
    };
  }, [deploymentId, connect, disconnect]);

  return {
    logs,
    status,
    progress,
    isConnected,
  };
}
```

### Step 2: Use in Component

```tsx
import { useState } from 'react';
import { DeploymentPanel } from '@/components/deployment';
import { DeploymentLogViewer } from '@/components/deployment';
import { useDeploymentWebSocket } from '@/hooks/useDeploymentWebSocket';

function DeploymentPageWithLiveUpdates({ siteId }: { siteId: string }) {
  const [currentDeploymentId, setCurrentDeploymentId] = useState<string | null>(null);
  const { logs, status, progress, isConnected } = useDeploymentWebSocket(currentDeploymentId);

  const handleDeploymentStart = (deploymentId: string) => {
    setCurrentDeploymentId(deploymentId);
  };

  return (
    <div className="space-y-6">
      <DeploymentPanel 
        siteId={siteId}
        onDeploymentStart={handleDeploymentStart}
      />

      {currentDeploymentId && (
        <DeploymentLogViewer
          logs={logs}
          isLive={isConnected && (status === 'pending' || status === 'deploying')}
          deploymentId={currentDeploymentId}
        />
      )}
    </div>
  );
}
```

## Individual Component Usage

### DeploymentConfigDialog

Use this component to collect deployment configuration:

```tsx
import { useState } from 'react';
import { DeploymentConfigDialog } from '@/components/deployment';
import { deployToVercel } from '@/lib/api/deploy';
import type { DeploymentConfig } from '@/lib/types';

function MyComponent() {
  const [isOpen, setIsOpen] = useState(false);

  const handleDeploy = async (config: DeploymentConfig) => {
    const deployment = await deployToVercel({
      site_id: 'site-123',
      platform: 'vercel',
      config,
    });
    console.log('Deployment started:', deployment.id);
  };

  return (
    <>
      <button onClick={() => setIsOpen(true)}>Deploy</button>
      <DeploymentConfigDialog
        open={isOpen}
        onOpenChange={setIsOpen}
        onDeploy={handleDeploy}
        siteId="site-123"
        siteName="My Site"
      />
    </>
  );
}
```

### DeploymentStatus

Display the status of a single deployment:

```tsx
import { DeploymentStatus } from '@/components/deployment';
import type { Deployment } from '@/lib/types';

function MyComponent({ deployment }: { deployment: Deployment }) {
  const handleRefresh = () => {
    // Refresh deployment list
    console.log('Refreshing deployments');
  };

  return (
    <DeploymentStatus 
      deployment={deployment}
      onRefresh={handleRefresh}
    />
  );
}
```

### DeploymentHistory

Show a list of all deployments:

```tsx
import { DeploymentHistory } from '@/components/deployment';
import type { Deployment } from '@/lib/types';

function MyComponent({ deployments }: { deployments: Deployment[] }) {
  const handleSelect = (deployment: Deployment) => {
    console.log('Selected deployment:', deployment.id);
  };

  return (
    <DeploymentHistory
      deployments={deployments}
      onSelectDeployment={handleSelect}
      selectedDeploymentId="deployment-123"
    />
  );
}
```

## API Integration

The deployment components use the following API endpoints:

```typescript
import { 
  deployToVercel, 
  getDeploymentStatus, 
  getSiteDeployments 
} from '@/lib/api/deploy';

// Start a new deployment
const deployment = await deployToVercel({
  site_id: 'site-123',
  platform: 'vercel',
  config: {
    projectName: 'my-site',
    buildCommand: 'npm run build',
    outputDirectory: 'dist',
    environmentVariables: {
      API_KEY: 'secret',
    },
  },
});

// Get deployment status
const status = await getDeploymentStatus(deployment.id);

// Get all deployments for a site
const deployments = await getSiteDeployments('site-123');
```

## WebSocket Message Format

The backend should send messages in this format:

```typescript
// Deployment status update
{
  type: 'deployment.status',
  deployment_id: 'deployment-123',
  status: 'deploying',
  progress: 50
}

// Deployment log entry
{
  type: 'deployment.log',
  deployment_id: 'deployment-123',
  log: {
    timestamp: '2024-11-17T10:30:00Z',
    level: 'info',
    message: 'Building project...'
  }
}

// Deployment complete
{
  type: 'deployment.complete',
  deployment_id: 'deployment-123',
  url: 'https://my-site.vercel.app'
}

// Deployment error
{
  type: 'deployment.error',
  deployment_id: 'deployment-123',
  error: 'Build failed: Missing dependencies'
}
```

## Error Handling

All components include comprehensive error handling:

```tsx
import { DeploymentPanel } from '@/components/deployment';

function MyComponent() {
  return (
    <DeploymentPanel 
      siteId="site-123"
      onError={(error) => {
        console.error('Deployment error:', error);
        // Show toast notification
      }}
    />
  );
}
```

## Styling Customization

Components use Tailwind CSS and can be customized:

```tsx
import { DeploymentStatus } from '@/components/deployment';

function MyComponent({ deployment }) {
  return (
    <div className="custom-wrapper">
      <DeploymentStatus 
        deployment={deployment}
        className="custom-status-card"
      />
    </div>
  );
}
```

## Testing

Example test for deployment components:

```tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { DeploymentConfigDialog } from '@/components/deployment';

describe('DeploymentConfigDialog', () => {
  it('should submit deployment configuration', async () => {
    const onDeploy = jest.fn();
    
    render(
      <DeploymentConfigDialog
        open={true}
        onOpenChange={() => {}}
        onDeploy={onDeploy}
        siteId="site-123"
      />
    );

    fireEvent.change(screen.getByLabelText(/project name/i), {
      target: { value: 'my-project' },
    });

    fireEvent.click(screen.getByText(/deploy/i));

    await waitFor(() => {
      expect(onDeploy).toHaveBeenCalledWith(
        expect.objectContaining({
          projectName: 'my-project',
          platform: 'vercel',
        })
      );
    });
  });
});
```

## Best Practices

1. **Always handle errors**: Wrap deployment calls in try-catch blocks
2. **Show loading states**: Use the built-in loading indicators
3. **Provide feedback**: Use toast notifications for success/error
4. **Poll for updates**: If WebSocket is unavailable, poll the status endpoint
5. **Clean up**: Disconnect WebSocket connections when components unmount
6. **Validate input**: Use the built-in form validation
7. **Test thoroughly**: Test both success and failure scenarios

## Troubleshooting

### Deployment not starting
- Check that the site ID is valid
- Verify API endpoint is accessible
- Check browser console for errors

### WebSocket not connecting
- Verify WebSocket URL is correct
- Check that deployment ID is valid
- Ensure backend WebSocket server is running

### Logs not updating
- Check WebSocket connection status
- Verify message format matches expected structure
- Check browser console for WebSocket errors

### Build errors
- Verify build command is correct
- Check that all dependencies are installed
- Review deployment logs for specific errors
