import type { WebSocketMessage, WebSocketCommand } from '../types/workflow';

export enum ConnectionState {
  CONNECTING = 'connecting',
  CONNECTED = 'connected',
  DISCONNECTED = 'disconnected',
  ERROR = 'error',
}

type MessageHandler = (message: WebSocketMessage) => void;
type StateChangeHandler = (state: ConnectionState) => void;

export class WebSocketClient {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectTimeout: NodeJS.Timeout | null = null;
  private heartbeatInterval: NodeJS.Timeout | null = null;
  private heartbeatTimeout: NodeJS.Timeout | null = null;
  private messageHandlers: Set<MessageHandler> = new Set();
  private stateChangeHandlers: Set<StateChangeHandler> = new Set();
  private currentState: ConnectionState = ConnectionState.DISCONNECTED;
  private workflowId: string | null = null;
  private shouldReconnect = true;

  constructor(private baseUrl: string) {}

  /**
   * Connect to WebSocket server for a specific workflow
   */
  connect(workflowId: string): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      console.warn('WebSocket already connected');
      return;
    }

    // Validate workflow ID format (basic UUID validation)
    if (!this.isValidWorkflowId(workflowId)) {
      console.error('Invalid workflow ID format');
      this.setState(ConnectionState.ERROR);
      return;
    }

    this.workflowId = workflowId;
    this.shouldReconnect = true;
    this.setState(ConnectionState.CONNECTING);

    // Build WebSocket URL with session ID if available
    const sessionId = localStorage.getItem('session_id');
    let wsUrl = `${this.baseUrl}/api/ws/${workflowId}`;
    
    // Add session ID as query parameter for authentication
    if (sessionId) {
      wsUrl += `?session_id=${encodeURIComponent(sessionId)}`;
    }
    
    try {
      this.ws = new WebSocket(wsUrl);
      this.setupEventHandlers();
    } catch (error) {
      console.error('Failed to create WebSocket:', error);
      this.setState(ConnectionState.ERROR);
      this.attemptReconnect();
    }
  }

  /**
   * Validate workflow ID format
   */
  private isValidWorkflowId(workflowId: string): boolean {
    // Basic UUID format validation
    const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
    return uuidRegex.test(workflowId);
  }

  /**
   * Set up WebSocket event handlers
   */
  private setupEventHandlers(): void {
    if (!this.ws) return;

    this.ws.onopen = () => {
      console.log('WebSocket connected');
      this.reconnectAttempts = 0;
      this.setState(ConnectionState.CONNECTED);
      this.startHeartbeat();
    };

    this.ws.onmessage = (event: MessageEvent) => {
      try {
        const message = JSON.parse(event.data) as WebSocketMessage;
        this.handleMessage(message);
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error);
      }
    };

    this.ws.onerror = (error: Event) => {
      console.error('WebSocket error:', error);
      this.setState(ConnectionState.ERROR);
    };

    this.ws.onclose = (event: CloseEvent) => {
      console.log('WebSocket closed:', event.code, event.reason);
      this.stopHeartbeat();
      this.setState(ConnectionState.DISCONNECTED);
      
      if (this.shouldReconnect) {
        this.attemptReconnect();
      }
    };
  }

  /**
   * Handle incoming WebSocket messages
   */
  private handleMessage(message: WebSocketMessage): void {
    // Validate message structure
    if (!message || typeof message !== 'object' || !message.type) {
      console.warn('Invalid WebSocket message format:', message);
      return;
    }

    // Handle pong messages for heartbeat
    if (message.type === 'pong') {
      this.resetHeartbeatTimeout();
      return;
    }

    // Sanitize message data to prevent XSS
    const sanitizedMessage = this.sanitizeMessage(message);

    // Notify all registered message handlers
    this.messageHandlers.forEach(handler => {
      try {
        handler(sanitizedMessage);
      } catch (error) {
        console.error('Error in message handler:', error);
      }
    });
  }

  /**
   * Sanitize message to prevent XSS attacks
   */
  private sanitizeMessage(message: WebSocketMessage): WebSocketMessage {
    // Create a deep copy to avoid modifying original
    const sanitized = JSON.parse(JSON.stringify(message));

    // Recursively sanitize string values
    const sanitizeValue = (value: any): any => {
      if (typeof value === 'string') {
        // Remove script tags and dangerous content
        return value
          .replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '')
          .replace(/javascript:/gi, '')
          .replace(/on\w+\s*=/gi, '');
      }
      if (Array.isArray(value)) {
        return value.map(sanitizeValue);
      }
      if (value && typeof value === 'object') {
        const sanitizedObj: any = {};
        for (const key in value) {
          sanitizedObj[key] = sanitizeValue(value[key]);
        }
        return sanitizedObj;
      }
      return value;
    };

    return sanitizeValue(sanitized);
  }

  /**
   * Attempt to reconnect with exponential backoff
   */
  private attemptReconnect(): void {
    if (!this.shouldReconnect || !this.workflowId) {
      return;
    }

    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('Max reconnection attempts reached');
      this.setState(ConnectionState.ERROR);
      return;
    }

    this.reconnectAttempts++;
    const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 30000);
    
    console.log(`Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
    
    this.reconnectTimeout = setTimeout(() => {
      if (this.workflowId) {
        this.connect(this.workflowId);
      }
    }, delay);
  }

  /**
   * Start heartbeat mechanism to keep connection alive
   */
  private startHeartbeat(): void {
    this.stopHeartbeat();

    // Send ping every 30 seconds
    this.heartbeatInterval = setInterval(() => {
      if (this.ws?.readyState === WebSocket.OPEN) {
        this.send({ type: 'ping' });
        this.setHeartbeatTimeout();
      }
    }, 30000);

    // Initial heartbeat
    this.setHeartbeatTimeout();
  }

  /**
   * Set timeout for heartbeat response
   */
  private setHeartbeatTimeout(): void {
    this.clearHeartbeatTimeout();

    // Expect pong within 10 seconds
    this.heartbeatTimeout = setTimeout(() => {
      console.warn('Heartbeat timeout - connection may be dead');
      this.ws?.close();
    }, 10000);
  }

  /**
   * Reset heartbeat timeout when pong is received
   */
  private resetHeartbeatTimeout(): void {
    this.clearHeartbeatTimeout();
  }

  /**
   * Clear heartbeat timeout
   */
  private clearHeartbeatTimeout(): void {
    if (this.heartbeatTimeout) {
      clearTimeout(this.heartbeatTimeout);
      this.heartbeatTimeout = null;
    }
  }

  /**
   * Stop heartbeat mechanism
   */
  private stopHeartbeat(): void {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
      this.heartbeatInterval = null;
    }
    this.clearHeartbeatTimeout();
  }

  /**
   * Send a command to the WebSocket server
   */
  send(command: WebSocketCommand): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      try {
        this.ws.send(JSON.stringify(command));
      } catch (error) {
        console.error('Failed to send WebSocket message:', error);
      }
    } else {
      console.warn('Cannot send message - WebSocket not connected');
    }
  }

  /**
   * Subscribe to WebSocket messages
   */
  subscribe(handler: MessageHandler): () => void {
    this.messageHandlers.add(handler);
    
    // Return unsubscribe function
    return () => {
      this.messageHandlers.delete(handler);
    };
  }

  /**
   * Subscribe to connection state changes
   */
  onStateChange(handler: StateChangeHandler): () => void {
    this.stateChangeHandlers.add(handler);
    
    // Immediately call with current state
    handler(this.currentState);
    
    // Return unsubscribe function
    return () => {
      this.stateChangeHandlers.delete(handler);
    };
  }

  /**
   * Update connection state and notify handlers
   */
  private setState(state: ConnectionState): void {
    if (this.currentState !== state) {
      this.currentState = state;
      this.stateChangeHandlers.forEach(handler => {
        try {
          handler(state);
        } catch (error) {
          console.error('Error in state change handler:', error);
        }
      });
    }
  }

  /**
   * Get current connection state
   */
  getState(): ConnectionState {
    return this.currentState;
  }

  /**
   * Disconnect from WebSocket server
   */
  disconnect(): void {
    this.shouldReconnect = false;
    
    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout);
      this.reconnectTimeout = null;
    }
    
    this.stopHeartbeat();
    
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    
    this.setState(ConnectionState.DISCONNECTED);
    this.workflowId = null;
  }

  /**
   * Check if WebSocket is connected
   */
  isConnected(): boolean {
    return this.currentState === ConnectionState.CONNECTED;
  }

  /**
   * Reset reconnection attempts (useful for manual reconnect)
   */
  resetReconnectAttempts(): void {
    this.reconnectAttempts = 0;
  }
}
