"""
API endpoints for forms and submissions.
"""
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid
import csv
import io
from fastapi.responses import StreamingResponse

from models.forms import Form, FormSubmission
from repositories.site_repository import site_repository
from utils.logging import logger
# Assuming we have a DB session dependency, but for now I'll mock the repository interaction or use a new repository.
# I'll create a FormRepository later.

router = APIRouter()

class FormField(BaseModel):
    id: str
    type: str
    label: str
    placeholder: Optional[str] = None
    required: bool = False
    options: Optional[List[str]] = None

class FormSettings(BaseModel):
    email_to: Optional[str] = None
    success_message: str = "Thank you for your submission!"
    spam_protection: bool = True

class CreateFormRequest(BaseModel):
    site_id: str
    name: str
    fields: List[FormField]
    settings: FormSettings

class FormResponse(BaseModel):
    id: str
    site_id: str
    name: str
    fields: List[FormField]
    settings: FormSettings
    created_at: datetime

class SubmitFormRequest(BaseModel):
    data: Dict[str, Any]

class SubmissionResponse(BaseModel):
    id: str
    form_id: str
    data: Dict[str, Any]
    created_at: datetime
    spam_score: float

@router.post("/forms", response_model=FormResponse)
async def create_form(req: CreateFormRequest):
    """Create a new form."""
    # TODO: Use repository to save form
    # For now, just return a mock response
    return FormResponse(
        id=str(uuid.uuid4()),
        site_id=req.site_id,
        name=req.name,
        fields=req.fields,
        settings=req.settings,
        created_at=datetime.utcnow()
    )

@router.get("/forms/{form_id}", response_model=FormResponse)
async def get_form(form_id: str):
    """Get form configuration."""
    # TODO: Fetch from DB
    return FormResponse(
        id=form_id,
        site_id="site-123",
        name="Contact Form",
        fields=[],
        settings=FormSettings(),
        created_at=datetime.utcnow()
    )

@router.post("/forms/{form_id}/submit")
async def submit_form(form_id: str, req: SubmitFormRequest, background_tasks: BackgroundTasks):
    """Submit form data."""
    # TODO: Save submission, check spam, send email
    return {"message": "Form submitted successfully"}

@router.get("/forms/{form_id}/submissions", response_model=List[SubmissionResponse])
async def get_submissions(form_id: str):
    """Get form submissions."""
    # TODO: Fetch from DB
    return []

@router.get("/forms/{form_id}/export")
async def export_submissions(form_id: str):
    """Export submissions as CSV."""
    # TODO: Fetch and convert to CSV
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Date", "Data"])
    
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=submissions-{form_id}.csv"}
    )
