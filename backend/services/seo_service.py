"""
Service for SEO tools and generation.
"""
from typing import Dict, Any, List, Optional
import json
from datetime import datetime

from models.seo import MetaTags, SitemapItem, RobotsTxtConfig, StructuredDataType
from services.gemini_service import gemini_service
from utils.logging import logger

class SEOService:
    """Service for handling SEO operations."""

    async def generate_meta_tags(self, content: str, site_name: str) -> MetaTags:
        """
        Generate optimized meta tags based on page content using AI.
        """
        prompt = f"""
        You are an SEO expert. Generate optimized meta tags for a website page.
        
        Site Name: {site_name}
        Page Content Summary: {content[:1000]}...
        
        Generate a JSON object with the following fields:
        - title: SEO optimized title (max 60 chars)
        - description: Compelling description (max 160 chars)
        - keywords: List of 5-10 relevant keywords
        - og_title: Open Graph title
        - og_description: Open Graph description
        - twitter_title: Twitter card title
        - twitter_description: Twitter card description
        """
        
        try:
            result = await gemini_service.generate_json(prompt)
            
            return MetaTags(
                title=result.get("title", site_name),
                description=result.get("description", ""),
                keywords=result.get("keywords", []),
                og_title=result.get("og_title"),
                og_description=result.get("og_description"),
                twitter_title=result.get("twitter_title"),
                twitter_description=result.get("twitter_description")
            )
        except Exception as e:
            logger.error(f"Error generating meta tags: {e}")
            return MetaTags(
                title=site_name,
                description="Welcome to my website",
                keywords=[]
            )

    def generate_sitemap(self, base_url: str, pages: List[str]) -> str:
        """
        Generate XML sitemap.
        """
        xml = ['<?xml version="1.0" encoding="UTF-8"?>']
        xml.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
        
        for page in pages:
            url = f"{base_url.rstrip('/')}/{page.lstrip('/')}"
            xml.append('  <url>')
            xml.append(f'    <loc>{url}</loc>')
            xml.append(f'    <lastmod>{datetime.utcnow().strftime("%Y-%m-%d")}</lastmod>')
            xml.append('    <changefreq>weekly</changefreq>')
            xml.append('    <priority>0.8</priority>')
            xml.append('  </url>')
            
        xml.append('</urlset>')
        return '\n'.join(xml)

    def generate_robots_txt(self, config: RobotsTxtConfig) -> str:
        """
        Generate robots.txt content.
        """
        lines = [f"User-agent: {config.user_agent}"]
        
        for path in config.allow:
            lines.append(f"Allow: {path}")
            
        for path in config.disallow:
            lines.append(f"Disallow: {path}")
            
        if config.sitemap:
            lines.append(f"Sitemap: {config.sitemap}")
            
        return '\n'.join(lines)

    async def generate_structured_data(self, type: StructuredDataType, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate JSON-LD structured data.
        """
        # Basic validation/enhancement could happen here
        base_schema = {
            "@context": "https://schema.org",
            "@type": type.value
        }
        
        # Merge with provided data
        return {**base_schema, **data}

# Global instance
seo_service = SEOService()
