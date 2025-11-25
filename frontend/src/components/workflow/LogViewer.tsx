import { useEffect, useRef, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { ScrollArea } from '../ui/scroll-area';
import { Search, Download, Trash2, Filter } from 'lucide-react';
import type { LogEntry } from '../../lib/types';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuCheckboxItem,
  DropdownMenuTrigger,
} from '../ui/dropdown-menu';

interface LogViewerProps {
  logs: LogEntry[];
  maxHeight?: string;
  autoScroll?: boolean;
}

export function LogViewer({ logs, maxHeight = '400px', autoScroll = true }: LogViewerProps) {
  const scrollRef = useRef<HTMLDivElement>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [levelFilters, setLevelFilters] = useState<Set<LogEntry['level']>>(
    new Set(['info', 'warning', 'error'])
  );
  const [agentFilters, setAgentFilters] = useState<Set<string>>(new Set());

  // Auto-scroll to bottom when new logs arrive
  useEffect(() => {
    if (autoScroll && scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [logs, autoScroll]);

  // Extract unique agents from logs
  const uniqueAgents = Array.from(new Set(logs.map(log => log.agent)));

  // Initialize agent filters
  useEffect(() => {
    if (agentFilters.size === 0 && uniqueAgents.length > 0) {
      setAgentFilters(new Set(uniqueAgents));
    }
  }, [uniqueAgents.length]);

  // Filter logs
  const filteredLogs = logs.filter(log => {
    // Level filter
    if (!levelFilters.has(log.level)) return false;

    // Agent filter
    if (agentFilters.size > 0 && !agentFilters.has(log.agent)) return false;

    // Search filter
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      return (
        log.message.toLowerCase().includes(query) ||
        log.agent.toLowerCase().includes(query)
      );
    }

    return true;
  });

  const getLevelColor = (level: LogEntry['level']) => {
    switch (level) {
      case 'error':
        return 'text-red-500 bg-red-500/10';
      case 'warning':
        return 'text-yellow-500 bg-yellow-500/10';
      case 'info':
      default:
        return 'text-blue-500 bg-blue-500/10';
    }
  };

  const getLevelBadgeVariant = (level: LogEntry['level']): 'default' | 'secondary' | 'destructive' => {
    switch (level) {
      case 'error':
        return 'destructive';
      case 'warning':
        return 'default';
      case 'info':
      default:
        return 'secondary';
    }
  };

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    const timeStr = date.toLocaleTimeString('en-US', {
      hour12: false,
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    });
    const ms = date.getMilliseconds().toString().padStart(3, '0');
    return `${timeStr}.${ms}`;
  };

  const formatAgentName = (name: string) => {
    return name
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  const handleExportLogs = () => {
    const logText = filteredLogs
      .map(log => `[${log.timestamp}] [${log.level.toUpperCase()}] [${log.agent}] ${log.message}`)
      .join('\n');

    const blob = new Blob([logText], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `workflow-logs-${new Date().toISOString()}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const handleClearSearch = () => {
    setSearchQuery('');
  };

  const toggleLevelFilter = (level: LogEntry['level']) => {
    setLevelFilters(prev => {
      const newSet = new Set(prev);
      if (newSet.has(level)) {
        newSet.delete(level);
      } else {
        newSet.add(level);
      }
      return newSet;
    });
  };

  const toggleAgentFilter = (agent: string) => {
    setAgentFilters(prev => {
      const newSet = new Set(prev);
      if (newSet.has(agent)) {
        newSet.delete(agent);
      } else {
        newSet.add(agent);
      }
      return newSet;
    });
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg">Workflow Logs</CardTitle>
          <div className="flex items-center gap-2">
            <Badge variant="outline">
              {filteredLogs.length} / {logs.length}
            </Badge>
            <Button
              variant="ghost"
              size="sm"
              onClick={handleExportLogs}
              disabled={filteredLogs.length === 0}
            >
              <Download className="h-4 w-4" />
            </Button>
          </div>
        </div>

        {/* Filters */}
        <div className="flex items-center gap-2 pt-2">
          {/* Search */}
          <div className="relative flex-1">
            <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search logs..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-8 pr-8"
            />
            {searchQuery && (
              <Button
                variant="ghost"
                size="sm"
                className="absolute right-0 top-0 h-full px-2"
                onClick={handleClearSearch}
              >
                <Trash2 className="h-4 w-4" />
              </Button>
            )}
          </div>

          {/* Level filter */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="outline" size="sm">
                <Filter className="h-4 w-4 mr-2" />
                Level
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuCheckboxItem
                checked={levelFilters.has('info')}
                onCheckedChange={() => toggleLevelFilter('info')}
              >
                Info
              </DropdownMenuCheckboxItem>
              <DropdownMenuCheckboxItem
                checked={levelFilters.has('warning')}
                onCheckedChange={() => toggleLevelFilter('warning')}
              >
                Warning
              </DropdownMenuCheckboxItem>
              <DropdownMenuCheckboxItem
                checked={levelFilters.has('error')}
                onCheckedChange={() => toggleLevelFilter('error')}
              >
                Error
              </DropdownMenuCheckboxItem>
            </DropdownMenuContent>
          </DropdownMenu>

          {/* Agent filter */}
          {uniqueAgents.length > 0 && (
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="outline" size="sm">
                  <Filter className="h-4 w-4 mr-2" />
                  Agent
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                {uniqueAgents.map(agent => (
                  <DropdownMenuCheckboxItem
                    key={agent}
                    checked={agentFilters.has(agent)}
                    onCheckedChange={() => toggleAgentFilter(agent)}
                  >
                    {formatAgentName(agent)}
                  </DropdownMenuCheckboxItem>
                ))}
              </DropdownMenuContent>
            </DropdownMenu>
          )}
        </div>
      </CardHeader>

      <CardContent>
        <ScrollArea
          ref={scrollRef}
          className="rounded-md border bg-muted/30"
          style={{ height: maxHeight }}
        >
          <div className="p-4 space-y-2 font-mono text-sm">
            {filteredLogs.length === 0 ? (
              <div className="text-center text-muted-foreground py-8">
                {logs.length === 0 ? 'No logs yet' : 'No logs match the current filters'}
              </div>
            ) : (
              filteredLogs.map((log, index) => (
                <div
                  key={index}
                  className={`flex items-start gap-2 p-2 rounded-md ${getLevelColor(log.level)}`}
                >
                  <span className="text-xs text-muted-foreground whitespace-nowrap">
                    {formatTimestamp(log.timestamp)}
                  </span>
                  <Badge variant={getLevelBadgeVariant(log.level)} className="text-xs">
                    {log.level.toUpperCase()}
                  </Badge>
                  <Badge variant="outline" className="text-xs">
                    {formatAgentName(log.agent)}
                  </Badge>
                  <span className="flex-1 break-words">{log.message}</span>
                </div>
              ))
            )}
          </div>
        </ScrollArea>
      </CardContent>
    </Card>
  );
}
