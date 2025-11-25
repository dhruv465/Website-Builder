"""
Celery tasks for background processing.
"""
from celery import shared_task
from datetime import datetime
import asyncio

from utils.logging import logger
from utils.config import settings


@shared_task(name="services.tasks.cleanup_old_sessions")
def cleanup_old_sessions():
    """
    Scheduled task to cleanup old sessions.
    
    Runs daily to remove sessions older than SESSION_CLEANUP_DAYS.
    """
    try:
        logger.info("Starting scheduled session cleanup")
        
        # Import here to avoid circular dependencies
        from agents.memory_agent import MemoryAgent, CleanupInput
        from agents.base_agent import AgentContext
        
        # Create Memory Agent
        memory_agent = MemoryAgent()
        
        # Create input for cleanup
        cleanup_input = CleanupInput(days=settings.SESSION_CLEANUP_DAYS)
        
        # Create context
        context = AgentContext(
            session_id="system",
            workflow_id=f"cleanup_{datetime.utcnow().isoformat()}",
        )
        
        # Execute cleanup (using sync wrapper since Celery doesn't support async)
        result = asyncio.run(memory_agent.execute(cleanup_input, context))
        
        if result.success:
            deleted_count = result.data.get("deleted_count", 0)
            logger.info(f"Session cleanup completed: {deleted_count} sessions deleted")
            return {
                "status": "success",
                "deleted_count": deleted_count,
                "timestamp": datetime.utcnow().isoformat(),
            }
        else:
            logger.error("Session cleanup failed")
            return {
                "status": "failed",
                "timestamp": datetime.utcnow().isoformat(),
            }
            
    except Exception as e:
        logger.error(f"Error in cleanup task: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat(),
        }


@shared_task(name="services.tasks.persist_workflow_logs")
def persist_workflow_logs(workflow_id: str):
    """
    Task to persist workflow logs to database.
    
    Args:
        workflow_id: Workflow ID
    """
    try:
        from services.orchestrator import orchestrator
        from models.base import SessionLocal
        
        db = SessionLocal()
        try:
            orchestrator.persist_workflow_logs(workflow_id, db)
            logger.info(f"Persisted logs for workflow {workflow_id}")
            return {
                "status": "success",
                "workflow_id": workflow_id,
                "timestamp": datetime.utcnow().isoformat(),
            }
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error persisting workflow logs: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat(),
        }


@shared_task(name="services.tasks.cleanup_old_logs")
def cleanup_old_logs():
    """
    Scheduled task to cleanup old workflow logs.
    
    Runs daily to remove logs older than 90 days.
    """
    try:
        from services.metrics_service import MetricsService
        from models.base import SessionLocal
        
        logger.info("Starting scheduled log cleanup")
        
        db = SessionLocal()
        try:
            metrics_service = MetricsService(db)
            deleted_count = metrics_service.cleanup_old_logs(days=90)
            
            logger.info(f"Log cleanup completed: {deleted_count} logs deleted")
            return {
                "status": "success",
                "deleted_count": deleted_count,
                "timestamp": datetime.utcnow().isoformat(),
            }
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error in log cleanup task: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat(),
        }


@shared_task(name="services.tasks.cleanup_old_workflows")
def cleanup_old_workflows():
    """
    Scheduled task to cleanup old workflow states from memory.
    
    Runs hourly to remove workflows older than 24 hours.
    """
    try:
        from services.orchestrator import orchestrator
        
        logger.info("Starting scheduled workflow cleanup")
        orchestrator.cleanup_old_workflows(max_age_hours=24)
        
        return {
            "status": "success",
            "timestamp": datetime.utcnow().isoformat(),
        }
        
    except Exception as e:
        logger.error(f"Error in workflow cleanup task: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat(),
        }


@shared_task(name="tasks.generate_code_task")
def generate_code_task(
    requirements: dict,
    session_id: str,
    workflow_id: str,
    template_preference: str = None
):
    """
    Async task to generate code from requirements.
    
    Args:
        requirements: Site requirements
        session_id: Session ID
        workflow_id: Workflow ID
        template_preference: Optional template preference
        
    Returns:
        Code generation result
    """
    try:
        logger.info(f"Starting code generation task for workflow {workflow_id}")
        
        from agents.code_generation_agent import CodeGenerationAgent, CodeGenerationInput
        from agents.base_agent import AgentContext
        
        # Create agent
        code_agent = CodeGenerationAgent()
        
        # Create input
        input_data = CodeGenerationInput(
            requirements=requirements,
            template_preference=template_preference,
        )
        
        # Create context
        context = AgentContext(
            session_id=session_id,
            workflow_id=workflow_id,
        )
        
        # Execute agent
        result = asyncio.run(code_agent.execute_with_metrics(input_data, context))
        
        if result.success:
            logger.info(f"Code generation task completed for workflow {workflow_id}")
            return {
                "success": True,
                "html": result.generated_code.html if result.generated_code else None,
                "metadata": result.generated_code.metadata.model_dump() if result.generated_code else None,
                "validation": result.generated_code.validation.model_dump() if result.generated_code else None,
                "confidence": result.confidence,
                "template_used": result.template_used,
                "is_modification": result.is_modification,
                "code_diff": result.code_diff.model_dump() if result.code_diff else None,
                "workflow_id": workflow_id,
                "message": "Code generated successfully"
            }
        else:
            logger.error(f"Code generation task failed for workflow {workflow_id}")
            return {
                "success": False,
                "workflow_id": workflow_id,
                "message": "Code generation failed"
            }
            
    except Exception as e:
        logger.error(f"Error in code generation task: {str(e)}")
        return {
            "success": False,
            "workflow_id": workflow_id,
            "error": str(e),
            "message": "Code generation task error"
        }


@shared_task(name="tasks.modify_code_task")
def modify_code_task(
    existing_code: str,
    modifications: list,
    requirements: dict,
    session_id: str,
    workflow_id: str
):
    """
    Async task to modify existing code.
    
    Args:
        existing_code: Existing HTML code
        modifications: List of requested modifications
        requirements: Original requirements
        session_id: Session ID
        workflow_id: Workflow ID
        
    Returns:
        Code modification result
    """
    try:
        logger.info(f"Starting code modification task for workflow {workflow_id}")
        
        from agents.code_generation_agent import CodeGenerationAgent, CodeGenerationInput
        from agents.base_agent import AgentContext
        
        # Create agent
        code_agent = CodeGenerationAgent()
        
        # Create input
        input_data = CodeGenerationInput(
            requirements=requirements,
            existing_code=existing_code,
            modifications=modifications,
        )
        
        # Create context
        context = AgentContext(
            session_id=session_id,
            workflow_id=workflow_id,
        )
        
        # Execute agent
        result = asyncio.run(code_agent.execute_with_metrics(input_data, context))
        
        if result.success:
            logger.info(f"Code modification task completed for workflow {workflow_id}")
            return {
                "success": True,
                "html": result.generated_code.html if result.generated_code else None,
                "metadata": result.generated_code.metadata.model_dump() if result.generated_code else None,
                "validation": result.generated_code.validation.model_dump() if result.generated_code else None,
                "confidence": result.confidence,
                "template_used": result.template_used,
                "is_modification": result.is_modification,
                "code_diff": result.code_diff.model_dump() if result.code_diff else None,
                "workflow_id": workflow_id,
                "message": "Code modified successfully"
            }
        else:
            logger.error(f"Code modification task failed for workflow {workflow_id}")
            return {
                "success": False,
                "workflow_id": workflow_id,
                "message": "Code modification failed"
            }
            
    except Exception as e:
        logger.error(f"Error in code modification task: {str(e)}")
        return {
            "success": False,
            "workflow_id": workflow_id,
            "error": str(e),
            "message": "Code modification task error"
        }


@shared_task(name="tasks.improve_site_task")
def improve_site_task(
    html_code: str,
    session_id: str,
    workflow_id: str,
    threshold_config: dict = None,
    max_cycles: int = 2
):
    """
    Async task to run automatic improvement workflow.
    
    Args:
        html_code: Current HTML code
        session_id: Session ID
        workflow_id: Workflow ID
        threshold_config: Optional custom threshold configuration
        max_cycles: Maximum improvement cycles (default: 2)
        
    Returns:
        Improvement workflow result
    """
    try:
        logger.info(f"Starting improvement workflow task for workflow {workflow_id}")
        
        from services.orchestrator import orchestrator, WorkflowType
        
        # Prepare input data
        input_data = {
            "html_code": html_code,
            "threshold_config": threshold_config,
            "max_cycles": max_cycles,
        }
        
        # Execute improvement workflow
        result = asyncio.run(orchestrator.execute_workflow(
            workflow_type=WorkflowType.IMPROVE_SITE,
            input_data=input_data,
            session_id=session_id,
            user_preferences=None,
        ))
        
        if result.get("status") == "completed":
            logger.info(f"Improvement workflow task completed for workflow {workflow_id}")
            return {
                "success": True,
                "workflow_id": workflow_id,
                "result": result.get("result"),
                "metrics": result.get("metrics"),
                "message": "Improvement workflow completed"
            }
        else:
            logger.error(f"Improvement workflow task failed for workflow {workflow_id}")
            return {
                "success": False,
                "workflow_id": workflow_id,
                "error": result.get("error"),
                "message": "Improvement workflow failed"
            }
            
    except Exception as e:
        logger.error(f"Error in improvement workflow task: {str(e)}")
        return {
            "success": False,
            "workflow_id": workflow_id,
            "error": str(e),
            "message": "Improvement workflow task error"
        }


@shared_task(name="services.tasks.health_check")
def health_check():
    """Health check task."""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}
