"""
Models for SEO Tools.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum

class TwitterCardType(str, Enum):
    SUMMARY = "summary"
    SUMMARY_LARGE_IMAGE = "summary_large_image"
    APP = "app"
    PLAYER = "player"

class MetaTags(BaseModel):
    """SEO Meta Tags configuration."""
    title: str = Field(..., description="Page title")
    description: str = Field(..., description="Page description")
    keywords: List[str] = Field(default_factory=list, description="SEO keywords")
    author: Optional[str] = None
    viewport: str = "width=device-width, initial-scale=1"
    robots: str = "index, follow"
    
    # Open Graph
    og_title: Optional[str] = None
    og_description: Optional[str] = None
    og_image: Optional[str] = None
    og_type: str = "website"
    og_url: Optional[str] = None
    
    # Twitter
    twitter_card: TwitterCardType = TwitterCardType.SUMMARY_LARGE_IMAGE
    twitter_title: Optional[str] = None
    twitter_description: Optional[str] = None
    twitter_image: Optional[str] = None
    twitter_creator: Optional[str] = None

class SitemapItem(BaseModel):
    """Sitemap URL entry."""
    loc: str
    lastmod: Optional[str] = None
    changefreq: Optional[str] = None
    priority: Optional[float] = None

class RobotsTxtConfig(BaseModel):
    """robots.txt configuration."""
    user_agent: str = "*"
    allow: List[str] = []
    disallow: List[str] = []
    sitemap: Optional[str] = None

class StructuredDataType(str, Enum):
    ORGANIZATION = "Organization"
    LOCAL_BUSINESS = "LocalBusiness"
    ARTICLE = "Article"
    PRODUCT = "Product"
    EVENT = "Event"
    PERSON = "Person"
    WEBSITE = "WebSite"

class StructuredDataRequest(BaseModel):
    type: StructuredDataType
    data: Dict[str, Any]
