import { useEffect, useRef, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Download, Trash2, Filter } from 'lucide-react';
import {
  DropdownMenu,
  DropdownMenuCheckboxItem,
  DropdownMenuContent,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import type { DeploymentLogEntry } from '@/lib/types';

interface DeploymentLogViewerProps {
  logs: DeploymentLogEntry[];
  isLive?: boolean;
  deploymentId?: string;
}

export function DeploymentLogViewer({
  logs,
  isLive = false,
  deploymentId,
}: DeploymentLogViewerProps) {
  const [filteredLogs, setFilteredLogs] = useState(logs);
  const [filters, setFilters] = useState({
    info: true,
    warning: true,
    error: true,
  });
  const scrollRef = useRef<HTMLDivElement>(null);
  const [autoScroll, setAutoScroll] = useState(true);

  useEffect(() => {
    const filtered = logs.filter((log) => filters[log.level]);
    setFilteredLogs(filtered);
  }, [logs, filters]);

  useEffect(() => {
    if (autoScroll && scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [filteredLogs, autoScroll]);

  const toggleFilter = (level: 'info' | 'warning' | 'error') => {
    setFilters((prev) => ({ ...prev, [level]: !prev[level] }));
  };

  const clearLogs = () => {
    setFilteredLogs([]);
  };

  const downloadLogs = () => {
    const logText = logs
      .map((log) => `[${log.timestamp}] [${log.level.toUpperCase()}] ${log.message}`)
      .join('\n');

    const blob = new Blob([logText], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `deployment-${deploymentId || 'logs'}-${Date.now()}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const getLogLevelColor = (level: string) => {
    switch (level) {
      case 'error':
        return 'text-red-500';
      case 'warning':
        return 'text-yellow-500';
      case 'info':
      default:
        return 'text-blue-500';
    }
  };

  const getLogLevelBadge = (level: string) => {
    const variants: Record<string, 'default' | 'secondary' | 'destructive' | 'outline'> = {
      error: 'destructive',
      warning: 'outline',
      info: 'secondary',
    };

    return (
      <Badge variant={variants[level] || 'default'} className="text-xs">
        {level.toUpperCase()}
      </Badge>
    );
  };

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('en-US', {
      hour12: false,
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    });
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="text-lg">Deployment Logs</CardTitle>
            <CardDescription>
              {isLive && (
                <span className="inline-flex items-center gap-1">
                  <span className="relative flex h-2 w-2">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span>
                  </span>
                  Live updates
                </span>
              )}
              {!isLive && `${logs.length} log entries`}
            </CardDescription>
          </div>
          <div className="flex gap-2">
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="outline" size="sm">
                  <Filter className="h-4 w-4 mr-2" />
                  Filter
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuLabel>Log Levels</DropdownMenuLabel>
                <DropdownMenuSeparator />
                <DropdownMenuCheckboxItem
                  checked={filters.info}
                  onCheckedChange={() => toggleFilter('info')}
                >
                  Info
                </DropdownMenuCheckboxItem>
                <DropdownMenuCheckboxItem
                  checked={filters.warning}
                  onCheckedChange={() => toggleFilter('warning')}
                >
                  Warning
                </DropdownMenuCheckboxItem>
                <DropdownMenuCheckboxItem
                  checked={filters.error}
                  onCheckedChange={() => toggleFilter('error')}
                >
                  Error
                </DropdownMenuCheckboxItem>
              </DropdownMenuContent>
            </DropdownMenu>

            <Button variant="outline" size="sm" onClick={downloadLogs} disabled={logs.length === 0}>
              <Download className="h-4 w-4 mr-2" />
              Download
            </Button>

            {!isLive && (
              <Button
                variant="outline"
                size="sm"
                onClick={clearLogs}
                disabled={filteredLogs.length === 0}
              >
                <Trash2 className="h-4 w-4 mr-2" />
                Clear
              </Button>
            )}
          </div>
        </div>
      </CardHeader>

      <CardContent>
        <ScrollArea className="h-[400px] w-full rounded-md border bg-muted/50" ref={scrollRef}>
          <div className="p-4 font-mono text-sm space-y-2">
            {filteredLogs.length === 0 && (
              <div className="text-center text-muted-foreground py-8">
                {logs.length === 0 ? 'No logs available' : 'No logs match the current filters'}
              </div>
            )}

            {filteredLogs.map((log, index) => (
              <div
                key={index}
                className="flex items-start gap-3 p-2 rounded hover:bg-muted/80 transition-colors"
              >
                <span className="text-muted-foreground text-xs whitespace-nowrap">
                  {formatTimestamp(log.timestamp)}
                </span>
                <div className="min-w-[60px]">{getLogLevelBadge(log.level)}</div>
                <span className={`flex-1 ${getLogLevelColor(log.level)}`}>{log.message}</span>
              </div>
            ))}
          </div>
        </ScrollArea>

        <div className="flex items-center justify-between mt-2 text-xs text-muted-foreground">
          <span>
            Showing {filteredLogs.length} of {logs.length} logs
          </span>
          {isLive && (
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={autoScroll}
                onChange={(e) => setAutoScroll(e.target.checked)}
                className="rounded"
              />
              Auto-scroll
            </label>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
