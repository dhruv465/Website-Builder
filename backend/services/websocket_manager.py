"""
WebSocket manager for real-time workflow updates.
"""
from typing import Dict, Set, Any
from fastapi import WebSocket
import json
import asyncio

from utils.logging import logger


class WebSocketManager:
    """Manager for WebSocket connections and broadcasting."""
    
    def __init__(self):
        """Initialize the WebSocket manager."""
        # Map of workflow_id to set of connected WebSocket clients
        self.connections: Dict[str, Set[WebSocket]] = {}
        self.lock = asyncio.Lock()
    
    async def connect(self, workflow_id: str, websocket: WebSocket):
        """
        Connect a WebSocket client to a workflow.
        
        Args:
            workflow_id: Workflow ID to subscribe to
            websocket: WebSocket connection
        """
        await websocket.accept()
        
        async with self.lock:
            if workflow_id not in self.connections:
                self.connections[workflow_id] = set()
            self.connections[workflow_id].add(websocket)
        
        logger.info(f"WebSocket connected to workflow {workflow_id}")
    
    async def disconnect(self, workflow_id: str, websocket: WebSocket):
        """
        Disconnect a WebSocket client from a workflow.
        
        Args:
            workflow_id: Workflow ID
            websocket: WebSocket connection
        """
        async with self.lock:
            if workflow_id in self.connections:
                self.connections[workflow_id].discard(websocket)
                
                # Clean up empty sets
                if not self.connections[workflow_id]:
                    del self.connections[workflow_id]
        
        logger.info(f"WebSocket disconnected from workflow {workflow_id}")
    
    async def broadcast(self, workflow_id: str, message: Dict[str, Any]):
        """
        Broadcast a message to all clients subscribed to a workflow.
        
        Args:
            workflow_id: Workflow ID
            message: Message to broadcast
        """
        if workflow_id not in self.connections:
            return
        
        # Get a copy of connections to avoid modification during iteration
        async with self.lock:
            connections = self.connections.get(workflow_id, set()).copy()
        
        # Broadcast to all connections
        disconnected = []
        for websocket in connections:
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"Error sending WebSocket message: {str(e)}")
                disconnected.append(websocket)
        
        # Clean up disconnected clients
        if disconnected:
            async with self.lock:
                for websocket in disconnected:
                    if workflow_id in self.connections:
                        self.connections[workflow_id].discard(websocket)
    
    async def send_progress_update(
        self,
        workflow_id: str,
        progress: float,
        current_agent: str,
        message: str,
    ):
        """
        Send a progress update to all clients.
        
        Args:
            workflow_id: Workflow ID
            progress: Progress percentage (0-100)
            current_agent: Current agent name
            message: Progress message
        """
        await self.broadcast(workflow_id, {
            "type": "progress",
            "workflow_id": workflow_id,
            "progress": progress,
            "current_agent": current_agent,
            "message": message,
        })
    
    async def send_log_entry(
        self,
        workflow_id: str,
        log_entry: Dict[str, Any],
    ):
        """
        Send a log entry to all clients.
        
        Args:
            workflow_id: Workflow ID
            log_entry: Log entry dictionary
        """
        await self.broadcast(workflow_id, {
            "type": "log",
            "workflow_id": workflow_id,
            "log": log_entry,
        })
    
    async def send_workflow_complete(
        self,
        workflow_id: str,
        result: Dict[str, Any],
    ):
        """
        Send workflow completion notification.
        
        Args:
            workflow_id: Workflow ID
            result: Workflow result
        """
        await self.broadcast(workflow_id, {
            "type": "complete",
            "workflow_id": workflow_id,
            "result": result,
        })
    
    async def send_workflow_error(
        self,
        workflow_id: str,
        error: str,
    ):
        """
        Send workflow error notification.
        
        Args:
            workflow_id: Workflow ID
            error: Error message
        """
        await self.broadcast(workflow_id, {
            "type": "error",
            "workflow_id": workflow_id,
            "error": error,
        })
    
    async def send_agent_status(
        self,
        workflow_id: str,
        agent_name: str,
        status: str,
        metadata: Dict[str, Any] = None,
    ):
        """
        Send agent status update.
        
        Args:
            workflow_id: Workflow ID
            agent_name: Agent name
            status: Agent status
            metadata: Optional metadata
        """
        await self.broadcast(workflow_id, {
            "type": "agent_status",
            "workflow_id": workflow_id,
            "agent_name": agent_name,
            "status": status,
            "metadata": metadata or {},
        })
    
    def get_connection_count(self, workflow_id: str) -> int:
        """
        Get number of connections for a workflow.
        
        Args:
            workflow_id: Workflow ID
            
        Returns:
            Number of connections
        """
        return len(self.connections.get(workflow_id, set()))
    
    def get_total_connections(self) -> int:
        """
        Get total number of connections across all workflows.
        
        Returns:
            Total number of connections
        """
        return sum(len(conns) for conns in self.connections.values())


# Global WebSocket manager instance
websocket_manager = WebSocketManager()
