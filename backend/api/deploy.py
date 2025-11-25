"""
Deployment API endpoints.
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import uuid

from agents.deployment_agent import (
    deployment_agent,
    DeploymentInput,
    DeploymentMetadata,
)
from agents.base_agent import AgentContext, AgentError
from repositories.site_repository import site_repository
from services.celery_app import celery_app
from services.websocket_manager import websocket_manager
from utils.logging import logger

router = APIRouter()


# Request/Response Models

class DeployRequest(BaseModel):
    """Request to deploy a site."""
    html_code: Optional[str] = Field(None, description="HTML code to deploy (for vanilla sites)")
    files: Optional[Dict[str, str]] = Field(None, description="Files to deploy (for framework sites)")
    site_name: Optional[str] = Field(None, description="Desired site name")
    site_id: Optional[str] = Field(None, description="Site ID for tracking")
    session_id: str = Field(..., description="Session ID for tracking")
    workflow_id: Optional[str] = Field(None, description="Workflow ID for tracking")
    project_id: Optional[str] = Field(None, description="Existing Vercel project ID for updates")
    environment: str = Field(default="production", description="Deployment environment")
    framework: str = Field(default="vanilla", description="Frontend framework (vanilla, react, vue, nextjs, svelte)")
    environment_variables: Optional[Dict[str, str]] = Field(None, description="Environment variables for the deployment")
    async_processing: bool = Field(default=False, description="Process asynchronously via Celery")


class DeploymentResponse(BaseModel):
    """Response with deployment information."""
    success: bool
    url: Optional[str] = None
    deployment_id: Optional[str] = None
    project_id: Optional[str] = None
    project_name: Optional[str] = None
    framework: Optional[str] = None
    build_config: Optional[Dict[str, Any]] = None
    build_time: Optional[int] = None
    is_update: bool = False
    health_check_passed: bool = False
    manual_instructions: Optional[str] = None
    workflow_id: str
    message: Optional[str] = None
    task_id: Optional[str] = None  # For async processing


class DeploymentStatusResponse(BaseModel):
    """Response for deployment status."""
    deployment_id: str
    url: str
    status: str
    framework: Optional[str] = None
    build_config: Optional[Dict[str, Any]] = None
    build_time: Optional[int] = None
    created_at: str


class DeploymentHistoryResponse(BaseModel):
    """Response with deployment history."""
    site_id: str
    deployments: List[DeploymentStatusResponse]
    total: int


class AsyncDeploymentStatusResponse(BaseModel):
    """Response for async deployment task status."""
    task_id: str
    status: str  # pending, processing, completed, failed
    result: Optional[DeploymentResponse] = None
    error: Optional[str] = None


@router.post("/deploy", response_model=DeploymentResponse)
async def deploy_site(req: DeployRequest, background_tasks: BackgroundTasks):
    """
    Deploy a site to Vercel.
    
    This endpoint deploys HTML code to Vercel, creating a new project
    or updating an existing one. It validates the HTML, deploys to Vercel,
    waits for the deployment to complete, and verifies the deployment health.
    
    Args:
        req: Deployment request
        background_tasks: FastAPI background tasks
        
    Returns:
        DeploymentResponse with deployment information
    """
    try:
        # Validate input
        if not req.html_code and not req.files:
            raise HTTPException(
                status_code=400,
                detail="Either html_code or files must be provided"
            )
        
        # Validate framework
        valid_frameworks = ["vanilla", "react", "vue", "nextjs", "svelte"]
        if req.framework.lower() not in valid_frameworks:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid framework. Must be one of: {', '.join(valid_frameworks)}"
            )
        
        # Validate session ID format
        try:
            uuid.UUID(req.session_id)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid session_id format. Must be a valid UUID."
            )
        
        # Validate site ID if provided
        if req.site_id:
            try:
                uuid.UUID(req.site_id)
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid site_id format. Must be a valid UUID."
                )
        
        # Generate workflow ID if not provided
        workflow_id = req.workflow_id or f"deploy_{req.session_id}_{uuid.uuid4()}"
        
        # Check if async processing is requested
        if req.async_processing:
            # Queue task in Celery
            task = celery_app.send_task(
                'tasks.deploy_site_task',
                args=[
                    req.html_code,
                    req.site_name,
                    req.site_id,
                    req.session_id,
                    workflow_id,
                    req.project_id,
                    req.environment,
                ]
            )
            
            logger.info(f"Queued deployment task {task.id} for workflow {workflow_id}")
            
            return DeploymentResponse(
                success=True,
                workflow_id=workflow_id,
                task_id=task.id,
                message="Deployment queued for async processing"
            )
        
        # Synchronous processing
        # Create input for agent
        input_data = DeploymentInput(
            html_code=req.html_code,
            files=req.files,
            site_name=req.site_name,
            site_id=req.site_id,
            project_id=req.project_id,
            environment=req.environment,
            framework=req.framework,
            environment_variables=req.environment_variables,
        )
        
        # Create context
        context = AgentContext(
            session_id=req.session_id,
            workflow_id=workflow_id,
        )
        
        # Execute agent
        logger.info(f"Deploying site for workflow {workflow_id}")
        
        # Send WebSocket update
        await websocket_manager.send_workflow_update(
            workflow_id,
            {
                "type": "agent_status",
                "agent": "DeploymentAgent",
                "status": "working",
                "message": "Deploying site..."
            }
        )
        
        result = await deployment_agent.execute_with_metrics(input_data, context)
        
        if not result.success:
            await websocket_manager.send_workflow_update(
                workflow_id,
                {
                    "type": "agent_status",
                    "agent": "DeploymentAgent",
                    "status": "error",
                    "message": "Deployment failed"
                }
            )
            raise HTTPException(
                status_code=500,
                detail="Failed to deploy site"
            )
        
        # Send success update
        await websocket_manager.send_workflow_update(
            workflow_id,
            {
                "type": "agent_status",
                "agent": "DeploymentAgent",
                "status": "done",
                "message": "Site deployed successfully"
            }
        )
        
        # Build response
        response = DeploymentResponse(
            success=True,
            workflow_id=workflow_id,
        )
        
        if result.deployment_metadata:
            metadata = result.deployment_metadata
            response.url = metadata.url
            response.deployment_id = metadata.deployment_id
            response.project_id = metadata.project_id
            response.project_name = metadata.project_name
            response.framework = metadata.framework
            response.build_config = metadata.build_config
            response.build_time = metadata.build_time
            response.is_update = metadata.is_update
            response.health_check_passed = metadata.health_check_passed
            response.message = f"Site deployed successfully to {metadata.url}"
        
        if result.manual_instructions:
            response.manual_instructions = result.manual_instructions
            response.message = "Automated deployment not available. Please deploy manually."
        
        logger.info(
            f"Successfully deployed site for workflow {workflow_id}. "
            f"URL: {response.url if response.url else 'N/A'}"
        )
        
        return response
        
    except HTTPException:
        raise
    except AgentError as e:
        logger.error(f"Agent error deploying site: {e.message}")
        
        # Check if we have manual instructions in context
        manual_instructions = e.context.get("manual_instructions") if e.context else None
        
        if manual_instructions:
            # Return response with manual instructions
            return DeploymentResponse(
                success=True,
                workflow_id=workflow_id,
                manual_instructions=manual_instructions,
                message="Automated deployment failed. Manual instructions provided."
            )
        
        if e.error_type.value == "validation_error":
            raise HTTPException(status_code=400, detail=e.message)
        elif e.error_type.value == "deployment_error":
            raise HTTPException(
                status_code=503,
                detail="Deployment service temporarily unavailable. Please try again."
            )
        elif e.error_type.value == "timeout_error":
            raise HTTPException(
                status_code=504,
                detail="Deployment timed out. Please try again."
            )
        else:
            raise HTTPException(status_code=500, detail=e.message)
    except Exception as e:
        logger.error(f"Unexpected error deploying site: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while deploying site"
        )


@router.get("/status/{deployment_id}", response_model=DeploymentStatusResponse)
async def get_deployment_status(deployment_id: str):
    """
    Get deployment status from Vercel.
    
    This endpoint queries Vercel for the current status of a deployment.
    
    Args:
        deployment_id: Vercel deployment ID
        
    Returns:
        DeploymentStatusResponse with deployment status
    """
    try:
        logger.info(f"Getting deployment status for {deployment_id}")
        
        # Get deployment from Vercel
        from services.vercel_client import vercel_client
        deployment = await vercel_client.get_deployment(deployment_id)
        
        # Build response
        response = DeploymentStatusResponse(
            deployment_id=deployment.id,
            url=f"https://{deployment.url}" if not deployment.url.startswith("http") else deployment.url,
            status=deployment.state.lower(),
            build_time=deployment.build_time,
            created_at=str(deployment.created_at),
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error getting deployment status: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get deployment status: {str(e)}"
        )


@router.get("/history/{site_id}", response_model=DeploymentHistoryResponse)
async def get_deployment_history(site_id: str, limit: int = 20):
    """
    Get deployment history for a site.
    
    This endpoint retrieves all deployments for a given site from the database.
    
    Args:
        site_id: Site ID
        limit: Maximum number of deployments to return (default: 20)
        
    Returns:
        DeploymentHistoryResponse with deployment history
    """
    try:
        # Validate site ID format
        try:
            site_uuid = uuid.UUID(site_id)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid site_id format. Must be a valid UUID."
            )
        
        logger.info(f"Getting deployment history for site {site_id}")
        
        # Get deployments from database
        deployments = site_repository.get_deployments_by_site(site_uuid)
        
        # Limit results
        deployments = deployments[:limit]
        
        # Build response
        deployment_list = []
        for deployment in deployments:
            deployment_list.append(
                DeploymentStatusResponse(
                    deployment_id=deployment.deployment_id,
                    url=deployment.url,
                    status=deployment.status,
                    framework=deployment.framework,
                    build_config=deployment.build_config,
                    build_time=deployment.build_time,
                    created_at=deployment.created_at.isoformat(),
                )
            )
        
        response = DeploymentHistoryResponse(
            site_id=site_id,
            deployments=deployment_list,
            total=len(deployment_list),
        )
        
        logger.info(f"Found {len(deployment_list)} deployments for site {site_id}")
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting deployment history: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to get deployment history"
        )


@router.get("/task/{task_id}", response_model=AsyncDeploymentStatusResponse)
async def get_deployment_task_status(task_id: str):
    """
    Get status of async deployment task.
    
    Args:
        task_id: Celery task ID
        
    Returns:
        AsyncDeploymentStatusResponse with task status
    """
    try:
        # Get task result from Celery
        task_result = celery_app.AsyncResult(task_id)
        
        status = task_result.status.lower()
        
        response = AsyncDeploymentStatusResponse(
            task_id=task_id,
            status=status
        )
        
        if status == "success":
            # Task completed successfully
            result_data = task_result.result
            response.result = DeploymentResponse(**result_data)
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


@router.post("/rollback/{site_id}")
async def rollback_deployment(site_id: str, deployment_id: str):
    """
    Rollback to a previous deployment.
    
    This endpoint retrieves the code from a previous deployment and
    redeploys it as a new deployment.
    
    Args:
        site_id: Site ID
        deployment_id: Deployment ID to rollback to
        
    Returns:
        DeploymentResponse with new deployment information
    """
    try:
        # Validate site ID format
        try:
            site_uuid = uuid.UUID(site_id)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid site_id format. Must be a valid UUID."
            )
        
        logger.info(f"Rolling back site {site_id} to deployment {deployment_id}")
        
        # Get the site
        site = site_repository.get_site_by_id(site_uuid)
        if not site:
            raise HTTPException(
                status_code=404,
                detail=f"Site {site_id} not found"
            )
        
        # Find the deployment to rollback to
        target_deployment = None
        for deployment in site.deployments:
            if deployment.deployment_id == deployment_id:
                target_deployment = deployment
                break
        
        if not target_deployment:
            raise HTTPException(
                status_code=404,
                detail=f"Deployment {deployment_id} not found for site {site_id}"
            )
        
        # Get the code from the deployment's version
        # Note: This assumes we have the version linked to the deployment
        # For now, we'll get the latest version as a fallback
        latest_version = site_repository.get_latest_version(site_uuid)
        if not latest_version:
            raise HTTPException(
                status_code=404,
                detail=f"No code found for site {site_id}"
            )
        
        # Create a new deployment with the old code
        input_data = DeploymentInput(
            html_code=latest_version.code,
            site_name=site.name,
            site_id=site_id,
            project_id=target_deployment.project_id,
            environment="production",
            framework=target_deployment.framework,
        )
        
        context = AgentContext(
            session_id=str(site.session_id),
            workflow_id=f"rollback_{site_id}_{uuid.uuid4()}",
        )
        
        result = await deployment_agent.execute_with_metrics(input_data, context)
        
        if not result.success:
            raise HTTPException(
                status_code=500,
                detail="Failed to rollback deployment"
            )
        
        # Build response
        response = DeploymentResponse(
            success=True,
            workflow_id=context.workflow_id,
            message=f"Successfully rolled back to deployment {deployment_id}"
        )
        
        if result.deployment_metadata:
            metadata = result.deployment_metadata
            response.url = metadata.url
            response.deployment_id = metadata.deployment_id
            response.project_id = metadata.project_id
            response.project_name = metadata.project_name
            response.framework = metadata.framework
            response.build_config = metadata.build_config
            response.build_time = metadata.build_time
            response.is_update = True
            response.health_check_passed = metadata.health_check_passed
        
        logger.info(f"Successfully rolled back site {site_id} to deployment {deployment_id}")
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error rolling back deployment: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to rollback deployment"
        )
