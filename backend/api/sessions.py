"""
Session management API endpoints.
"""
from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
import uuid

from agents.memory_agent import (
    MemoryAgent,
    SaveSessionInput,
    LoadSessionInput,
    SaveSiteInput,
    LoadSiteInput,
    SavePreferencesInput,
    LoadPreferencesInput,
    ExportSessionInput,
    ImportSessionInput,
)
from agents.base_agent import AgentContext, AgentError
from utils.logging import logger

router = APIRouter()

# Request/Response Models

class CreateSessionRequest(BaseModel):
    """Request to create a new session."""
    user_id: Optional[str] = None
    preferences: Dict[str, Any] = Field(default_factory=dict)


class UpdateSessionRequest(BaseModel):
    """Request to update session."""
    preferences: Dict[str, Any]


class UpdatePreferencesRequest(BaseModel):
    """Request to update user preferences."""
    default_color_scheme: Optional[str] = None
    default_site_type: Optional[str] = None
    favorite_features: Optional[List[str]] = None
    design_style: Optional[str] = None


class ExportSessionRequest(BaseModel):
    """Request to export session."""
    session_id: str
    include_sites: bool = True
    compress: bool = True


class ImportSessionRequest(BaseModel):
    """Request to import session."""
    data: str
    compressed: bool = True


# Initialize Memory Agent
memory_agent = MemoryAgent()


@router.get("/{session_id}")
async def get_session(session_id: str):
    """
    Load session data.
    
    Args:
        session_id: Session ID
        
    Returns:
        Session data with sites
    """
    try:
        # Create input
        input_data = LoadSessionInput(session_id=session_id)
        
        # Create context
        context = AgentContext(
            session_id=session_id,
            workflow_id=f"load_session_{session_id}",
        )
        
        # Execute
        result = await memory_agent.execute(input_data, context)
        
        if not result.success:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return result.data
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session ID format")
    except AgentError as e:
        if e.error_type.value == "validation_error":
            raise HTTPException(status_code=404, detail=e.message)
        raise HTTPException(status_code=500, detail=e.message)
    except Exception as e:
        logger.error(f"Error loading session: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("")
async def create_session(request: CreateSessionRequest):
    """
    Create new session.
    
    Args:
        request: Session creation request
        
    Returns:
        Created session data
    """
    try:
        # Generate new session ID
        new_session_id = str(uuid.uuid4())
        
        # Create input
        input_data = SaveSessionInput(
            session_id=new_session_id,
            user_id=request.user_id,
            preferences=request.preferences,
        )
        
        # Create context
        context = AgentContext(
            session_id=new_session_id,
            workflow_id=f"create_session_{new_session_id}",
        )
        
        # Execute
        result = await memory_agent.execute(input_data, context)
        
        if not result.success:
            raise HTTPException(status_code=500, detail="Failed to create session")
        
        return result.data
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID format")
    except AgentError as e:
        raise HTTPException(status_code=500, detail=e.message)
    except Exception as e:
        logger.error(f"Error creating session: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{session_id}")
async def update_session(session_id: str, request: UpdateSessionRequest):
    """
    Update session data.
    
    Args:
        session_id: Session ID
        request: Session update request
        
    Returns:
        Updated session data
    """
    try:
        # Create input
        input_data = SaveSessionInput(
            session_id=session_id,
            preferences=request.preferences,
        )
        
        # Create context
        context = AgentContext(
            session_id=session_id,
            workflow_id=f"update_session_{session_id}",
        )
        
        # Execute
        result = await memory_agent.execute(input_data, context)
        
        if not result.success:
            raise HTTPException(status_code=500, detail="Failed to update session")
        
        return result.data
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session ID format")
    except AgentError as e:
        if e.error_type.value == "validation_error":
            raise HTTPException(status_code=404, detail=e.message)
        raise HTTPException(status_code=500, detail=e.message)
    except Exception as e:
        logger.error(f"Error updating session: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{session_id}/preferences")
async def update_preferences(session_id: str, request: UpdatePreferencesRequest):
    """
    Update user preferences.
    
    Args:
        session_id: Session ID
        request: Preferences update request
        
    Returns:
        Updated preferences
    """
    try:
        # Create input
        input_data = SavePreferencesInput(
            session_id=session_id,
            default_color_scheme=request.default_color_scheme,
            default_site_type=request.default_site_type,
            favorite_features=request.favorite_features,
            design_style=request.design_style,
        )
        
        # Create context
        context = AgentContext(
            session_id=session_id,
            workflow_id=f"update_preferences_{session_id}",
        )
        
        # Execute
        result = await memory_agent.execute(input_data, context)
        
        if not result.success:
            raise HTTPException(status_code=500, detail="Failed to update preferences")
        
        return result.data
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session ID format")
    except AgentError as e:
        raise HTTPException(status_code=500, detail=e.message)
    except Exception as e:
        logger.error(f"Error updating preferences: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sites/{site_id}")
async def get_site(site_id: str):
    """
    Get site details.
    
    Args:
        site_id: Site ID
        
    Returns:
        Site data with versions, audits, and deployments
    """
    try:
        # Create input
        input_data = LoadSiteInput(site_id=site_id)
        
        # Create context
        context = AgentContext(
            session_id="system",
            workflow_id=f"load_site_{site_id}",
        )
        
        # Execute
        result = await memory_agent.execute(input_data, context)
        
        if not result.success:
            raise HTTPException(status_code=404, detail="Site not found")
        
        return result.data
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid site ID format")
    except AgentError as e:
        if e.error_type.value == "validation_error":
            raise HTTPException(status_code=404, detail=e.message)
        raise HTTPException(status_code=500, detail=e.message)
    except Exception as e:
        logger.error(f"Error loading site: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sites/{site_id}/versions")
async def get_site_versions(site_id: str):
    """
    Get site version history.
    
    Args:
        site_id: Site ID
        
    Returns:
        List of site versions
    """
    try:
        # Load full site data
        input_data = LoadSiteInput(site_id=site_id)
        
        # Create context
        context = AgentContext(
            session_id="system",
            workflow_id=f"load_site_versions_{site_id}",
        )
        
        # Execute
        result = await memory_agent.execute(input_data, context)
        
        if not result.success:
            raise HTTPException(status_code=404, detail="Site not found")
        
        # Return only versions
        site_data = result.data.get("site", {})
        return {"versions": site_data.get("versions", [])}
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid site ID format")
    except AgentError as e:
        if e.error_type.value == "validation_error":
            raise HTTPException(status_code=404, detail=e.message)
        raise HTTPException(status_code=500, detail=e.message)
    except Exception as e:
        logger.error(f"Error loading site versions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/export")
async def export_session(request: ExportSessionRequest):
    """
    Export session data.
    
    Args:
        request: Export request
        
    Returns:
        Exported session data (JSON or compressed)
    """
    try:
        # Create input
        input_data = ExportSessionInput(
            session_id=request.session_id,
        )
        
        # Create context
        context = AgentContext(
            session_id=request.session_id,
            workflow_id=f"export_session_{request.session_id}",
        )
        
        # Execute
        result = await memory_agent.execute(input_data, context)
        
        if not result.success:
            raise HTTPException(status_code=500, detail="Failed to export session")
        
        return result.data
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session ID format")
    except AgentError as e:
        if e.error_type.value == "validation_error":
            raise HTTPException(status_code=404, detail=e.message)
        raise HTTPException(status_code=500, detail=e.message)
    except Exception as e:
        logger.error(f"Error exporting session: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/import")
async def import_session(request: ImportSessionRequest):
    """
    Import session data.
    
    Args:
        request: Import request
        
    Returns:
        Imported session data
    """
    try:
        # Parse the data
        import json
        if request.compressed:
            session_data = request.data  # Already a string, will be decompressed by agent
        else:
            session_data = json.loads(request.data) if isinstance(request.data, str) else request.data
        
        # Create input
        input_data = ImportSessionInput(
            session_data=session_data,
        )
        
        # Create context
        context = AgentContext(
            session_id="new",
            workflow_id=f"import_session_{uuid.uuid4()}",
        )
        
        # Execute
        result = await memory_agent.execute(input_data, context)
        
        if not result.success:
            raise HTTPException(status_code=500, detail="Failed to import session")
        
        return result.data
        
    except AgentError as e:
        if e.error_type.value == "validation_error":
            raise HTTPException(status_code=400, detail=e.message)
        raise HTTPException(status_code=500, detail=e.message)
    except Exception as e:
        logger.error(f"Error importing session: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
