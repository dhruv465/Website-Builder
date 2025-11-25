"""
API endpoints for template management.
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel

from data.templates import (
    get_all_templates,
    get_template_by_id,
    get_templates_by_category,
    search_templates,
    CATEGORIES,
)

router = APIRouter()


class TemplateResponse(BaseModel):
    """Template response model."""
    id: str
    name: str
    description: str
    category: str
    tags: List[str]
    thumbnail_url: str
    preview_url: Optional[str]
    framework: str
    design_style: str
    features: List[str]
    created_at: Optional[str]
    updated_at: Optional[str]


class TemplateDetailResponse(TemplateResponse):
    """Template detail response with code."""
    html_code: str
    css_code: str
    js_code: str


class TemplateListResponse(BaseModel):
    """Template list response."""
    templates: List[TemplateResponse]
    total: int
    categories: List[str]


@router.get("/templates", response_model=TemplateListResponse)
async def list_templates(
    category: Optional[str] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search query"),
):
    """
    Get list of all templates with optional filtering.
    
    - **category**: Filter templates by category
    - **search**: Search templates by name, description, or tags
    """
    if search:
        templates = search_templates(search)
    elif category:
        if category not in CATEGORIES:
            raise HTTPException(status_code=400, detail=f"Invalid category: {category}")
        templates = get_templates_by_category(category)
    else:
        templates = get_all_templates()
    
    # Convert to response models (without code)
    template_responses = [
        TemplateResponse(
            id=t.id,
            name=t.name,
            description=t.description,
            category=t.category,
            tags=t.tags,
            thumbnail_url=t.thumbnail_url,
            preview_url=t.preview_url,
            framework=t.framework,
            design_style=t.design_style,
            features=t.features,
            created_at=t.created_at.isoformat() if t.created_at else None,
            updated_at=t.updated_at.isoformat() if t.updated_at else None,
        )
        for t in templates
    ]
    
    return TemplateListResponse(
        templates=template_responses,
        total=len(template_responses),
        categories=CATEGORIES,
    )


@router.get("/templates/{template_id}", response_model=TemplateDetailResponse)
async def get_template(template_id: str):
    """
    Get a specific template by ID including its code.
    
    - **template_id**: The ID of the template to retrieve
    """
    template = get_template_by_id(template_id)
    
    if not template:
        raise HTTPException(status_code=404, detail=f"Template not found: {template_id}")
    
    return TemplateDetailResponse(
        id=template.id,
        name=template.name,
        description=template.description,
        category=template.category,
        tags=template.tags,
        thumbnail_url=template.thumbnail_url,
        preview_url=template.preview_url,
        html_code=template.html_code,
        css_code=template.css_code,
        js_code=template.js_code,
        framework=template.framework,
        design_style=template.design_style,
        features=template.features,
        created_at=template.created_at.isoformat() if template.created_at else None,
        updated_at=template.updated_at.isoformat() if template.updated_at else None,
    )


@router.get("/templates/categories", response_model=List[str])
async def get_categories():
    """
    Get list of all template categories.
    """
    return CATEGORIES


class ApplyTemplateRequest(BaseModel):
    """Request to apply a template to a site."""
    session_id: str
    site_id: Optional[str] = None
    template_id: str
    customization: Optional[str] = None


class ApplyTemplateResponse(BaseModel):
    """Response after applying a template."""
    site_id: str
    version_id: str
    message: str


@router.post("/templates/apply", response_model=ApplyTemplateResponse)
async def apply_template(request: ApplyTemplateRequest):
    """
    Apply a template to a new or existing site.
    
    - **session_id**: User session ID
    - **site_id**: Optional site ID to apply template to (creates new if not provided)
    - **template_id**: ID of the template to apply
    - **customization**: Optional natural language customization instructions
    """
    # Get the template
    template = get_template_by_id(request.template_id)
    
    if not template:
        raise HTTPException(status_code=404, detail=f"Template not found: {request.template_id}")
    
    # TODO: Implement actual site creation/update logic
    # This would integrate with the existing workflow system
    # For now, return a placeholder response
    
    return ApplyTemplateResponse(
        site_id=request.site_id or "new-site-id",
        version_id="new-version-id",
        message=f"Template '{template.name}' applied successfully",
    )
