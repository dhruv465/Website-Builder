"""
Workflow management API endpoints.
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import uuid

from services.orchestrator import orchestrator, WorkflowType, WorkflowStatus

router = APIRouter()


class WorkflowCreateRequest(BaseModel):
    """Request model for creating a workflow."""
    requirements: str
    session_id: str
    framework: Optional[str] = None
    design_style: Optional[str] = None
    features: Optional[List[str]] = None


class WorkflowUpdateRequest(BaseModel):
    """Request model for updating a workflow."""
    requirements: str
    session_id: str
    site_id: str
    framework: Optional[str] = None
    design_style: Optional[str] = None


class WorkflowResponse(BaseModel):
    """Response model for workflow operations."""
    workflow_id: str
    status: str
    message: str


@router.post("/create", response_model=WorkflowResponse)
async def create_workflow(request: WorkflowCreateRequest, background_tasks: BackgroundTasks):
    """Start a new CREATE_SITE workflow."""
    workflow_id = str(uuid.uuid4())
    
    input_data = {
        "requirements": request.requirements,
        "framework": request.framework,
        "design_style": request.design_style,
        "features": request.features or [],
    }
    
    # Start workflow in background
    background_tasks.add_task(
        orchestrator.execute_workflow,
        workflow_type=WorkflowType.CREATE_SITE,
        input_data=input_data,
        session_id=request.session_id,
        workflow_id=workflow_id
    )
    
    return WorkflowResponse(
        workflow_id=workflow_id,
        status="pending",
        message="Workflow started successfully"
    )


@router.post("/update", response_model=WorkflowResponse)
async def update_workflow(request: WorkflowUpdateRequest, background_tasks: BackgroundTasks):
    """Start an UPDATE_SITE workflow."""
    workflow_id = str(uuid.uuid4())
    
    input_data = {
        "requirements": request.requirements,
        "site_id": request.site_id,
        "framework": request.framework,
        "design_style": request.design_style,
    }
    
    # Start workflow in background
    background_tasks.add_task(
        orchestrator.execute_workflow,
        workflow_type=WorkflowType.UPDATE_SITE,
        input_data=input_data,
        session_id=request.session_id,
        workflow_id=workflow_id
    )
    
    return WorkflowResponse(
        workflow_id=workflow_id,
        status="pending",
        message="Update workflow started successfully"
    )


@router.get("/{workflow_id}/status")
async def get_workflow_status(workflow_id: str):
    """Get workflow status."""
    status = orchestrator.get_workflow_status(workflow_id)
    if not status:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return status


@router.delete("/{workflow_id}")
async def cancel_workflow(workflow_id: str):
    """Cancel a running workflow."""
    success = await orchestrator.cancel_workflow(workflow_id)
    if not success:
        raise HTTPException(status_code=404, detail="Workflow not found or cannot be cancelled")
    return {"message": "Workflow cancelled successfully"}
