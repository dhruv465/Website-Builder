"""
API endpoints for export and backup.
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional

from services.export_service import export_service
from utils.logging import logger

router = APIRouter()

class ExportGitHubRequest(BaseModel):
    repo_url: str
    token: str
    html_code: str
    css_code: str
    js_code: str

class ExportZipRequest(BaseModel):
    html_code: str
    css_code: str
    js_code: str

@router.post("/zip")
async def export_zip(req: ExportZipRequest):
    """Export site as ZIP file."""
    try:
        zip_buffer = export_service.create_zip_export(
            req.html_code, 
            req.css_code, 
            req.js_code
        )
        
        return StreamingResponse(
            iter([zip_buffer.getvalue()]),
            media_type="application/zip",
            headers={"Content-Disposition": "attachment; filename=website-export.zip"}
        )
    except Exception as e:
        logger.error(f"Error exporting ZIP: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/github")
async def export_github(req: ExportGitHubRequest):
    """Export site to GitHub repository."""
    try:
        result = export_service.export_to_github(
            req.repo_url,
            req.token,
            req.html_code,
            req.css_code,
            req.js_code
        )
        return {"message": result}
    except Exception as e:
        logger.error(f"Error exporting to GitHub: {e}")
        raise HTTPException(status_code=500, detail=str(e))
