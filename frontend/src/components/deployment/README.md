# Deployment Components

This directory contains components for managing site deployments to Vercel.

## Components

### DeploymentPanel

Main container component that orchestrates the deployment workflow.

**Props:**
- `siteId: string` - ID of the site to deploy
- `siteName?: string` - Optional name of the site
- `initialDeployments?: Deployment[]` - Optional initial deployments list

**Features:**
- Initiates new deployments
- Displays current deployment status
- Shows deployment logs
- Lists deployment history

**Usage:**
```tsx
<DeploymentPanel 
  siteId="site-123" 
  siteName="My Awesome Site"
/>
```

### DeploymentConfigDialog

Modal dialog for configuring deployment settings before deploying.

**Props:**
- `open: boolean` - Controls dialog visibility
- `onOpenChange: (open: boolean) => void` - Callback when dialog state changes
- `onDeploy: (config: DeploymentConfig) => Promise<void>` - Callback when deployment is submitted
- `siteId: string` - ID of the site being deployed
- `siteName?: string` - Optional site name for default project name

**Features:**
- Project name configuration
- Build command customization
- Output directory specification
- Environment variables input
- Form validation with Zod

### DeploymentStatus

Displays the current status of a deployment with real-time updates.

**Props:**
- `deployment: Deployment` - The deployment to display
- `onRefresh?: () => void` - Optional callback when status updates

**Features:**
- Status badge (pending, deploying, success, failed)
- Progress bar for in-progress deployments
- Live URL display with copy and open actions
- Error messages with troubleshooting tips
- Automatic polling for status updates

### DeploymentLogViewer

Displays deployment logs with filtering and export capabilities.

**Props:**
- `logs: DeploymentLogEntry[]` - Array of log entries
- `isLive?: boolean` - Whether logs are being updated in real-time
- `deploymentId?: string` - Optional deployment ID for log export filename

**Features:**
- Real-time log streaming
- Log level filtering (info, warning, error)
- Auto-scroll for live logs
- Download logs as text file
- Clear logs functionality
- Syntax highlighting by log level

### DeploymentHistory

Lists all deployments for a site with expandable details.

**Props:**
- `deployments: Deployment[]` - Array of deployments
- `onSelectDeployment?: (deployment: Deployment) => void` - Callback when deployment is selected
- `selectedDeploymentId?: string` - ID of currently selected deployment

**Features:**
- Chronological list of deployments
- Status indicators
- Expandable deployment details
- Quick access to live URLs
- Relative timestamps (e.g., "2 hours ago")

## Integration

### With WebSocket

For real-time deployment updates, integrate with WebSocket client:

```tsx
import { useWebSocket } from '@/lib/hooks/useWebSocket';
import { DeploymentPanel } from '@/components/deployment';

function MyComponent() {
  const [logs, setLogs] = useState<DeploymentLogEntry[]>([]);
  
  const { connect, disconnect } = useWebSocket({
    onMessage: (message) => {
      if (message.type === 'deployment.log') {
        setLogs(prev => [...prev, message.log]);
      }
    }
  });

  useEffect(() => {
    if (deploymentId) {
      connect(deploymentId);
    }
    return () => disconnect();
  }, [deploymentId]);

  return <DeploymentPanel siteId={siteId} />;
}
```

### With API

The components use the deployment API client from `@/lib/api/deploy`:

```tsx
import { deployToVercel, getDeploymentStatus, getSiteDeployments } from '@/lib/api/deploy';

// Deploy a site
const deployment = await deployToVercel({
  site_id: 'site-123',
  platform: 'vercel',
  config: {
    projectName: 'my-site',
    buildCommand: 'npm run build',
    outputDirectory: 'dist',
  }
});

// Get deployment status
const status = await getDeploymentStatus(deployment.id);

// Get all deployments for a site
const deployments = await getSiteDeployments('site-123');
```

## Styling

All components use ShadCN UI components and Tailwind CSS for consistent styling with the rest of the application.

## Accessibility

- Keyboard navigation support
- ARIA labels for screen readers
- Focus management in dialogs
- Color contrast compliance
- Status indicators with icons and text

## Error Handling

Components include comprehensive error handling:
- Network errors with retry options
- Validation errors with helpful messages
- Deployment failures with troubleshooting guidance
- Graceful degradation when features are unavailable
