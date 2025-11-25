import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import {
  CheckCircle2,
  XCircle,
  Loader2,
  ExternalLink,
  Clock,
  ChevronRight,
} from 'lucide-react';
import type { Deployment } from '@/lib/types';

interface DeploymentHistoryProps {
  deployments: Deployment[];
  onSelectDeployment?: (deployment: Deployment) => void;
  selectedDeploymentId?: string;
}

export function DeploymentHistory({
  deployments,
  onSelectDeployment,
  selectedDeploymentId,
}: DeploymentHistoryProps) {
  const [expandedId, setExpandedId] = useState<string | null>(null);

  const sortedDeployments = [...deployments].sort(
    (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
  );

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'success':
        return <CheckCircle2 className="h-4 w-4 text-green-500" />;
      case 'failed':
        return <XCircle className="h-4 w-4 text-red-500" />;
      case 'deploying':
      case 'pending':
        return <Loader2 className="h-4 w-4 text-blue-500 animate-spin" />;
      default:
        return <Clock className="h-4 w-4 text-gray-500" />;
    }
  };

  const getStatusBadge = (status: string) => {
    const variants: Record<string, 'default' | 'secondary' | 'destructive' | 'outline'> = {
      pending: 'secondary',
      deploying: 'default',
      success: 'default',
      failed: 'destructive',
    };

    return (
      <Badge variant={variants[status] || 'outline'} className="text-xs">
        {status.toUpperCase()}
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
    if (diffMins < 60) return `${diffMins} minute${diffMins > 1 ? 's' : ''} ago`;
    if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
    if (diffDays < 7) return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;

    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined,
    });
  };

  const formatFullDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const toggleExpand = (id: string) => {
    setExpandedId(expandedId === id ? null : id);
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg">Deployment History</CardTitle>
        <CardDescription>
          {deployments.length === 0
            ? 'No deployments yet'
            : `${deployments.length} deployment${deployments.length > 1 ? 's' : ''}`}
        </CardDescription>
      </CardHeader>

      <CardContent>
        {deployments.length === 0 ? (
          <div className="text-center py-8 text-muted-foreground">
            <p>No deployments have been created for this site yet.</p>
            <p className="text-sm mt-2">Deploy your site to see the history here.</p>
          </div>
        ) : (
          <ScrollArea className="h-[400px] pr-4">
            <div className="space-y-3">
              {sortedDeployments.map((deployment) => {
                const isExpanded = expandedId === deployment.id;
                const isSelected = selectedDeploymentId === deployment.id;

                return (
                  <div
                    key={deployment.id}
                    className={`border rounded-lg p-3 transition-all ${
                      isSelected ? 'border-primary bg-primary/5' : 'hover:border-primary/50'
                    }`}
                  >
                    <div className="flex items-start justify-between gap-3">
                      <div className="flex items-start gap-3 flex-1 min-w-0">
                        {getStatusIcon(deployment.status)}
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 mb-1">
                            {getStatusBadge(deployment.status)}
                            <span className="text-sm text-muted-foreground">
                              {formatDate(deployment.created_at)}
                            </span>
                          </div>
                          <div className="text-xs text-muted-foreground truncate">
                            ID: {deployment.id}
                          </div>
                        </div>
                      </div>

                      <div className="flex items-center gap-1">
                        {deployment.status === 'success' && deployment.url && (
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => window.open(deployment.url, '_blank')}
                            title="Open deployment"
                          >
                            <ExternalLink className="h-4 w-4" />
                          </Button>
                        )}
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => toggleExpand(deployment.id)}
                        >
                          <ChevronRight
                            className={`h-4 w-4 transition-transform ${
                              isExpanded ? 'rotate-90' : ''
                            }`}
                          />
                        </Button>
                      </div>
                    </div>

                    {isExpanded && (
                      <div className="mt-3 pt-3 border-t space-y-2 text-sm">
                        <div className="grid grid-cols-2 gap-2">
                          <div>
                            <span className="text-muted-foreground">Platform:</span>
                            <span className="ml-2 font-medium">{deployment.platform}</span>
                          </div>
                          <div>
                            <span className="text-muted-foreground">Created:</span>
                            <span className="ml-2 font-medium">
                              {formatFullDate(deployment.created_at)}
                            </span>
                          </div>
                        </div>

                        {deployment.deployed_at && (
                          <div>
                            <span className="text-muted-foreground">Deployed:</span>
                            <span className="ml-2 font-medium">
                              {formatFullDate(deployment.deployed_at)}
                            </span>
                          </div>
                        )}

                        {deployment.url && (
                          <div>
                            <span className="text-muted-foreground">URL:</span>
                            <a
                              href={deployment.url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="ml-2 text-primary hover:underline break-all"
                            >
                              {deployment.url}
                            </a>
                          </div>
                        )}

                        {deployment.error_message && (
                          <div className="p-2 bg-red-50 dark:bg-red-950 rounded text-red-600 dark:text-red-400">
                            <span className="font-medium">Error:</span>
                            <p className="mt-1 text-xs">{deployment.error_message}</p>
                          </div>
                        )}

                        {onSelectDeployment && (
                          <Button
                            variant="outline"
                            size="sm"
                            className="w-full mt-2"
                            onClick={() => onSelectDeployment(deployment)}
                          >
                            View Details
                          </Button>
                        )}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </ScrollArea>
        )}
      </CardContent>
    </Card>
  );
}
