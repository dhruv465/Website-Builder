"""
API endpoints for automatic improvement workflow.
"""
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session

from services.orchestrator import orchestrator, WorkflowType
from services.tasks import improve_site_task
from repositories.quality_threshold_repository import QualityThresholdRepository
from repositories.improvement_cycle_repository import ImprovementCycleRepository
from models.base import get_db
from utils.logging import logger


router = APIRouter(prefix="/api/improve", tags=["improvement"])


# Request/Response Models
class StartImprovementRequest(BaseModel):
    """Request to start improvement workflow."""
    html_code: str = Field(..., description="Current HTML code to improve")
    session_id: str = Field(..., description="Session ID")
    threshold_config: Optional[Dict[str, int]] = Field(
        None,
        description="Optional custom threshold configuration"
    )
    max_cycles: int = Field(
        default=2,
        ge=1,
        le=5,
        description="Maximum improvement cycles (1-5)"
    )
    async_mode: bool = Field(
        default=True,
        description="Run improvement workflow asynchronously"
    )


class ThresholdCheckRequest(BaseModel):
    """Request to check quality thresholds."""
    audit_result: Dict[str, Any] = Field(..., description="Audit result to check")
    threshold_config: Optional[Dict[str, int]] = Field(
        None,
        description="Optional custom threshold configuration"
    )


class ThresholdCheckResponse(BaseModel):
    """Response for threshold check."""
    meets_thresholds: bool
    seo_pass: bool
    accessibility_pass: bool
    performance_pass: bool
    overall_pass: bool
    seo_gap: int
    accessibility_gap: int
    performance_gap: int
    overall_gap: int
    thresholds: Dict[str, int]
    scores: Dict[str, int]


class ImprovementStatusResponse(BaseModel):
    """Response for improvement workflow status."""
    workflow_id: str
    status: str
    progress_percentage: float
    current_cycle: Optional[int] = None
    total_cycles: Optional[int] = None
    current_agent: Optional[str] = None
    completed_agents: List[str]
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    metrics: Optional[Dict[str, Any]] = None


class QualityThresholdResponse(BaseModel):
    """Response for quality threshold."""
    id: str
    name: str
    seo_min_score: int
    accessibility_min_score: int
    performance_min_score: int
    overall_min_score: int
    enabled: bool
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class UpdateThresholdRequest(BaseModel):
    """Request to update quality threshold."""
    seo_min_score: Optional[int] = Field(None, ge=0, le=100)
    accessibility_min_score: Optional[int] = Field(None, ge=0, le=100)
    performance_min_score: Optional[int] = Field(None, ge=0, le=100)
    overall_min_score: Optional[int] = Field(None, ge=0, le=100)
    enabled: Optional[bool] = None


# Endpoints
@router.post("/start")
async def start_improvement(
    request: StartImprovementRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Start automatic improvement workflow.
    
    This endpoint initiates an improvement workflow that:
    1. Audits the current code
    2. Checks if quality thresholds are met
    3. If not, generates improvement instructions
    4. Regenerates code with improvements
    5. Re-audits to verify improvements
    6. Repeats up to max_cycles times
    
    Args:
        request: Improvement request
        background_tasks: FastAPI background tasks
        db: Database session
        
    Returns:
        Workflow ID and status
    """
    try:
        logger.info(f"Starting improvement workflow for session {request.session_id}")
        
        if request.async_mode:
            # Run asynchronously using Celery
            task = improve_site_task.delay(
                html_code=request.html_code,
                session_id=request.session_id,
                workflow_id=f"improve_{request.session_id}",
                threshold_config=request.threshold_config,
                max_cycles=request.max_cycles
            )
            
            return {
                "workflow_id": task.id,
                "status": "pending",
                "message": "Improvement workflow started asynchronously",
                "async_mode": True,
                "task_id": task.id
            }
        else:
            # Run synchronously
            input_data = {
                "html_code": request.html_code,
                "threshold_config": request.threshold_config,
                "max_cycles": request.max_cycles,
            }
            
            result = await orchestrator.execute_workflow(
                workflow_type=WorkflowType.IMPROVE_SITE,
                input_data=input_data,
                session_id=request.session_id,
                user_preferences=None,
            )
            
            return {
                "workflow_id": result["workflow_id"],
                "status": result["status"],
                "result": result.get("result"),
                "metrics": result.get("metrics"),
                "async_mode": False
            }
            
    except Exception as e:
        logger.error(f"Error starting improvement workflow: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{workflow_id}")
async def get_improvement_status(workflow_id: str):
    """
    Get improvement workflow status.
    
    Args:
        workflow_id: Workflow ID
        
    Returns:
        Workflow status and progress
    """
    try:
        status = orchestrator.get_workflow_status(workflow_id)
        
        if not status:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        # Extract current cycle from logs or result
        current_cycle = None
        total_cycles = None
        
        if status.get("result"):
            result = status["result"]
            if isinstance(result, dict):
                cycles = result.get("cycles", [])
                total_cycles = len(cycles)
                # Find the last incomplete cycle
                for i, cycle in enumerate(cycles):
                    if not cycle.get("success"):
                        current_cycle = i + 1
                        break
                if current_cycle is None and cycles:
                    current_cycle = len(cycles)
        
        return ImprovementStatusResponse(
            workflow_id=workflow_id,
            status=status["status"],
            progress_percentage=status.get("progress_percentage", 0.0),
            current_cycle=current_cycle,
            total_cycles=total_cycles,
            current_agent=status.get("current_agent"),
            completed_agents=status.get("completed_agents", []),
            result=status.get("result"),
            error=status.get("error"),
            metrics=status.get("metrics")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting improvement status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/check-thresholds")
async def check_thresholds(request: ThresholdCheckRequest):
    """
    Check if audit results meet quality thresholds.
    
    Args:
        request: Threshold check request
        
    Returns:
        Threshold check results
    """
    try:
        threshold_check = orchestrator.check_quality_thresholds(
            audit_result=request.audit_result,
            threshold_config=request.threshold_config
        )
        
        return ThresholdCheckResponse(**threshold_check)
        
    except Exception as e:
        logger.error(f"Error checking thresholds: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/thresholds")
async def list_thresholds(db: Session = Depends(get_db)):
    """
    List all quality thresholds.
    
    Args:
        db: Database session
        
    Returns:
        List of quality thresholds
    """
    try:
        repo = QualityThresholdRepository(db)
        thresholds = repo.list_all()
        
        return [
            QualityThresholdResponse(**threshold.to_dict())
            for threshold in thresholds
        ]
        
    except Exception as e:
        logger.error(f"Error listing thresholds: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/thresholds/active")
async def get_active_threshold(db: Session = Depends(get_db)):
    """
    Get the active quality threshold.
    
    Args:
        db: Database session
        
    Returns:
        Active quality threshold
    """
    try:
        repo = QualityThresholdRepository(db)
        threshold = repo.get_active_threshold()
        
        if not threshold:
            raise HTTPException(status_code=404, detail="No active threshold found")
        
        return QualityThresholdResponse(**threshold.to_dict())
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting active threshold: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/thresholds/{threshold_id}")
async def update_threshold(
    threshold_id: str,
    request: UpdateThresholdRequest,
    db: Session = Depends(get_db)
):
    """
    Update quality threshold.
    
    Args:
        threshold_id: Threshold ID
        request: Update request
        db: Database session
        
    Returns:
        Updated threshold
    """
    try:
        repo = QualityThresholdRepository(db)
        
        threshold = repo.update_threshold(
            threshold_id=threshold_id,
            seo_min_score=request.seo_min_score,
            accessibility_min_score=request.accessibility_min_score,
            performance_min_score=request.performance_min_score,
            overall_min_score=request.overall_min_score,
            enabled=request.enabled
        )
        
        if not threshold:
            raise HTTPException(status_code=404, detail="Threshold not found")
        
        return QualityThresholdResponse(**threshold.to_dict())
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating threshold: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cycles/workflow/{workflow_id}")
async def get_workflow_cycles(workflow_id: str, db: Session = Depends(get_db)):
    """
    Get improvement cycles for a workflow.
    
    Args:
        workflow_id: Workflow ID
        db: Database session
        
    Returns:
        List of improvement cycles
    """
    try:
        repo = ImprovementCycleRepository(db)
        cycles = repo.get_by_workflow(workflow_id)
        
        return [cycle.to_dict() for cycle in cycles]
        
    except Exception as e:
        logger.error(f"Error getting workflow cycles: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cycles/session/{session_id}")
async def get_session_cycles(session_id: str, db: Session = Depends(get_db)):
    """
    Get improvement cycles for a session.
    
    Args:
        session_id: Session ID
        db: Database session
        
    Returns:
        List of improvement cycles
    """
    try:
        repo = ImprovementCycleRepository(db)
        cycles = repo.get_by_session(session_id)
        
        return [cycle.to_dict() for cycle in cycles]
        
    except Exception as e:
        logger.error(f"Error getting session cycles: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cycles/site/{site_id}")
async def get_site_cycles(site_id: str, db: Session = Depends(get_db)):
    """
    Get improvement cycles for a site.
    
    Args:
        site_id: Site ID
        db: Database session
        
    Returns:
        List of improvement cycles
    """
    try:
        repo = ImprovementCycleRepository(db)
        cycles = repo.get_by_site(site_id)
        
        return [cycle.to_dict() for cycle in cycles]
        
    except Exception as e:
        logger.error(f"Error getting site cycles: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
