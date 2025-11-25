
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import { Progress } from '../ui/progress';
import { CheckCircle2, Circle, Loader2, XCircle } from 'lucide-react';
import type { AgentStatus } from '../../lib/types';

interface AgentStatusCardProps {
  agent: AgentStatus;
}

export function AgentStatusCard({ agent }: AgentStatusCardProps) {
  const getStatusIcon = () => {
    switch (agent.status) {
      case 'completed':
        return <CheckCircle2 className="h-5 w-5 text-green-500" />;
      case 'executing':
        return <Loader2 className="h-5 w-5 text-blue-500 animate-spin" />;
      case 'failed':
        return <XCircle className="h-5 w-5 text-red-500" />;
      case 'pending':
      default:
        return <Circle className="h-5 w-5 text-gray-400" />;
    }
  };

  const getStatusBadge = () => {
    const variants: Record<AgentStatus['status'], 'default' | 'secondary' | 'destructive' | 'outline'> = {
      pending: 'outline',
      executing: 'default',
      completed: 'secondary',
      failed: 'destructive',
    };

    return (
      <Badge variant={variants[agent.status]}>
        {agent.status.charAt(0).toUpperCase() + agent.status.slice(1)}
      </Badge>
    );
  };

  const formatDuration = () => {
    if (!agent.startTime) return null;
    
    const start = new Date(agent.startTime).getTime();
    const end = agent.endTime ? new Date(agent.endTime).getTime() : Date.now();
    const duration = Math.floor((end - start) / 1000);
    
    if (duration < 60) {
      return `${duration}s`;
    }
    
    const minutes = Math.floor(duration / 60);
    const seconds = duration % 60;
    return `${minutes}m ${seconds}s`;
  };

  const formatAgentName = (name: string) => {
    return name
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  return (
    <Card className="transition-all hover:shadow-md">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            {getStatusIcon()}
            <CardTitle className="text-base font-medium">
              {formatAgentName(agent.name)}
            </CardTitle>
          </div>
          {getStatusBadge()}
        </div>
      </CardHeader>
      <CardContent className="space-y-3">
        {/* Progress bar for executing agents */}
        {agent.status === 'executing' && agent.progress !== undefined && (
          <div className="space-y-1">
            <div className="flex justify-between text-xs text-muted-foreground">
              <span>Progress</span>
              <span>{agent.progress}%</span>
            </div>
            <Progress value={agent.progress} className="h-2" />
          </div>
        )}

        {/* Duration */}
        {agent.startTime && (
          <div className="flex justify-between text-xs text-muted-foreground">
            <span>Duration</span>
            <span className="font-mono">{formatDuration()}</span>
          </div>
        )}

        {/* Error message */}
        {agent.error && (
          <div className="rounded-md bg-destructive/10 p-2 text-xs text-destructive">
            {agent.error}
          </div>
        )}

        {/* Timestamps */}
        {(agent.startTime || agent.endTime) && (
          <div className="space-y-1 text-xs text-muted-foreground">
            {agent.startTime && (
              <div className="flex justify-between">
                <span>Started</span>
                <span className="font-mono">
                  {new Date(agent.startTime).toLocaleTimeString()}
                </span>
              </div>
            )}
            {agent.endTime && (
              <div className="flex justify-between">
                <span>Ended</span>
                <span className="font-mono">
                  {new Date(agent.endTime).toLocaleTimeString()}
                </span>
              </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
