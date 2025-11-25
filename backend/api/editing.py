"""
API endpoints for natural language editing.
"""
from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

from models.editing import EditCommand, SiteContext, EditResult
from services.editing_service import editing_service
from utils.logging import logger

router = APIRouter()

class ParseCommandRequest(BaseModel):
    prompt: str
    context: Optional[SiteContext] = None

class ApplyEditRequest(BaseModel):
    command: EditCommand
    context: SiteContext

@router.post("/parse", response_model=EditCommand)
async def parse_edit_command(req: ParseCommandRequest):
    """
    Parse a natural language edit request into a structured command.
    """
    try:
        return await editing_service.parse_command(req.prompt, req.context)
    except Exception as e:
        logger.error(f"Error parsing command: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/apply", response_model=EditResult)
async def apply_edit_command(req: ApplyEditRequest):
    """
    Apply an edit command to the provided site context.
    """
    try:
        return await editing_service.apply_edit(req.command, req.context)
    except Exception as e:
        logger.error(f"Error applying edit: {e}")
        raise HTTPException(status_code=500, detail=str(e))
