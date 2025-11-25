"""
WebSocket API endpoints for real-time updates.
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from services.websocket_manager import websocket_manager
from utils.logging import logger

router = APIRouter()


@router.websocket("/ws/{workflow_id}")
async def websocket_endpoint(websocket: WebSocket, workflow_id: str):
    """
    WebSocket endpoint for workflow updates.
    
    Args:
        websocket: WebSocket connection
        workflow_id: Workflow ID to subscribe to
    """
    await websocket_manager.connect(workflow_id, websocket)
    
    try:
        # Keep connection alive and handle incoming messages
        while True:
            data = await websocket.receive_json()
            
            # Handle ping messages
            if data.get("type") == "ping":
                await websocket.send_json({"type": "pong"})
            
            # Handle workflow control messages
            elif data.get("type") == "workflow.cancel":
                logger.info(f"Received cancel request for workflow {workflow_id}")
                # The actual cancellation will be handled by the workflow API
                await websocket.send_json({
                    "type": "workflow.cancel_ack",
                    "workflow_id": workflow_id,
                })
            
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for workflow {workflow_id}")
    except Exception as e:
        logger.error(f"WebSocket error for workflow {workflow_id}: {str(e)}")
    finally:
        await websocket_manager.disconnect(workflow_id, websocket)
