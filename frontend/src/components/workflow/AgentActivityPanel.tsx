import { useMemo } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Progress } from '../ui/progress';
import { Badge } from '../ui/badge';
import { Separator } from '../ui/separator';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { XCircle, CheckCircle2, Clock, Loader2 } from 'lucide-react';
import { AgentStatusCard } from './AgentStatusCard';
import { LogViewer } from './LogViewer';
import { ErrorAlert } from './ErrorAlert';
import { useWorkflow } from '../../lib/context';
import { ConnectionState } from '../../lib/websocket/client';
import { createError, ErrorType } from '../../lib/utils/errors';

interface AgentActivityPanelProps {
  onCancel?: () => void;
  showLogs?: boolean;
  className?: string;
}

export function AgentActivityPanel({
  onCancel,
  showLogs = true,
  className = '',
}: AgentActivityPanelProps) {
  const {
    workflowState,
    agentStatuses,
    connectionState,
    isCancelling,
    error,
    cancelWorkflow,
    clearError,
  } = useWorkflow();

  // Convert agent statuses map to array
  const agents = useMemo(() => {
    return Array.from(agentStatuses.values());
  }, [agentStatuses]);

  // Calculate overall progress
  const overallProgress = workflowState?.progress_percentage ?? 0;

  // Get workflow status
  const workflowStatus = workflowState?.status ?? 'pending';

  // Format estimated time remaining
  const formatEstimatedTime = () => {
    if (!workflowState || workflowStatus === 'completed' || workflowStatus === 'failed') {
      return null;
    }

    // Simple estimation based on progress
    // This is a placeholder - backend should provide actual estimates
    const completedAgents = agents.filter(a => a.status === 'completed').length;
    const totalAgents = agents.length;
    
    if (totalAgents === 0 || completedAgents === 0) {
      return 'Calculating...';
    }

    const avgTimePerAgent = agents
      .filter(a => a.startTime && a.endTime)
      .reduce((sum, a) => {
        const duration = new Date(a.endTime!).getTime() - new Date(a.startTime!).getTime();
        return sum + duration;
      }, 0) / completedAgents;

    const remainingAgents = totalAgents - completedAgents;
    const estimatedMs = avgTimePerAgent * remainingAgents;
    const estimatedSeconds = Math.ceil(estimatedMs / 1000);

    if (estimatedSeconds < 60) {
      return `~${estimatedSeconds}s`;
    }

    const minutes = Math.floor(estimatedSeconds / 60);
    const seconds = estimatedSeconds % 60;
    return `~${minutes}m ${seconds}s`;
  };

  const getStatusIcon = () => {
    switch (workflowStatus) {
      case 'completed':
        return <CheckCircle2 className="h-5 w-5 text-green-500" />;
      case 'failed':
      case 'cancelled':
        return <XCircle className="h-5 w-5 text-red-500" />;
      case 'running':
        return <Loader2 className="h-5 w-5 text-blue-500 animate-spin" />;
      case 'pending':
      default:
        return <Clock className="h-5 w-5 text-gray-400" />;
    }
  };

  const getStatusBadge = () => {
    const variants: Record<typeof workflowStatus, 'default' | 'secondary' | 'destructive' | 'outline'> = {
      pending: 'outline',
      running: 'default',
      completed: 'secondary',
      failed: 'destructive',
      cancelled: 'destructive',
    };

    return (
      <Badge variant={variants[workflowStatus]}>
        {workflowStatus.charAt(0).toUpperCase() + workflowStatus.slice(1)}
      </Badge>
    );
  };

  const getConnectionBadge = () => {
    const variants: Record<ConnectionState, { variant: 'default' | 'secondary' | 'destructive' | 'outline'; label: string }> = {
      [ConnectionState.CONNECTED]: { variant: 'secondary', label: 'Connected' },
      [ConnectionState.CONNECTING]: { variant: 'outline', label: 'Connecting' },
      [ConnectionState.DISCONNECTED]: { variant: 'outline', label: 'Disconnected' },
      [ConnectionState.ERROR]: { variant: 'destructive', label: 'Connection Error' },
    };

    const config = variants[connectionState];
    return (
      <Badge variant={config.variant} className="text-xs">
        {config.label}
      </Badge>
    );
  };

  const handleCancel = async () => {
    await cancelWorkflow();
    onCancel?.();
  };

  const handleRetry = () => {
    clearError();
    // Retry logic would be handled by parent component
  };

  if (!workflowState) {
    return (
      <Card className={className}>
        <CardContent className="flex items-center justify-center py-12">
          <p className="text-muted-foreground">No active workflow</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className={className}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            {getStatusIcon()}
            <CardTitle>Workflow Activity</CardTitle>
          </div>
          <div className="flex items-center gap-2">
            {getConnectionBadge()}
            {getStatusBadge()}
          </div>
        </div>

        {/* Overall Progress */}
        <div className="space-y-2 pt-4">
          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">Overall Progress</span>
            <div className="flex items-center gap-2">
              <span className="font-medium">{overallProgress}%</span>
              {formatEstimatedTime() && (
                <span className="text-xs text-muted-foreground">
                  {formatEstimatedTime()} remaining
                </span>
              )}
            </div>
          </div>
          <Progress value={overallProgress} className="h-2" />
        </div>

        {/* Cancel Button */}
        {(workflowStatus === 'running' || workflowStatus === 'pending') && (
          <div className="pt-2">
            <Button
              variant="outline"
              size="sm"
              onClick={handleCancel}
              disabled={isCancelling}
              className="w-full"
            >
              {isCancelling ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Cancelling...
                </>
              ) : (
                <>
                  <XCircle className="mr-2 h-4 w-4" />
                  Cancel Workflow
                </>
              )}
            </Button>
          </div>
        )}
      </CardHeader>

      <CardContent className="space-y-4">
        {/* Error Alert */}
        {error && (
          <ErrorAlert
            error={createError(ErrorType.API_ERROR, error)}
            onRetry={handleRetry}
            onDismiss={clearError}
          />
        )}

        {/* Tabs for Agents and Logs */}
        <Tabs defaultValue="agents" className="w-full">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="agents">
              Agents ({agents.length})
            </TabsTrigger>
            {showLogs && (
              <TabsTrigger value="logs">
                Logs ({workflowState.logs.length})
              </TabsTrigger>
            )}
          </TabsList>

          <TabsContent value="agents" className="space-y-3 mt-4">
            {agents.length === 0 ? (
              <div className="text-center text-muted-foreground py-8">
                No agents active yet
              </div>
            ) : (
              agents.map(agent => (
                <AgentStatusCard key={agent.name} agent={agent} />
              ))
            )}
          </TabsContent>

          {showLogs && (
            <TabsContent value="logs" className="mt-4">
              <LogViewer
                logs={workflowState.logs}
                maxHeight="500px"
                autoScroll={workflowStatus === 'running'}
              />
            </TabsContent>
          )}
        </Tabs>

        {/* Workflow Summary */}
        {(workflowStatus === 'completed' || workflowStatus === 'failed' || workflowStatus === 'cancelled') && (
          <>
            <Separator />
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Workflow ID</span>
                <span className="font-mono text-xs">{workflowState.workflow_id}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Completed Agents</span>
                <span>{workflowState.completed_agents.length} / {agents.length}</span>
              </div>
              {workflowState.current_agent && (
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Last Agent</span>
                  <span>{workflowState.current_agent}</span>
                </div>
              )}
            </div>
          </>
        )}
      </CardContent>
    </Card>
  );
}
