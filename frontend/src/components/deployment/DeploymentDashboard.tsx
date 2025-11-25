import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';
import { 
  Rocket, 
  Clock, 
  CheckCircle2, 
  XCircle, 
  ExternalLink,
  RotateCcw,
  Globe,
  Settings,
  TrendingUp,
} from 'lucide-react';
import { apiClient } from '@/lib/api/client';
import { cn } from '@/lib/utils';

interface Deployment {
  deployment_id: string;
  url: string;
  status: string;
  framework?: string;
  build_time?: number;
  created_at: string;
}

interface DeploymentDashboardProps {
  siteId: string;
  onDeploy?: () => void;
  onRollback?: (deploymentId: string) => void;
}

export function DeploymentDashboard({ siteId, onDeploy, onRollback }: DeploymentDashboardProps) {
  const [deployments, setDeployments] = useState<Deployment[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedDeployment, setSelectedDeployment] = useState<Deployment | null>(null);

  useEffect(() => {
    loadDeployments();
  }, [siteId]);

  const loadDeployments = async () => {
    setIsLoading(true);
    try {
      const response = await apiClient.get(`/api/deploy/history/${siteId}`);
      setDeployments(response.data.deployments);
    } catch (error) {
      console.error('Failed to load deployments:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleRollback = async (deploymentId: string) => {
    try {
      await apiClient.post(`/api/deploy/rollback/${siteId}/${deploymentId}`);
      onRollback?.(deploymentId);
      loadDeployments();
    } catch (error) {
      console.error('Failed to rollback deployment:', error);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status.toLowerCase()) {
      case 'ready':
      case 'success':
        return <CheckCircle2 className="h-4 w-4 text-green-500" />;
      case 'error':
      case 'failed':
        return <XCircle className="h-4 w-4 text-red-500" />;
      case 'building':
      case 'queued':
        return <Clock className="h-4 w-4 text-yellow-500 animate-pulse" />;
      default:
        return <Clock className="h-4 w-4 text-gray-500" />;
    }
  };

  const getStatusBadge = (status: string) => {
    const variants: Record<string, "default" | "secondary" | "destructive" | "outline"> = {
      ready: "default",
      success: "default",
      error: "destructive",
      failed: "destructive",
      building: "secondary",
      queued: "outline",
    };

    return (
      <Badge variant={variants[status.toLowerCase()] || "outline"}>
        {status}
      </Badge>
    );
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString();
  };

  const formatBuildTime = (seconds?: number) => {
    if (!seconds) return 'N/A';
    if (seconds < 60) return `${seconds}s`;
    return `${Math.floor(seconds / 60)}m ${seconds % 60}s`;
  };

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="flex items-center justify-between p-6 border-b border-border">
        <div>
          <h2 className="text-2xl font-bold flex items-center gap-2">
            <Rocket className="h-6 w-6 text-primary" />
            Deployments
          </h2>
          <p className="text-sm text-muted-foreground mt-1">
            Manage and track your site deployments
          </p>
        </div>
        <Button onClick={onDeploy}>
          <Rocket className="h-4 w-4 mr-2" />
          Deploy Now
        </Button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-4 p-6 border-b border-border">
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Total Deployments</CardDescription>
            <CardTitle className="text-3xl">{deployments.length}</CardTitle>
          </CardHeader>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Active</CardDescription>
            <CardTitle className="text-3xl text-green-500">
              {deployments.filter(d => d.status.toLowerCase() === 'ready').length}
            </CardTitle>
          </CardHeader>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Avg Build Time</CardDescription>
            <CardTitle className="text-3xl">
              {formatBuildTime(
                deployments.reduce((acc, d) => acc + (d.build_time || 0), 0) / deployments.length
              )}
            </CardTitle>
          </CardHeader>
        </Card>
      </div>

      {/* Deployment List */}
      <ScrollArea className="flex-1 p-6">
        {isLoading ? (
          <div className="flex items-center justify-center py-12">
            <Clock className="h-8 w-8 animate-spin text-muted-foreground" />
          </div>
        ) : deployments.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-12 text-center">
            <Rocket className="h-12 w-12 text-muted-foreground mb-4" />
            <h3 className="text-lg font-semibold mb-2">No deployments yet</h3>
            <p className="text-sm text-muted-foreground mb-4">
              Deploy your site to see it live on the web
            </p>
            <Button onClick={onDeploy}>
              <Rocket className="h-4 w-4 mr-2" />
              Deploy Now
            </Button>
          </div>
        ) : (
          <div className="space-y-4">
            {deployments.map((deployment, index) => (
              <Card
                key={deployment.deployment_id}
                className={cn(
                  'cursor-pointer transition-all hover:shadow-md',
                  selectedDeployment?.deployment_id === deployment.deployment_id && 'ring-2 ring-primary'
                )}
                onClick={() => setSelectedDeployment(deployment)}
              >
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div className="flex items-center gap-3">
                      {getStatusIcon(deployment.status)}
                      <div>
                        <CardTitle className="text-base">
                          Deployment #{deployments.length - index}
                        </CardTitle>
                        <CardDescription className="flex items-center gap-2 mt-1">
                          <Clock className="h-3 w-3" />
                          {formatDate(deployment.created_at)}
                          {deployment.build_time && (
                            <>
                              <span>•</span>
                              <TrendingUp className="h-3 w-3" />
                              {formatBuildTime(deployment.build_time)}
                            </>
                          )}
                        </CardDescription>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      {getStatusBadge(deployment.status)}
                      {deployment.framework && (
                        <Badge variant="outline">{deployment.framework}</Badge>
                      )}
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2 text-sm">
                      <Globe className="h-4 w-4 text-muted-foreground" />
                      <a
                        href={deployment.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-primary hover:underline"
                        onClick={(e) => e.stopPropagation()}
                      >
                        {deployment.url}
                      </a>
                      <ExternalLink className="h-3 w-3" />
                    </div>
                    {index > 0 && deployment.status.toLowerCase() === 'ready' && (
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleRollback(deployment.deployment_id);
                        }}
                      >
                        <RotateCcw className="h-4 w-4 mr-2" />
                        Rollback
                      </Button>
                    )}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </ScrollArea>

      {/* Deployment Details Panel */}
      {selectedDeployment && (
        <div className="border-t border-border p-6 bg-muted/20">
          <h3 className="text-lg font-semibold mb-4">Deployment Details</h3>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-sm text-muted-foreground">Deployment ID</p>
              <p className="text-sm font-mono">{selectedDeployment.deployment_id}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Status</p>
              <p className="text-sm">{getStatusBadge(selectedDeployment.status)}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">URL</p>
              <a
                href={selectedDeployment.url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-sm text-primary hover:underline flex items-center gap-1"
              >
                {selectedDeployment.url}
                <ExternalLink className="h-3 w-3" />
              </a>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Build Time</p>
              <p className="text-sm">{formatBuildTime(selectedDeployment.build_time)}</p>
            </div>
            {selectedDeployment.framework && (
              <div>
                <p className="text-sm text-muted-foreground">Framework</p>
                <p className="text-sm">{selectedDeployment.framework}</p>
              </div>
            )}
            <div>
              <p className="text-sm text-muted-foreground">Created</p>
              <p className="text-sm">{new Date(selectedDeployment.created_at).toLocaleString()}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
