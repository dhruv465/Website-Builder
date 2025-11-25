import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Rocket, AlertCircle } from 'lucide-react';
import { DeploymentConfigDialog } from './DeploymentConfigDialog';
import { DeploymentStatus } from './DeploymentStatus';
import { DeploymentLogViewer } from './DeploymentLogViewer';
import { DeploymentHistory } from './DeploymentHistory';
import { deployToVercel, getSiteDeployments } from '@/lib/api/deploy';
import type { Deployment, DeploymentConfig, DeploymentLogEntry } from '@/lib/types';

interface DeploymentPanelProps {
  siteId: string;
  siteName?: string;
  initialDeployments?: Deployment[];
}

export function DeploymentPanel({
  siteId,
  siteName,
  initialDeployments = [],
}: DeploymentPanelProps) {
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [deployments, setDeployments] = useState<Deployment[]>(initialDeployments);
  const [currentDeployment, setCurrentDeployment] = useState<Deployment | null>(null);
  const [logs, setLogs] = useState<DeploymentLogEntry[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  // Load deployments on mount
  useEffect(() => {
    loadDeployments();
  }, [siteId]);

  const loadDeployments = async () => {
    try {
      const fetchedDeployments = await getSiteDeployments(siteId);
      setDeployments(fetchedDeployments);

      // Set the most recent deployment as current
      if (fetchedDeployments.length > 0) {
        const latest = fetchedDeployments.sort(
          (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
        )[0];
        if (latest) {
          setCurrentDeployment(latest);
        }
      }
    } catch (err) {
      console.error('Failed to load deployments:', err);
    }
  };

  const handleDeploy = async (config: DeploymentConfig) => {
    setIsLoading(true);
    setError(null);
    setLogs([]);

    try {
      // Add initial log
      setLogs([
        {
          timestamp: new Date().toISOString(),
          level: 'info',
          message: 'Initiating deployment to Vercel...',
        },
      ]);

      const deployment = await deployToVercel({
        site_id: siteId,
        platform: 'vercel',
        config,
      });

      setCurrentDeployment(deployment);
      setDeployments((prev) => [deployment, ...prev]);

      // Add success log
      setLogs((prev) => [
        ...prev,
        {
          timestamp: new Date().toISOString(),
          level: 'info',
          message: `Deployment created with ID: ${deployment.id}`,
        },
        {
          timestamp: new Date().toISOString(),
          level: 'info',
          message: 'Deployment is now in progress. This may take a few minutes...',
        },
      ]);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to create deployment';
      setError(errorMessage);

      setLogs((prev) => [
        ...prev,
        {
          timestamp: new Date().toISOString(),
          level: 'error',
          message: errorMessage,
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSelectDeployment = (deployment: Deployment) => {
    setCurrentDeployment(deployment);
    // In a real implementation, you would fetch logs for this deployment
    setLogs([
      {
        timestamp: deployment.created_at,
        level: 'info',
        message: 'Deployment created',
      },
      {
        timestamp: deployment.deployed_at || deployment.created_at,
        level: deployment.status === 'success' ? 'info' : 'error',
        message:
          deployment.status === 'success'
            ? 'Deployment completed successfully'
            : deployment.error_message || 'Deployment failed',
      },
    ]);
  };

  const handleRefresh = () => {
    loadDeployments();
  };

  return (
    <div className="space-y-6">
      {/* Deploy Button */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Deployment</h2>
          <p className="text-muted-foreground">Deploy your site to Vercel</p>
        </div>
        <Button onClick={() => setIsDialogOpen(true)} disabled={isLoading}>
          <Rocket className="mr-2 h-4 w-4" />
          Deploy Site
        </Button>
      </div>

      {/* Error Alert */}
      {error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Current Deployment Status */}
      {currentDeployment && (
        <DeploymentStatus deployment={currentDeployment} onRefresh={handleRefresh} />
      )}

      {/* Deployment Logs */}
      {logs.length > 0 && (
        <DeploymentLogViewer
          logs={logs}
          isLive={
            currentDeployment?.status === 'pending' || currentDeployment?.status === 'deploying'
          }
          deploymentId={currentDeployment?.id}
        />
      )}

      {/* Deployment History */}
      <DeploymentHistory
        deployments={deployments}
        onSelectDeployment={handleSelectDeployment}
        selectedDeploymentId={currentDeployment?.id}
      />

      {/* Deployment Config Dialog */}
      <DeploymentConfigDialog
        open={isDialogOpen}
        onOpenChange={setIsDialogOpen}
        onDeploy={handleDeploy}
        siteId={siteId}
        siteName={siteName}
      />
    </div>
  );
}
