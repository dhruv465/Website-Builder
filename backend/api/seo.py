"""
API endpoints for SEO tools.
"""
from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from fastapi.responses import PlainTextResponse

from models.seo import MetaTags, RobotsTxtConfig, StructuredDataType
from services.seo_service import seo_service
from utils.logging import logger

router = APIRouter()

class GenerateMetaTagsRequest(BaseModel):
    content: str
    site_name: str

class GenerateSitemapRequest(BaseModel):
    base_url: str
    pages: List[str]

class GenerateStructuredDataRequest(BaseModel):
    type: StructuredDataType
    data: Dict[str, Any]

@router.post("/meta-tags", response_model=MetaTags)
async def generate_meta_tags(req: GenerateMetaTagsRequest):
    """Generate AI-optimized meta tags."""
    try:
        return await seo_service.generate_meta_tags(req.content, req.site_name)
    except Exception as e:
        logger.error(f"Error generating meta tags: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sitemap", response_class=PlainTextResponse)
async def generate_sitemap(req: GenerateSitemapRequest):
    """Generate XML sitemap."""
    try:
        return seo_service.generate_sitemap(req.base_url, req.pages)
    except Exception as e:
        logger.error(f"Error generating sitemap: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/robots-txt", response_class=PlainTextResponse)
async def generate_robots_txt(config: RobotsTxtConfig):
    """Generate robots.txt content."""
    try:
        return seo_service.generate_robots_txt(config)
    except Exception as e:
        logger.error(f"Error generating robots.txt: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/structured-data")
async def generate_structured_data(req: GenerateStructuredDataRequest):
    """Generate JSON-LD structured data."""
    try:
        return await seo_service.generate_structured_data(req.type, req.data)
    except Exception as e:
        logger.error(f"Error generating structured data: {e}")
        raise HTTPException(status_code=500, detail=str(e))
