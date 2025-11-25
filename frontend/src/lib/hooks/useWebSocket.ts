import { useEffect, useRef, useState, useCallback } from 'react';
import { WebSocketClient, ConnectionState } from '../websocket/client';
import type { WebSocketMessage, WebSocketCommand } from '../types/workflow';

interface UseWebSocketOptions {
  /**
   * Base URL for WebSocket connection
   * @default process.env.VITE_WS_URL || 'ws://localhost:8000'
   */
  baseUrl?: string;
  
  /**
   * Whether to automatically connect on mount
   * @default true
   */
  autoConnect?: boolean;
  
  /**
   * Callback for incoming messages
   */
  onMessage?: (message: WebSocketMessage) => void;
  
  /**
   * Callback for connection state changes
   */
  onStateChange?: (state: ConnectionState) => void;
}

interface UseWebSocketReturn {
  /**
   * Current connection state
   */
  state: ConnectionState;
  
  /**
   * Whether the WebSocket is connected
   */
  isConnected: boolean;
  
  /**
   * Connect to WebSocket for a specific workflow
   */
  connect: (workflowId: string) => void;
  
  /**
   * Disconnect from WebSocket
   */
  disconnect: () => void;
  
  /**
   * Send a command to the WebSocket server
   */
  send: (command: WebSocketCommand) => void;
  
  /**
   * Subscribe to WebSocket messages
   */
  subscribe: (handler: (message: WebSocketMessage) => void) => () => void;
  
  /**
   * Last received message
   */
  lastMessage: WebSocketMessage | null;
}

/**
 * Custom React hook for WebSocket connection management
 * 
 * @example
 * ```tsx
 * const { state, isConnected, connect, disconnect, send, lastMessage } = useWebSocket({
 *   onMessage: (message) => {
 *     console.log('Received:', message);
 *   },
 *   onStateChange: (state) => {
 *     console.log('State changed:', state);
 *   }
 * });
 * 
 * // Connect to a workflow
 * useEffect(() => {
 *   connect('workflow-123');
 *   return () => disconnect();
 * }, []);
 * 
 * // Send a command
 * const cancelWorkflow = () => {
 *   send({ type: 'workflow.cancel', workflow_id: 'workflow-123' });
 * };
 * ```
 */
export function useWebSocket(options: UseWebSocketOptions = {}): UseWebSocketReturn {
  const {
    baseUrl = import.meta.env.VITE_WS_URL || 'ws://localhost:8000',
    autoConnect = false,
    onMessage,
    onStateChange,
  } = options;

  const clientRef = useRef<WebSocketClient | null>(null);
  const [state, setState] = useState<ConnectionState>(ConnectionState.DISCONNECTED);
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null);
  const workflowIdRef = useRef<string | null>(null);

  // Initialize WebSocket client
  useEffect(() => {
    if (!clientRef.current) {
      clientRef.current = new WebSocketClient(baseUrl);
    }

    return () => {
      clientRef.current?.disconnect();
      clientRef.current = null;
    };
  }, [baseUrl]);

  // Subscribe to state changes
  useEffect(() => {
    if (!clientRef.current) return;

    const unsubscribe = clientRef.current.onStateChange((newState) => {
      setState(newState);
      onStateChange?.(newState);
    });

    return unsubscribe;
  }, [onStateChange]);

  // Subscribe to messages
  useEffect(() => {
    if (!clientRef.current) return;

    const unsubscribe = clientRef.current.subscribe((message) => {
      setLastMessage(message);
      onMessage?.(message);
    });

    return unsubscribe;
  }, [onMessage]);

  // Connect function
  const connect = useCallback((workflowId: string) => {
    if (!clientRef.current) {
      console.error('WebSocket client not initialized');
      return;
    }

    workflowIdRef.current = workflowId;
    clientRef.current.connect(workflowId);
  }, []);

  // Disconnect function
  const disconnect = useCallback(() => {
    if (!clientRef.current) return;
    
    clientRef.current.disconnect();
    workflowIdRef.current = null;
  }, []);

  // Send function
  const send = useCallback((command: WebSocketCommand) => {
    if (!clientRef.current) {
      console.error('WebSocket client not initialized');
      return;
    }

    clientRef.current.send(command);
  }, []);

  // Subscribe function
  const subscribe = useCallback((handler: (message: WebSocketMessage) => void) => {
    if (!clientRef.current) {
      console.error('WebSocket client not initialized');
      return () => {};
    }

    return clientRef.current.subscribe(handler);
  }, []);

  // Auto-connect if enabled and workflowId is provided
  useEffect(() => {
    if (autoConnect && workflowIdRef.current && clientRef.current) {
      clientRef.current.connect(workflowIdRef.current);
    }
  }, [autoConnect]);

  return {
    state,
    isConnected: state === ConnectionState.CONNECTED,
    connect,
    disconnect,
    send,
    subscribe,
    lastMessage,
  };
}
