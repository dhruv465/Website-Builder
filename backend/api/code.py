"""
Code generation API endpoints.
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import uuid

from agents.code_generation_agent import (
    CodeGenerationAgent,
    CodeGenerationInput,
    GeneratedCode,
)
from agents.base_agent import AgentContext, AgentError
from services.celery_app import celery_app
from services.websocket_manager import websocket_manager
from utils.logging import logger

router = APIRouter()

# Request/Response Models

class GenerateCodeRequest(BaseModel):
    """Request to generate code from requirements."""
    requirements: Dict[str, Any] = Field(..., description="Site requirements from Input Agent")
    session_id: str = Field(..., description="Session ID for tracking")
    workflow_id: Optional[str] = Field(None, description="Workflow ID for tracking")
    template_preference: Optional[str] = Field(None, description="Preferred template to use")
    async_processing: bool = Field(default=False, description="Process asynchronously via Celery")


class ModifyCodeRequest(BaseModel):
    """Request to modify existing code."""
    existing_code: str = Field(..., description="Existing HTML code to modify")
    modifications: List[str] = Field(..., description="List of requested modifications")
    requirements: Dict[str, Any] = Field(..., description="Original requirements for context")
    session_id: str = Field(..., description="Session ID for tracking")
    workflow_id: Optional[str] = Field(None, description="Workflow ID for tracking")
    async_processing: bool = Field(default=False, description="Process asynchronously via Celery")


class CodeGenerationResponse(BaseModel):
    """Response with generated code."""
    success: bool
    html: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    validation: Optional[Dict[str, Any]] = None
    confidence: float = 0.0
    template_used: Optional[str] = None
    is_modification: bool = False
    code_diff: Optional[Dict[str, Any]] = None
    workflow_id: str
    message: Optional[str] = None
    task_id: Optional[str] = None  # For async processing


class CodeGenerationStatusResponse(BaseModel):
    """Response for async task status."""
    task_id: str
    status: str  # pending, processing, completed, failed
    result: Optional[CodeGenerationResponse] = None
    error: Optional[str] = None


# Initialize Code Generation Agent
code_agent = CodeGenerationAgent()


@router.post("/generate", response_model=CodeGenerationResponse)
async def generate_code(req: GenerateCodeRequest, background_tasks: BackgroundTasks):
    """
    Generate HTML code from requirements.
    
    This endpoint generates complete, production-ready HTML/CSS/JS code
    based on structured requirements. It can use templates or LLM-based
    generation depending on the site type.
    
    Args:
        req: Code generation request
        background_tasks: FastAPI background tasks
        
    Returns:
        CodeGenerationResponse with generated code
    """
    try:
        # Validate input
        if not req.requirements:
            raise HTTPException(
                status_code=400,
                detail="requirements cannot be empty"
            )
        
        # Validate session ID format
        try:
            uuid.UUID(req.session_id)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid session_id format. Must be a valid UUID."
            )
        
        # Generate workflow ID if not provided
        workflow_id = req.workflow_id or f"generate_code_{req.session_id}_{uuid.uuid4()}"
        
        # Check if async processing is requested
        if req.async_processing:
            # Queue task in Celery
            task = celery_app.send_task(
                'tasks.generate_code_task',
                args=[
                    req.requirements,
                    req.session_id,
                    workflow_id,
                    req.template_preference
                ]
            )
            
            logger.info(f"Queued code generation task {task.id} for workflow {workflow_id}")
            
            return CodeGenerationResponse(
                success=True,
                workflow_id=workflow_id,
                task_id=task.id,
                message="Code generation queued for async processing"
            )
        
        # Synchronous processing
        # Create input for agent
        input_data = CodeGenerationInput(
            requirements=req.requirements,
            template_preference=req.template_preference,
        )
        
        # Create context
        context = AgentContext(
            session_id=req.session_id,
            workflow_id=workflow_id,
        )
        
        # Execute agent
        logger.info(f"Generating code for workflow {workflow_id}")
        
        # Send WebSocket update
        await websocket_manager.send_workflow_update(
            workflow_id,
            {
                "type": "agent_status",
                "agent": "CodeGenerationAgent",
                "status": "working",
                "message": "Generating code..."
            }
        )
        
        result = await code_agent.execute_with_metrics(input_data, context)
        
        if not result.success:
            await websocket_manager.send_workflow_update(
                workflow_id,
                {
                    "type": "agent_status",
                    "agent": "CodeGenerationAgent",
                    "status": "error",
                    "message": "Code generation failed"
                }
            )
            raise HTTPException(
                status_code=500,
                detail="Failed to generate code"
            )
        
        # Send success update
        await websocket_manager.send_workflow_update(
            workflow_id,
            {
                "type": "agent_status",
                "agent": "CodeGenerationAgent",
                "status": "done",
                "message": "Code generated successfully"
            }
        )
        
        # Build response
        response = CodeGenerationResponse(
            success=True,
            html=result.generated_code.html if result.generated_code else None,
            metadata=result.generated_code.metadata.model_dump() if result.generated_code else None,
            validation=result.generated_code.validation.model_dump() if result.generated_code else None,
            confidence=result.confidence,
            template_used=result.template_used,
            is_modification=result.is_modification,
            code_diff=result.code_diff.model_dump() if result.code_diff else None,
            workflow_id=workflow_id,
            message="Code generated successfully"
        )
        
        logger.info(
            f"Successfully generated code for workflow {workflow_id}. "
            f"Confidence: {result.confidence:.2f}"
        )
        
        return response
        
    except HTTPException:
        raise
    except AgentError as e:
        logger.error(f"Agent error generating code: {e.message}")
        if e.error_type.value == "validation_error":
            raise HTTPException(status_code=400, detail=e.message)
        elif e.error_type.value == "llm_error":
            raise HTTPException(
                status_code=503,
                detail="AI service temporarily unavailable. Please try again."
            )
        else:
            raise HTTPException(status_code=500, detail=e.message)
    except Exception as e:
        logger.error(f"Unexpected error generating code: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while generating code"
        )


@router.post("/modify", response_model=CodeGenerationResponse)
async def modify_code(req: ModifyCodeRequest, background_tasks: BackgroundTasks):
    """
    Modify existing HTML code based on requested changes.
    
    This endpoint takes existing code and a list of modifications,
    then generates updated code while preserving existing functionality.
    It also provides a diff of the changes.
    
    Args:
        req: Code modification request
        background_tasks: FastAPI background tasks
        
    Returns:
        CodeGenerationResponse with modified code and diff
    """
    try:
        # Validate input
        if not req.existing_code or len(req.existing_code.strip()) == 0:
            raise HTTPException(
                status_code=400,
                detail="existing_code cannot be empty"
            )
        
        if not req.modifications or len(req.modifications) == 0:
            raise HTTPException(
                status_code=400,
                detail="modifications list cannot be empty"
            )
        
        if not req.requirements:
            raise HTTPException(
                status_code=400,
                detail="requirements cannot be empty"
            )
        
        # Validate session ID format
        try:
            uuid.UUID(req.session_id)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid session_id format. Must be a valid UUID."
            )
        
        # Generate workflow ID if not provided
        workflow_id = req.workflow_id or f"modify_code_{req.session_id}_{uuid.uuid4()}"
        
        # Check if async processing is requested
        if req.async_processing:
            # Queue task in Celery
            task = celery_app.send_task(
                'tasks.modify_code_task',
                args=[
                    req.existing_code,
                    req.modifications,
                    req.requirements,
                    req.session_id,
                    workflow_id
                ]
            )
            
            logger.info(f"Queued code modification task {task.id} for workflow {workflow_id}")
            
            return CodeGenerationResponse(
                success=True,
                workflow_id=workflow_id,
                task_id=task.id,
                message="Code modification queued for async processing"
            )
        
        # Synchronous processing
        # Create input for agent
        input_data = CodeGenerationInput(
            requirements=req.requirements,
            existing_code=req.existing_code,
            modifications=req.modifications,
        )
        
        # Create context
        context = AgentContext(
            session_id=req.session_id,
            workflow_id=workflow_id,
        )
        
        # Execute agent
        logger.info(f"Modifying code for workflow {workflow_id}")
        
        # Send WebSocket update
        await websocket_manager.send_workflow_update(
            workflow_id,
            {
                "type": "agent_status",
                "agent": "CodeGenerationAgent",
                "status": "working",
                "message": "Modifying code..."
            }
        )
        
        result = await code_agent.execute_with_metrics(input_data, context)
        
        if not result.success:
            await websocket_manager.send_workflow_update(
                workflow_id,
                {
                    "type": "agent_status",
                    "agent": "CodeGenerationAgent",
                    "status": "error",
                    "message": "Code modification failed"
                }
            )
            raise HTTPException(
                status_code=500,
                detail="Failed to modify code"
            )
        
        # Send success update
        await websocket_manager.send_workflow_update(
            workflow_id,
            {
                "type": "agent_status",
                "agent": "CodeGenerationAgent",
                "status": "done",
                "message": "Code modified successfully"
            }
        )
        
        # Build response
        response = CodeGenerationResponse(
            success=True,
            html=result.generated_code.html if result.generated_code else None,
            metadata=result.generated_code.metadata.model_dump() if result.generated_code else None,
            validation=result.generated_code.validation.model_dump() if result.generated_code else None,
            confidence=result.confidence,
            template_used=result.template_used,
            is_modification=result.is_modification,
            code_diff=result.code_diff.model_dump() if result.code_diff else None,
            workflow_id=workflow_id,
            message="Code modified successfully"
        )
        
        logger.info(
            f"Successfully modified code for workflow {workflow_id}. "
            f"Confidence: {result.confidence:.2f}, "
            f"Changes: {result.code_diff.diff_summary if result.code_diff else 'N/A'}"
        )
        
        return response
        
    except HTTPException:
        raise
    except AgentError as e:
        logger.error(f"Agent error modifying code: {e.message}")
        if e.error_type.value == "validation_error":
            raise HTTPException(status_code=400, detail=e.message)
        elif e.error_type.value == "llm_error":
            raise HTTPException(
                status_code=503,
                detail="AI service temporarily unavailable. Please try again."
            )
        else:
            raise HTTPException(status_code=500, detail=e.message)
    except Exception as e:
        logger.error(f"Unexpected error modifying code: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while modifying code"
        )


@router.get("/status/{task_id}", response_model=CodeGenerationStatusResponse)
async def get_code_generation_status(task_id: str):
    """
    Get status of async code generation task.
    
    Args:
        task_id: Celery task ID
        
    Returns:
        CodeGenerationStatusResponse with task status
    """
    try:
        # Get task result from Celery
        task_result = celery_app.AsyncResult(task_id)
        
        status = task_result.status.lower()
        
        response = CodeGenerationStatusResponse(
            task_id=task_id,
            status=status
        )
        
        if status == "success":
            # Task completed successfully
            result_data = task_result.result
            response.result = CodeGenerationResponse(**result_data)
        elif status == "failure":
            # Task failed
            response.error = str(task_result.info)
        
        return response
        
    except Exception as e:
        logger.error(f"Error getting task status: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve task status"
        )


@router.get("/templates")
async def list_templates():
    """
    List available code generation templates.
    
    Returns:
        List of available templates with descriptions
    """
    try:
        templates = []
        
        for template_name in code_agent.template_library.list_templates():
            template = code_agent.template_library.get_template(template_name)
            if template:
                templates.append({
                    "name": template.name,
                    "site_type": template.site_type,
                    "description": template.description,
                    "default_features": template.default_features,
                    "customization_points": template.customization_points
                })
        
        return {
            "templates": templates,
            "count": len(templates)
        }
        
    except Exception as e:
        logger.error(f"Error listing templates: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to list templates"
        )
