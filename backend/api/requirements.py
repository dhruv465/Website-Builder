"""
Requirements parsing API endpoints.
"""
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import uuid

from agents.input_agent import (
    InputAgent,
    ParseRequirementsInput,
    ClarifyRequirementsInput,
    SiteRequirements,
)
from agents.base_agent import AgentContext, AgentError
from utils.logging import logger

router = APIRouter()

# Request/Response Models

class ParseRequirementsRequest(BaseModel):
    """Request to parse user requirements."""
    raw_input: str = Field(..., description="User's description of website needs")
    input_type: str = Field(default="text", description="Type of input: 'text' or 'voice'")
    session_id: str = Field(..., description="Session ID for tracking conversation")
    conversation_history: Optional[List[Dict[str, str]]] = Field(
        default=None,
        description="Previous conversation messages"
    )


class ClarifyRequirementsRequest(BaseModel):
    """Request to handle clarifying questions."""
    session_id: str = Field(..., description="Session ID")
    user_response: str = Field(..., description="User's response to clarifying questions")
    previous_requirements: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Previously extracted partial requirements"
    )
    conversation_history: Optional[List[Dict[str, str]]] = Field(
        default=None,
        description="Conversation history"
    )


class FrameworkRecommendationResponse(BaseModel):
    """Framework recommendation response."""
    framework: str
    explanation: str
    confidence: float


class RequirementsResponse(BaseModel):
    """Response with parsed requirements."""
    success: bool
    requirements: Optional[SiteRequirements] = None
    needs_clarification: bool = False
    clarifying_questions: List[str] = Field(default_factory=list)
    conversation_id: str
    message: Optional[str] = None
    framework_recommendation: Optional[FrameworkRecommendationResponse] = None


# Initialize Input Agent
input_agent = InputAgent()


@router.post("/parse", response_model=RequirementsResponse)
async def parse_requirements(req: ParseRequirementsRequest):
    """
    Parse user input into structured requirements.
    
    This endpoint processes natural language descriptions of website needs
    and extracts structured requirements. If the input is incomplete or
    ambiguous, it returns clarifying questions.
    
    Args:
        req: Parse requirements request
        
    Returns:
        RequirementsResponse with parsed requirements or clarifying questions
    """
    try:
        # Validate input
        if not req.raw_input or len(req.raw_input.strip()) == 0:
            raise HTTPException(
                status_code=400,
                detail="raw_input cannot be empty"
            )
        
        if req.input_type not in ["text", "voice"]:
            raise HTTPException(
                status_code=400,
                detail="input_type must be 'text' or 'voice'"
            )
        
        # Validate session ID format
        try:
            uuid.UUID(req.session_id)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid session_id format. Must be a valid UUID."
            )
        
        # Create input for agent
        input_data = ParseRequirementsInput(
            raw_input=req.raw_input,
            input_type=req.input_type,
            session_id=req.session_id,
            conversation_history=req.conversation_history,
        )
        
        # Create context
        context = AgentContext(
            session_id=req.session_id,
            workflow_id=f"parse_requirements_{req.session_id}_{uuid.uuid4()}",
        )
        
        # Execute agent
        logger.info(f"Parsing requirements for session {req.session_id}")
        result = await input_agent.execute_with_metrics(input_data, context)
        
        if not result.success:
            raise HTTPException(
                status_code=500,
                detail="Failed to parse requirements"
            )
        
        # Build response
        framework_rec = None
        if result.framework_recommendation:
            framework_rec = FrameworkRecommendationResponse(
                framework=result.framework_recommendation.framework.value,
                explanation=result.framework_recommendation.explanation,
                confidence=result.framework_recommendation.confidence
            )
        
        response = RequirementsResponse(
            success=True,
            requirements=result.requirements,
            needs_clarification=result.needs_clarification,
            clarifying_questions=result.clarifying_questions or [],
            conversation_id=result.conversation_id or req.session_id,
            message="Requirements parsed successfully" if not result.needs_clarification 
                    else "Additional information needed",
            framework_recommendation=framework_rec
        )
        
        logger.info(
            f"Successfully parsed requirements for session {req.session_id}. "
            f"Needs clarification: {result.needs_clarification}"
        )
        
        return response
        
    except HTTPException:
        raise
    except AgentError as e:
        logger.error(f"Agent error parsing requirements: {e.message}")
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
        logger.error(f"Unexpected error parsing requirements: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while parsing requirements"
        )


@router.post("/clarify", response_model=RequirementsResponse)
async def clarify_requirements(req: ClarifyRequirementsRequest):
    """
    Handle user response to clarifying questions.
    
    This endpoint processes the user's response to clarifying questions
    and updates the requirements accordingly. It may return additional
    questions if more information is still needed.
    
    Args:
        req: Clarify requirements request
        
    Returns:
        RequirementsResponse with updated requirements or more questions
    """
    try:
        # Validate input
        if not req.user_response or len(req.user_response.strip()) == 0:
            raise HTTPException(
                status_code=400,
                detail="user_response cannot be empty"
            )
        
        # Validate session ID format
        try:
            uuid.UUID(req.session_id)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid session_id format. Must be a valid UUID."
            )
        
        # Create input for agent
        input_data = ClarifyRequirementsInput(
            session_id=req.session_id,
            user_response=req.user_response,
            previous_requirements=req.previous_requirements,
            conversation_history=req.conversation_history,
        )
        
        # Create context
        context = AgentContext(
            session_id=req.session_id,
            workflow_id=f"clarify_requirements_{req.session_id}_{uuid.uuid4()}",
        )
        
        # Execute agent
        logger.info(f"Processing clarification for session {req.session_id}")
        result = await input_agent.execute_with_metrics(input_data, context)
        
        if not result.success:
            raise HTTPException(
                status_code=500,
                detail="Failed to process clarification"
            )
        
        # Build response
        framework_rec = None
        if result.framework_recommendation:
            framework_rec = FrameworkRecommendationResponse(
                framework=result.framework_recommendation.framework.value,
                explanation=result.framework_recommendation.explanation,
                confidence=result.framework_recommendation.confidence
            )
        
        response = RequirementsResponse(
            success=True,
            requirements=result.requirements,
            needs_clarification=result.needs_clarification,
            clarifying_questions=result.clarifying_questions or [],
            conversation_id=result.conversation_id or req.session_id,
            message="Requirements updated successfully" if not result.needs_clarification
                    else "Additional information still needed",
            framework_recommendation=framework_rec
        )
        
        logger.info(
            f"Successfully processed clarification for session {req.session_id}. "
            f"Needs clarification: {result.needs_clarification}"
        )
        
        return response
        
    except HTTPException:
        raise
    except AgentError as e:
        logger.error(f"Agent error processing clarification: {e.message}")
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
        logger.error(f"Unexpected error processing clarification: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while processing clarification"
        )


@router.get("/conversation/{session_id}")
async def get_conversation_history(session_id: str):
    """
    Get conversation history for a session.
    
    Args:
        session_id: Session ID
        
    Returns:
        Conversation history
    """
    try:
        # Validate session ID format
        try:
            uuid.UUID(session_id)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid session_id format. Must be a valid UUID."
            )
        
        # Load conversation history from Redis
        history = input_agent._load_conversation_history(session_id)
        
        if history is None:
            return {
                "session_id": session_id,
                "conversation_history": [],
                "message": "No conversation history found"
            }
        
        return {
            "session_id": session_id,
            "conversation_history": history,
            "message": "Conversation history retrieved successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving conversation history: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve conversation history"
        )


@router.delete("/conversation/{session_id}")
async def clear_conversation_history(session_id: str):
    """
    Clear conversation history for a session.
    
    Args:
        session_id: Session ID
        
    Returns:
        Success message
    """
    try:
        # Validate session ID format
        try:
            uuid.UUID(session_id)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid session_id format. Must be a valid UUID."
            )
        
        # Clear conversation history from Redis
        key = f"conversation:{session_id}"
        input_agent.redis.delete(key)
        
        logger.info(f"Cleared conversation history for session {session_id}")
        
        return {
            "session_id": session_id,
            "message": "Conversation history cleared successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error clearing conversation history: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to clear conversation history"
        )


@router.get("/frameworks")
async def get_frameworks():
    """
    Get list of available frameworks with descriptions.
    
    Returns:
        List of frameworks with descriptions and use cases
    """
    from agents.input_agent import Framework
    
    frameworks = [
        {
            "value": Framework.VANILLA.value,
            "name": "Vanilla HTML/CSS/JS",
            "description": "Plain HTML, CSS, and JavaScript without any framework",
            "use_cases": ["Simple static sites", "Landing pages", "Minimal interactivity"],
            "pros": ["Fast load times", "No build process", "Easy deployment", "Small bundle size"],
            "cons": ["Limited scalability", "Manual DOM manipulation", "No component reusability"]
        },
        {
            "value": Framework.REACT.value,
            "name": "React",
            "description": "Popular JavaScript library for building user interfaces",
            "use_cases": ["Complex interactive UIs", "Single-page applications", "Large applications"],
            "pros": ["Component reusability", "Large ecosystem", "Strong community", "Virtual DOM"],
            "cons": ["Steeper learning curve", "Requires build tools", "Larger bundle size"]
        },
        {
            "value": Framework.VUE.value,
            "name": "Vue.js",
            "description": "Progressive JavaScript framework for building UIs",
            "use_cases": ["Progressive enhancement", "Moderate complexity", "Flexible applications"],
            "pros": ["Easy learning curve", "Good documentation", "Flexible", "Reactive data binding"],
            "cons": ["Smaller ecosystem than React", "Less corporate backing"]
        },
        {
            "value": Framework.NEXTJS.value,
            "name": "Next.js",
            "description": "React framework with server-side rendering and static generation",
            "use_cases": ["SEO-critical sites", "Blogs", "E-commerce", "Marketing sites"],
            "pros": ["Excellent SEO", "Server-side rendering", "Static generation", "API routes"],
            "cons": ["More complex setup", "Requires Node.js server", "Larger learning curve"]
        },
        {
            "value": Framework.SVELTE.value,
            "name": "Svelte",
            "description": "Compiler-based framework that generates efficient vanilla JavaScript",
            "use_cases": ["Performance-critical apps", "Smaller bundle sizes", "Reactive programming"],
            "pros": ["Smallest bundle size", "No virtual DOM", "Simple syntax", "Fast performance"],
            "cons": ["Smaller ecosystem", "Fewer resources", "Less mature tooling"]
        }
    ]
    
    return {
        "frameworks": frameworks,
        "message": "Available frameworks retrieved successfully"
    }


@router.get("/design-styles")
async def get_design_styles():
    """
    Get list of available design styles with descriptions.
    
    Returns:
        List of design styles with descriptions and characteristics
    """
    from agents.input_agent import DesignStyle
    
    design_styles = [
        {
            "value": DesignStyle.BOLD_MINIMALISM.value,
            "name": "Bold Minimalism",
            "description": "Clean layouts with striking typography and generous white space",
            "characteristics": [
                "Striking typography",
                "Generous white space",
                "Subtle accent colors",
                "Clean, uncluttered layouts"
            ],
            "best_for": ["Professional sites", "Portfolios", "Corporate websites"]
        },
        {
            "value": DesignStyle.BRUTALISM.value,
            "name": "Brutalism/Neo-Brutalism",
            "description": "Raw elements with big blocks and bold fonts",
            "characteristics": [
                "Raw, unpolished elements",
                "Big blocks and bold fonts",
                "Authentic presentation",
                "Unconventional layouts"
            ],
            "best_for": ["Creative portfolios", "Art projects", "Experimental sites"]
        },
        {
            "value": DesignStyle.FLAT_MINIMALIST.value,
            "name": "Flat Minimalist",
            "description": "Highly functional interfaces emphasizing simplicity",
            "characteristics": [
                "Flat design elements",
                "Simple color schemes",
                "Focus on usability",
                "Clean typography"
            ],
            "best_for": ["Apps", "Dashboards", "Business tools"]
        },
        {
            "value": DesignStyle.ANTI_DESIGN.value,
            "name": "Anti-Design",
            "description": "Asymmetric layouts with experimental typography",
            "characteristics": [
                "Asymmetric layouts",
                "Experimental typography",
                "Creative imperfections",
                "Breaking traditional rules"
            ],
            "best_for": ["Creative agencies", "Fashion brands", "Artistic projects"]
        },
        {
            "value": DesignStyle.VIBRANT_BLOCKS.value,
            "name": "Vibrant Blocks",
            "description": "Big blocks with vivid contrasts and vibrant colors",
            "characteristics": [
                "Big color blocks",
                "Vivid contrasts",
                "Vibrant color palettes",
                "Bold visual hierarchy"
            ],
            "best_for": ["Youth-oriented sites", "Entertainment", "Events"]
        },
        {
            "value": DesignStyle.ORGANIC_FLUID.value,
            "name": "Organic Fluid",
            "description": "Organic, fluid shapes for intuitive navigation",
            "characteristics": [
                "Organic shapes",
                "Fluid animations",
                "Asymmetrical layouts",
                "Natural flow"
            ],
            "best_for": ["Wellness sites", "Nature brands", "Creative portfolios"]
        },
        {
            "value": DesignStyle.RETRO_NOSTALGIC.value,
            "name": "Retro/Nostalgic",
            "description": "Retro elements with playful geometric shapes",
            "characteristics": [
                "Retro elements",
                "Playful geometric shapes",
                "Pastel color schemes",
                "Vintage typography"
            ],
            "best_for": ["Vintage brands", "Nostalgic products", "Retro gaming"]
        },
        {
            "value": DesignStyle.EXPERIMENTAL.value,
            "name": "Experimental",
            "description": "Experimental navigation with dynamic typography",
            "characteristics": [
                "Experimental navigation",
                "Non-traditional scrolling",
                "Dynamic typography",
                "Innovative interactions"
            ],
            "best_for": ["Tech startups", "Innovation showcases", "Cutting-edge brands"]
        }
    ]
    
    return {
        "design_styles": design_styles,
        "message": "Available design styles retrieved successfully"
    }
