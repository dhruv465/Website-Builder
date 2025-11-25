import { useEffect, useState } from 'react';
import { Wifi, WifiOff, AlertCircle } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { Badge } from '@/components/ui/badge';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import { ConnectionState } from '@/lib/websocket/client';

interface ConnectionStatusProps {
  status: ConnectionState;
  onReconnect?: () => void;
  showLabel?: boolean;
  className?: string;
}

export function ConnectionStatus({
  status,
  onReconnect,
  showLabel = false,
  className = '',
}: ConnectionStatusProps) {
  const [isVisible, setIsVisible] = useState(false);

  // Only show indicator when not connected
  useEffect(() => {
    if (status !== ConnectionState.CONNECTED) {
      setIsVisible(true);
    } else {
      // Hide after a brief delay when connected
      const timer = setTimeout(() => setIsVisible(false), 2000);
      return () => clearTimeout(timer);
    }
  }, [status]);

  const getStatusConfig = () => {
    switch (status) {
      case ConnectionState.CONNECTED:
        return {
          icon: <Wifi className="h-3 w-3" />,
          label: 'Connected',
          color: 'bg-green-500',
          variant: 'default' as const,
        };
      case ConnectionState.CONNECTING:
        return {
          icon: <Wifi className="h-3 w-3 animate-pulse" />,
          label: 'Connecting...',
          color: 'bg-yellow-500',
          variant: 'secondary' as const,
        };
      case ConnectionState.DISCONNECTED:
        return {
          icon: <WifiOff className="h-3 w-3" />,
          label: 'Disconnected',
          color: 'bg-gray-500',
          variant: 'secondary' as const,
        };
      case ConnectionState.ERROR:
        return {
          icon: <AlertCircle className="h-3 w-3" />,
          label: 'Connection Error',
          color: 'bg-red-500',
          variant: 'destructive' as const,
        };
    }
  };

  const config = getStatusConfig();

  return (
    <AnimatePresence>
      {isVisible && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -10 }}
          className={className}
        >
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger asChild>
                <Badge
                  variant={config.variant}
                  className="cursor-pointer gap-1.5"
                  onClick={
                    status === ConnectionState.DISCONNECTED || status === ConnectionState.ERROR
                      ? onReconnect
                      : undefined
                  }
                >
                  <span className={`h-2 w-2 rounded-full ${config.color} animate-pulse`} />
                  {config.icon}
                  {showLabel && <span className="text-xs">{config.label}</span>}
                </Badge>
              </TooltipTrigger>
              <TooltipContent>
                <p>{config.label}</p>
                {(status === ConnectionState.DISCONNECTED || status === ConnectionState.ERROR) &&
                  onReconnect && (
                    <p className="text-xs text-muted-foreground">Click to reconnect</p>
                  )}
              </TooltipContent>
            </Tooltip>
          </TooltipProvider>
        </motion.div>
      )}
    </AnimatePresence>
  );
}

// Inline connection indicator (simpler version)
interface InlineConnectionStatusProps {
  status: ConnectionState;
  className?: string;
}

export function InlineConnectionStatus({ status, className = '' }: InlineConnectionStatusProps) {
  const getStatusConfig = () => {
    switch (status) {
      case ConnectionState.CONNECTED:
        return { color: 'bg-green-500', label: 'Connected' };
      case ConnectionState.CONNECTING:
        return { color: 'bg-yellow-500 animate-pulse', label: 'Connecting' };
      case ConnectionState.DISCONNECTED:
        return { color: 'bg-gray-500', label: 'Disconnected' };
      case ConnectionState.ERROR:
        return { color: 'bg-red-500', label: 'Error' };
    }
  };

  const config = getStatusConfig();

  return (
    <div className={`flex items-center gap-2 ${className}`}>
      <span className={`h-2 w-2 rounded-full ${config.color}`} />
      <span className="text-xs text-muted-foreground">{config.label}</span>
    </div>
  );
}
