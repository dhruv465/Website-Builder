"""
Workflow Integration API endpoints.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
import uuid

from agents.workflow_integration_agent import (
    WorkflowIntegrationAgent,
    WorkflowIntegrationInput,
    IntegrationType,
    IntegrationProvider,
)
from agents.base_agent import AgentContext, AgentError
from services.websocket_manager import websocket_manager
from utils.logging import logger

router = APIRouter()

# Request/Response Models

class AddIntegrationRequest(BaseModel):
    """Request to add an integration to a site."""
    integration_type: str = Field(..., description="Type of integration: payment, booking, or contact")
    provider: str = Field(..., description="Integration provider (e.g., stripe, calendly, formspree)")
    config: Dict[str, Any] = Field(default_factory=dict, description="Provider-specific configuration")
    existing_html: Optional[str] = Field(None, description="Existing HTML to integrate into")
    site_requirements: Optional[Dict[str, Any]] = Field(None, description="Site requirements for context")
    session_id: str = Field(..., description="Session ID for tracking")
    workflow_id: Optional[str] = Field(None, description="Workflow ID for tracking")


class IntegrationResponse(BaseModel):
    """Response with integration details."""
    success: bool
    integration_type: Optional[str] = None
    provider: Optional[str] = None
    code: Optional[Dict[str, Any]] = None
    setup_instructions: Optional[Dict[str, Any]] = None
    security_validation: Optional[Dict[str, Any]] = None
    integrated_html: Optional[str] = None
    confidence: float = 0.0
    workflow_id: str
    message: Optional[str] = None


class AvailableIntegrationsResponse(BaseModel):
    """Response with available integrations."""
    integrations: List[Dict[str, Any]]
    count: int


class ValidateIntegrationRequest(BaseModel):
    """Request to validate integration code."""
    integration_type: str = Field(..., description="Type of integration")
    provider: str = Field(..., description="Integration provider")
    code: Dict[str, Any] = Field(..., description="Integration code to validate")
    session_id: str = Field(..., description="Session ID for tracking")


class ValidationResponse(BaseModel):
    """Response with validation results."""
    success: bool
    is_secure: bool
    issues: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    message: Optional[str] = None


# Initialize Workflow Integration Agent
integration_agent = WorkflowIntegrationAgent()


@router.post("/add", response_model=IntegrationResponse)
async def add_integration(req: AddIntegrationRequest):
    """
    Add a workflow integration to a site.
    
    This endpoint generates integration code for third-party services
    like payment processors, booking systems, and contact forms.
    It validates security and provides setup instructions.
    
    Args:
        req: Integration request
        
    Returns:
        IntegrationResponse with integration code and instructions
    """
    try:
        # Validate input
        if not req.integration_type:
            raise HTTPException(
                status_code=400,
                detail="integration_type is required"
            )
        
        if not req.provider:
            raise HTTPException(
                status_code=400,
                detail="provider is required"
            )
        
        # Validate session ID format
        try:
            uuid.UUID(req.session_id)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid session_id format. Must be a valid UUID."
            )
        
        # Validate integration type
        try:
            integration_type = IntegrationType(req.integration_type.lower())
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid integration_type. Must be one of: {', '.join([t.value for t in IntegrationType])}"
            )
        
        # Validate provider
        try:
            provider = IntegrationProvider(req.provider.lower())
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid provider. Must be one of: {', '.join([p.value for p in IntegrationProvider])}"
            )
        
        # Generate workflow ID if not provided
        workflow_id = req.workflow_id or f"integration_{req.session_id}_{uuid.uuid4()}"
        
        # Create input for agent
        input_data = WorkflowIntegrationInput(
            integration_type=integration_type,
            provider=provider,
            config=req.config,
            existing_html=req.existing_html,
            site_requirements=req.site_requirements,
        )
        
        # Create context
        context = AgentContext(
            session_id=req.session_id,
            workflow_id=workflow_id,
        )
        
        # Execute agent
        logger.info(
            f"Generating {integration_type.value} integration with {provider.value} "
            f"for workflow {workflow_id}"
        )
        
        # Send WebSocket update
        await websocket_manager.send_workflow_update(
            workflow_id,
            {
                "type": "agent_status",
                "agent": "WorkflowIntegrationAgent",
                "status": "working",
                "message": f"Generating {integration_type.value} integration..."
            }
        )
        
        result = await integration_agent.execute_with_metrics(input_data, context)
        
        if not result.success:
            await websocket_manager.send_workflow_update(
                workflow_id,
                {
                    "type": "agent_status",
                    "agent": "WorkflowIntegrationAgent",
                    "status": "error",
                    "message": "Integration generation failed"
                }
            )
            raise HTTPException(
                status_code=500,
                detail="Failed to generate integration"
            )
        
        # Send success update
        await websocket_manager.send_workflow_update(
            workflow_id,
            {
                "type": "agent_status",
                "agent": "WorkflowIntegrationAgent",
                "status": "done",
                "message": "Integration generated successfully"
            }
        )
        
        # Build response
        integration = result.integration
        response = IntegrationResponse(
            success=True,
            integration_type=integration.integration_type.value if integration else None,
            provider=integration.provider.value if integration else None,
            code=integration.code.model_dump() if integration else None,
            setup_instructions=integration.setup_instructions.model_dump() if integration else None,
            security_validation=integration.security_validation.model_dump() if integration else None,
            integrated_html=result.integrated_html,
            confidence=result.confidence,
            workflow_id=workflow_id,
            message="Integration generated successfully"
        )
        
        logger.info(
            f"Successfully generated {integration_type.value} integration "
            f"for workflow {workflow_id}. Confidence: {result.confidence:.2f}"
        )
        
        return response
        
    except HTTPException:
        raise
    except AgentError as e:
        logger.error(f"Agent error generating integration: {e.message}")
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
        logger.error(f"Unexpected error generating integration: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while generating integration"
        )


@router.get("/available", response_model=AvailableIntegrationsResponse)
async def get_available_integrations():
    """
    Get list of available integrations.
    
    Returns information about all supported integration types and providers,
    including their configuration options and requirements.
    
    Returns:
        AvailableIntegrationsResponse with available integrations
    """
    try:
        integrations = [
            {
                "type": "payment",
                "provider": "stripe",
                "name": "Stripe Payment Integration",
                "description": "Accept credit card payments with Stripe Elements",
                "config_options": [
                    {"name": "product_name", "type": "string", "required": False, "default": "Product"},
                    {"name": "price", "type": "string", "required": False, "default": "99.99"},
                    {"name": "currency", "type": "string", "required": False, "default": "usd"},
                    {"name": "button_text", "type": "string", "required": False, "default": "Buy Now"}
                ],
                "requirements": [
                    "Stripe account",
                    "Publishable and secret API keys",
                    "Backend endpoint for payment processing"
                ]
            },
            {
                "type": "booking",
                "provider": "calendly",
                "name": "Calendly Booking Integration",
                "description": "Embed Calendly scheduling widget",
                "config_options": [
                    {"name": "calendly_url", "type": "string", "required": True},
                    {"name": "button_text", "type": "string", "required": False, "default": "Schedule a Meeting"},
                    {"name": "title", "type": "string", "required": False, "default": "Book a Meeting"},
                    {"name": "description", "type": "string", "required": False, "default": "Choose a time that works for you"}
                ],
                "requirements": [
                    "Calendly account",
                    "Event type created",
                    "Calendly scheduling link"
                ]
            },
            {
                "type": "booking",
                "provider": "custom_booking",
                "name": "Custom Booking Form",
                "description": "Custom booking form with time slot selection",
                "config_options": [
                    {"name": "title", "type": "string", "required": False, "default": "Book an Appointment"},
                    {"name": "time_slots", "type": "array", "required": False, "default": ["9:00 AM", "10:00 AM", "11:00 AM", "2:00 PM", "3:00 PM", "4:00 PM"]}
                ],
                "requirements": [
                    "Backend endpoint for booking submissions",
                    "Email notification system",
                    "Booking management system"
                ]
            },
            {
                "type": "contact",
                "provider": "formspree",
                "name": "Formspree Contact Form",
                "description": "Simple contact form powered by Formspree",
                "config_options": [
                    {"name": "form_id", "type": "string", "required": True},
                    {"name": "title", "type": "string", "required": False, "default": "Contact Us"},
                    {"name": "include_phone", "type": "boolean", "required": False, "default": True},
                    {"name": "include_recaptcha", "type": "boolean", "required": False, "default": True}
                ],
                "requirements": [
                    "Formspree account",
                    "Form created in Formspree dashboard",
                    "Form ID from Formspree"
                ]
            },
            {
                "type": "contact",
                "provider": "emailjs",
                "name": "EmailJS Contact Form",
                "description": "Contact form using EmailJS service",
                "config_options": [
                    {"name": "service_id", "type": "string", "required": True},
                    {"name": "template_id", "type": "string", "required": True},
                    {"name": "public_key", "type": "string", "required": True},
                    {"name": "title", "type": "string", "required": False, "default": "Get in Touch"}
                ],
                "requirements": [
                    "EmailJS account",
                    "Email service configured",
                    "Email template created",
                    "Service ID, Template ID, and Public Key"
                ]
            },
            {
                "type": "contact",
                "provider": "custom_smtp",
                "name": "Custom SMTP Contact Form",
                "description": "Contact form with custom SMTP backend",
                "config_options": [
                    {"name": "title", "type": "string", "required": False, "default": "Contact Form"},
                    {"name": "include_recaptcha", "type": "boolean", "required": False, "default": True}
                ],
                "requirements": [
                    "Backend endpoint for form submissions",
                    "SMTP server configuration",
                    "Email sending implementation"
                ]
            }
        ]
        
        return AvailableIntegrationsResponse(
            integrations=integrations,
            count=len(integrations)
        )
        
    except Exception as e:
        logger.error(f"Error listing available integrations: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to list available integrations"
        )


@router.post("/validate", response_model=ValidationResponse)
async def validate_integration(req: ValidateIntegrationRequest):
    """
    Validate integration code for security issues.
    
    This endpoint performs security validation on integration code,
    checking for common vulnerabilities like hardcoded API keys,
    XSS vulnerabilities, and insecure communication.
    
    Args:
        req: Validation request
        
    Returns:
        ValidationResponse with security validation results
    """
    try:
        # Validate input
        if not req.integration_type:
            raise HTTPException(
                status_code=400,
                detail="integration_type is required"
            )
        
        if not req.provider:
            raise HTTPException(
                status_code=400,
                detail="provider is required"
            )
        
        if not req.code:
            raise HTTPException(
                status_code=400,
                detail="code is required"
            )
        
        # Validate session ID format
        try:
            uuid.UUID(req.session_id)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid session_id format. Must be a valid UUID."
            )
        
        # Validate integration type
        try:
            integration_type = IntegrationType(req.integration_type.lower())
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid integration_type. Must be one of: {', '.join([t.value for t in IntegrationType])}"
            )
        
        # Validate provider
        try:
            provider = IntegrationProvider(req.provider.lower())
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid provider. Must be one of: {', '.join([p.value for p in IntegrationProvider])}"
            )
        
        # Create a mock integration for validation
        from agents.workflow_integration_agent import (
            WorkflowIntegration,
            IntegrationCode,
            SetupInstructions,
            SecurityValidation as SecurityValidationModel
        )
        
        # Build integration code from request
        integration_code = IntegrationCode(
            html_snippet=req.code.get("html_snippet", ""),
            javascript_snippet=req.code.get("javascript_snippet"),
            css_snippet=req.code.get("css_snippet"),
            dependencies=req.code.get("dependencies", [])
        )
        
        # Create mock integration
        mock_integration = WorkflowIntegration(
            integration_type=integration_type,
            provider=provider,
            code=integration_code,
            setup_instructions=SetupInstructions(),
            security_validation=SecurityValidationModel(),
            config={}
        )
        
        # Create context
        context = AgentContext(
            session_id=req.session_id,
            workflow_id=f"validate_{req.session_id}_{uuid.uuid4()}",
        )
        
        # Validate security
        logger.info(f"Validating {integration_type.value} integration security")
        security_validation = await integration_agent._validate_security(mock_integration, context)
        
        response = ValidationResponse(
            success=True,
            is_secure=security_validation.is_secure,
            issues=security_validation.issues,
            warnings=security_validation.warnings,
            recommendations=security_validation.recommendations,
            message="Security validation complete"
        )
        
        logger.info(
            f"Security validation complete. Secure: {security_validation.is_secure}, "
            f"Issues: {len(security_validation.issues)}, "
            f"Warnings: {len(security_validation.warnings)}"
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error validating integration: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while validating integration"
        )
