"""
Audit API endpoints.
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import uuid

from agents.audit_agent import (
    AuditAgent,
    AuditInput,
    AuditResult,
)
from agents.base_agent import AgentContext, AgentError
from repositories.audit_repository import AuditRepository
from services.celery_app import celery_app
from services.websocket_manager import websocket_manager
from utils.logging import logger

router = APIRouter()

# Request/Response Models

class RunAuditRequest(BaseModel):
    """Request to run audit on HTML code."""
    html_code: str = Field(..., description="HTML code to audit")
    site_id: str = Field(..., description="Site ID for storing results")
    site_version_id: Optional[str] = Field(None, description="Site version ID")
    session_id: str = Field(..., description="Session ID for tracking")
    workflow_id: Optional[str] = Field(None, description="Workflow ID for tracking")
    async_processing: bool = Field(default=False, description="Process asynchronously via Celery")


class AuditResponse(BaseModel):
    """Response with audit results."""
    success: bool
    audit_result: Optional[Dict[str, Any]] = None
    audit_id: Optional[str] = None
    confidence: float = 0.0
    workflow_id: str
    message: Optional[str] = None
    task_id: Optional[str] = None  # For async processing


class AuditHistoryResponse(BaseModel):
    """Response with audit history."""
    site_id: str
    audits: List[Dict[str, Any]]
    count: int


class AuditTrendsResponse(BaseModel):
    """Response with audit trends."""
    site_id: str
    period_days: int
    audit_count: int
    trends: List[Dict[str, Any]]
    average_scores: Dict[str, float]
    improvement: Dict[str, int]
    latest_audit: Optional[Dict[str, Any]] = None


# Initialize Audit Agent
audit_agent = AuditAgent()


@router.post("/run", response_model=AuditResponse)
async def run_audit(req: RunAuditRequest, background_tasks: BackgroundTasks):
    """
    Run audit on HTML code.
    
    This endpoint evaluates HTML code for SEO, accessibility, and performance.
    It generates detailed issue reports with fix suggestions and stores results
    in the database.
    
    Args:
        req: Audit request
        background_tasks: FastAPI background tasks
        
    Returns:
        AuditResponse with audit results
    """
    try:
        # Validate input
        if not req.html_code or len(req.html_code.strip()) == 0:
            raise HTTPException(
                status_code=400,
                detail="html_code cannot be empty"
            )
        
        # Validate UUIDs
        try:
            site_uuid = uuid.UUID(req.site_id)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid site_id format. Must be a valid UUID."
            )
        
        site_version_uuid = None
        if req.site_version_id:
            try:
                site_version_uuid = uuid.UUID(req.site_version_id)
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid site_version_id format. Must be a valid UUID."
                )
        
        try:
            uuid.UUID(req.session_id)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid session_id format. Must be a valid UUID."
            )
        
        # Generate workflow ID if not provided
        workflow_id = req.workflow_id or f"audit_{req.site_id}_{uuid.uuid4()}"
        
        # Check if async processing is requested
        if req.async_processing:
            # Queue task in Celery
            task = celery_app.send_task(
                'tasks.run_audit_task',
                args=[
                    req.html_code,
                    req.site_id,
                    req.site_version_id,
                    req.session_id,
                    workflow_id
                ]
            )
            
            logger.info(f"Queued audit task {task.id} for workflow {workflow_id}")
            
            return AuditResponse(
                success=True,
                workflow_id=workflow_id,
                task_id=task.id,
                message="Audit queued for async processing"
            )
        
        # Synchronous processing
        # Get previous audit for comparison
        audit_repo = AuditRepository()
        previous_audit = audit_repo.get_latest_audit(site_uuid)
        previous_audit_data = None
        if previous_audit:
            previous_audit_data = {
                "overall_score": previous_audit.overall_score,
                "seo_score": previous_audit.seo_score,
                "accessibility_score": previous_audit.accessibility_score,
                "performance_score": previous_audit.performance_score,
            }
        
        # Create input for agent
        input_data = AuditInput(
            html_code=req.html_code,
            previous_audit=previous_audit_data,
            site_id=req.site_id,
        )
        
        # Create context
        context = AgentContext(
            session_id=req.session_id,
            workflow_id=workflow_id,
        )
        
        # Execute agent
        logger.info(f"Running audit for workflow {workflow_id}")
        
        # Send WebSocket update
        await websocket_manager.send_workflow_update(
            workflow_id,
            {
                "type": "agent_status",
                "agent": "AuditAgent",
                "status": "working",
                "message": "Running audit..."
            }
        )
        
        result = await audit_agent.execute_with_metrics(input_data, context)
        
        if not result.success:
            await websocket_manager.send_workflow_update(
                workflow_id,
                {
                    "type": "agent_status",
                    "agent": "AuditAgent",
                    "status": "error",
                    "message": "Audit failed"
                }
            )
            raise HTTPException(
                status_code=500,
                detail="Failed to run audit"
            )
        
        # Store audit results in database
        audit_result = result.audit_result
        audit_record = audit_repo.create_audit(
            site_id=site_uuid,
            site_version_id=site_version_uuid,
            seo_score=audit_result.seo.score,
            accessibility_score=audit_result.accessibility.score,
            performance_score=audit_result.performance.score,
            overall_score=audit_result.overall_score,
            details={
                "seo": audit_result.seo.model_dump(),
                "accessibility": audit_result.accessibility.model_dump(),
                "performance": audit_result.performance.model_dump(),
                "improvement_from_previous": audit_result.improvement_from_previous,
            }
        )
        
        # Store audit issues
        all_issues = (
            audit_result.seo.issues +
            audit_result.accessibility.issues +
            audit_result.performance.issues
        )
        
        for issue in all_issues:
            audit_repo.create_audit_issue(
                audit_id=audit_record.id,
                category=issue.category.value,
                severity=issue.severity,
                description=issue.description,
                location=issue.location,
                fix_suggestion=issue.fix_suggestion,
            )
        
        # Send success update
        await websocket_manager.send_workflow_update(
            workflow_id,
            {
                "type": "agent_status",
                "agent": "AuditAgent",
                "status": "done",
                "message": f"Audit complete. Overall score: {audit_result.overall_score}"
            }
        )
        
        # Build response
        response = AuditResponse(
            success=True,
            audit_result=audit_result.model_dump(),
            audit_id=str(audit_record.id),
            confidence=result.confidence,
            workflow_id=workflow_id,
            message=f"Audit completed successfully. Overall score: {audit_result.overall_score}"
        )
        
        logger.info(
            f"Successfully completed audit for workflow {workflow_id}. "
            f"Overall score: {audit_result.overall_score}"
        )
        
        return response
        
    except HTTPException:
        raise
    except AgentError as e:
        logger.error(f"Agent error running audit: {e.message}")
        if e.error_type.value == "validation_error":
            raise HTTPException(status_code=400, detail=e.message)
        else:
            raise HTTPException(status_code=500, detail=e.message)
    except Exception as e:
        logger.error(f"Unexpected error running audit: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while running audit"
        )


@router.get("/history/{site_id}", response_model=AuditHistoryResponse)
async def get_audit_history(site_id: str, limit: Optional[int] = 10):
    """
    Get audit history for a site.
    
    Args:
        site_id: Site ID
        limit: Maximum number of audits to return (default: 10)
        
    Returns:
        AuditHistoryResponse with audit history
    """
    try:
        # Validate site_id
        try:
            site_uuid = uuid.UUID(site_id)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid site_id format. Must be a valid UUID."
            )
        
        # Get audits from database
        audit_repo = AuditRepository()
        audits = audit_repo.get_audits_by_site(site_uuid, limit=limit)
        
        # Format audits for response
        audit_list = []
        for audit in audits:
            audit_data = {
                "id": str(audit.id),
                "site_version_id": str(audit.site_version_id) if audit.site_version_id else None,
                "overall_score": audit.overall_score,
                "seo_score": audit.seo_score,
                "accessibility_score": audit.accessibility_score,
                "performance_score": audit.performance_score,
                "created_at": audit.created_at.isoformat(),
                "issue_count": len(audit.issues) if audit.issues else 0,
            }
            
            # Add details if available
            if audit.details:
                audit_data["details"] = audit.details
            
            audit_list.append(audit_data)
        
        return AuditHistoryResponse(
            site_id=site_id,
            audits=audit_list,
            count=len(audit_list)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting audit history: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve audit history"
        )


@router.get("/trends/{site_id}", response_model=AuditTrendsResponse)
async def get_audit_trends(site_id: str, days: Optional[int] = 30):
    """
    Get audit trends for a site over time.
    
    Args:
        site_id: Site ID
        days: Number of days to look back (default: 30)
        
    Returns:
        AuditTrendsResponse with trend data
    """
    try:
        # Validate site_id
        try:
            site_uuid = uuid.UUID(site_id)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid site_id format. Must be a valid UUID."
            )
        
        # Validate days parameter
        if days < 1 or days > 365:
            raise HTTPException(
                status_code=400,
                detail="days parameter must be between 1 and 365"
            )
        
        # Get trends from database
        audit_repo = AuditRepository()
        trends_data = audit_repo.get_audit_trends(site_uuid, days=days)
        
        # Check if there was an error
        if "error" in trends_data:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to calculate trends: {trends_data['error']}"
            )
        
        return AuditTrendsResponse(**trends_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting audit trends: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve audit trends"
        )
