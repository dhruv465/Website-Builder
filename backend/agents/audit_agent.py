"""
Audit Agent for evaluating websites against SEO, accessibility, and performance criteria.

This agent:
- Evaluates generated websites for SEO compliance
- Checks accessibility using WCAG guidelines
- Analyzes performance metrics
- Uses Gemini for semantic quality analysis
- Generates detailed issue reports with fix suggestions
- Calculates confidence scores for each category
"""
from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field
from bs4 import BeautifulSoup
import re
from enum import Enum

from agents.base_agent import (
    BaseAgent,
    AgentInput,
    AgentOutput,
    AgentContext,
    ValidationResult,
    AgentError,
    ErrorType,
)
from models.framework import FrameworkType
from services.gemini_service import gemini_service
from utils.logging import logger


# Enums
class SeverityLevel(str, Enum):
    """Severity levels for audit issues."""
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"


class AuditCategory(str, Enum):
    """Audit categories."""
    SEO = "seo"
    ACCESSIBILITY = "accessibility"
    PERFORMANCE = "performance"


# Input Models
class AuditInput(AgentInput):
    """Input for audit agent."""
    html_code: str = Field(..., description="HTML code to audit")
    previous_audit: Optional[Dict[str, Any]] = Field(None, description="Previous audit for comparison")
    site_id: Optional[str] = Field(None, description="Site ID for storing results")
    framework: Optional[FrameworkType] = Field(None, description="Framework used for the site")


# Output Models
class AuditIssue(BaseModel):
    """Individual audit issue."""
    category: AuditCategory
    severity: SeverityLevel
    description: str
    location: Optional[str] = Field(None, description="Line number or CSS selector")
    fix_suggestion: Optional[str] = Field(None, description="Suggested fix")


class CategoryScore(BaseModel):
    """Score for a specific audit category."""
    score: int = Field(..., ge=0, le=100, description="Score from 0-100")
    summary: str = Field(..., description="Summary of findings")
    suggestions: List[str] = Field(default_factory=list, description="Improvement suggestions")
    issues: List[AuditIssue] = Field(default_factory=list, description="Detailed issues")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Confidence in assessment")


class FrameworkAuditScore(BaseModel):
    """Score for framework-specific audit."""
    score: int = Field(..., ge=0, le=100, description="Score from 0-100")
    summary: str = Field(..., description="Summary of findings")
    suggestions: List[str] = Field(default_factory=list, description="Improvement suggestions")
    issues: List[AuditIssue] = Field(default_factory=list, description="Detailed issues")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Confidence in assessment")
    framework: FrameworkType = Field(..., description="Framework being audited")


class AuditResult(BaseModel):
    """Complete audit result."""
    seo: CategoryScore
    accessibility: CategoryScore
    performance: CategoryScore
    framework_specific: Optional[FrameworkAuditScore] = Field(None, description="Framework-specific audit results")
    overall_score: int = Field(..., ge=0, le=100, description="Weighted average score")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    improvement_from_previous: Optional[int] = Field(None, description="Score improvement from previous audit")


class AuditOutput(AgentOutput):
    """Output for audit agent."""
    audit_result: Optional[AuditResult] = None


class AuditAgent(BaseAgent):
    """
    Audit Agent for evaluating website quality.
    
    Responsibilities:
    - Evaluate SEO compliance
    - Check accessibility standards
    - Analyze performance metrics
    - Generate detailed issue reports
    - Calculate confidence scores
    """
    
    def __init__(self):
        """Initialize Audit Agent."""
        super().__init__(name="AuditAgent")
        self.gemini = gemini_service
        logger.info("Audit Agent initialized")
    
    async def execute(self, input_data: AgentInput, context: AgentContext) -> AgentOutput:
        """
        Execute audit on HTML code.
        
        Args:
            input_data: Input data with HTML code
            context: Execution context
            
        Returns:
            AuditOutput with audit results
            
        Raises:
            AgentError: If audit fails
        """
        try:
            if not isinstance(input_data, AuditInput):
                raise AgentError(
                    message=f"Unsupported input type: {type(input_data).__name__}",
                    error_type=ErrorType.VALIDATION_ERROR,
                    agent_name=self.name,
                    recoverable=False,
                    retryable=False,
                )
            
            logger.info(f"Starting audit for workflow {context.workflow_id}")
            
            # Parse HTML
            try:
                soup = BeautifulSoup(input_data.html_code, 'html.parser')
            except Exception as e:
                raise AgentError(
                    message=f"Failed to parse HTML: {str(e)}",
                    error_type=ErrorType.VALIDATION_ERROR,
                    agent_name=self.name,
                    recoverable=False,
                    retryable=False,
                )
            
            # Run audits for each category
            logger.info("Running SEO audit")
            seo_score = await self._audit_seo(soup, input_data.html_code)
            
            logger.info("Running accessibility audit")
            accessibility_score = await self._audit_accessibility(soup, input_data.html_code)
            
            logger.info("Running performance audit")
            performance_score = await self._audit_performance(soup, input_data.html_code)
            
            # Run framework-specific audit if framework is specified
            framework_score = None
            if input_data.framework and input_data.framework != FrameworkType.VANILLA_HTML:
                logger.info(f"Running {input_data.framework.value} framework-specific audit")
                framework_score = await self._audit_framework_specific(
                    input_data.html_code,
                    input_data.framework
                )
            
            # Calculate overall score (weighted average)
            overall_score = self._calculate_overall_score(
                seo_score.score,
                accessibility_score.score,
                performance_score.score,
                framework_score.score if framework_score else None
            )
            
            # Calculate improvement from previous audit
            improvement = None
            if input_data.previous_audit:
                previous_overall = input_data.previous_audit.get("overall_score", 0)
                improvement = overall_score - previous_overall
            
            # Create audit result
            audit_result = AuditResult(
                seo=seo_score,
                accessibility=accessibility_score,
                performance=performance_score,
                framework_specific=framework_score,
                overall_score=overall_score,
                improvement_from_previous=improvement
            )
            
            log_msg = (
                f"Audit complete: Overall={overall_score}, SEO={seo_score.score}, "
                f"A11y={accessibility_score.score}, Perf={performance_score.score}"
            )
            if framework_score:
                log_msg += f", Framework={framework_score.score}"
            logger.info(log_msg)
            
            return AuditOutput(
                success=True,
                audit_result=audit_result,
                confidence=self._calculate_overall_confidence(audit_result),
                data={
                    "seo": seo_score.model_dump(),
                    "accessibility": accessibility_score.model_dump(),
                    "performance": performance_score.model_dump(),
                    "overall_score": overall_score,
                    "improvement_from_previous": improvement
                }
            )
            
        except AgentError:
            raise
        except Exception as e:
            logger.error(f"Audit Agent execution error: {str(e)}")
            raise AgentError(
                message=f"Audit failed: {str(e)}",
                error_type=ErrorType.UNKNOWN_ERROR,
                agent_name=self.name,
                recoverable=False,
                retryable=True,
            )
    
    async def _audit_seo(self, soup: BeautifulSoup, html_code: str) -> CategoryScore:
        """
        Audit SEO compliance.
        
        Checks:
        - Meta tags (title, description, keywords)
        - Heading hierarchy (H1, H2, etc.)
        - Image alt attributes
        - Semantic HTML usage
        - Open Graph tags
        """
        issues = []
        score = 100
        suggestions = []
        
        # Check title tag
        title_tag = soup.find('title')
        if not title_tag:
            issues.append(AuditIssue(
                category=AuditCategory.SEO,
                severity=SeverityLevel.CRITICAL,
                description="Missing <title> tag",
                location="<head>",
                fix_suggestion="Add a descriptive <title> tag in the <head> section"
            ))
            score -= 20
        elif len(title_tag.get_text().strip()) < 10:
            issues.append(AuditIssue(
                category=AuditCategory.SEO,
                severity=SeverityLevel.WARNING,
                description="Title tag is too short (less than 10 characters)",
                location="<head><title>",
                fix_suggestion="Use a descriptive title between 50-60 characters"
            ))
            score -= 5
        
        # Check meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if not meta_desc:
            issues.append(AuditIssue(
                category=AuditCategory.SEO,
                severity=SeverityLevel.CRITICAL,
                description="Missing meta description",
                location="<head>",
                fix_suggestion='Add <meta name="description" content="..."> in the <head> section'
            ))
            score -= 15
        elif meta_desc.get('content') and len(meta_desc.get('content', '').strip()) < 50:
            issues.append(AuditIssue(
                category=AuditCategory.SEO,
                severity=SeverityLevel.WARNING,
                description="Meta description is too short",
                location="<head>",
                fix_suggestion="Use a description between 150-160 characters"
            ))
            score -= 5
        
        # Check heading hierarchy
        h1_tags = soup.find_all('h1')
        if len(h1_tags) == 0:
            issues.append(AuditIssue(
                category=AuditCategory.SEO,
                severity=SeverityLevel.CRITICAL,
                description="Missing H1 heading",
                location="<body>",
                fix_suggestion="Add exactly one <h1> tag as the main page heading"
            ))
            score -= 15
        elif len(h1_tags) > 1:
            issues.append(AuditIssue(
                category=AuditCategory.SEO,
                severity=SeverityLevel.WARNING,
                description=f"Multiple H1 headings found ({len(h1_tags)})",
                location="<body>",
                fix_suggestion="Use only one <h1> tag per page"
            ))
            score -= 5
        
        # Check for proper heading hierarchy
        headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        if len(headings) < 2:
            issues.append(AuditIssue(
                category=AuditCategory.SEO,
                severity=SeverityLevel.INFO,
                description="Limited heading structure",
                location="<body>",
                fix_suggestion="Use hierarchical headings (H1-H6) to structure content"
            ))
            score -= 3
        
        # Check image alt attributes
        images = soup.find_all('img')
        images_without_alt = [img for img in images if not img.get('alt')]
        if images_without_alt:
            issues.append(AuditIssue(
                category=AuditCategory.SEO,
                severity=SeverityLevel.WARNING,
                description=f"{len(images_without_alt)} image(s) missing alt attributes",
                location="<img> tags",
                fix_suggestion="Add descriptive alt text to all images for SEO and accessibility"
            ))
            score -= min(10, len(images_without_alt) * 2)
        
        # Check for semantic HTML
        semantic_tags = soup.find_all(['header', 'nav', 'main', 'article', 'section', 'aside', 'footer'])
        if len(semantic_tags) < 3:
            issues.append(AuditIssue(
                category=AuditCategory.SEO,
                severity=SeverityLevel.INFO,
                description="Limited use of semantic HTML5 tags",
                location="<body>",
                fix_suggestion="Use semantic tags like <header>, <nav>, <main>, <article>, <section>, <footer>"
            ))
            score -= 5
        
        # Check for Open Graph tags
        og_tags = soup.find_all('meta', property=re.compile(r'^og:'))
        if len(og_tags) == 0:
            issues.append(AuditIssue(
                category=AuditCategory.SEO,
                severity=SeverityLevel.INFO,
                description="Missing Open Graph meta tags",
                location="<head>",
                fix_suggestion="Add Open Graph tags for better social media sharing"
            ))
            score -= 5
        
        # Use Gemini for semantic quality analysis
        semantic_analysis = await self._analyze_semantic_quality(soup, "SEO")
        if semantic_analysis:
            suggestions.extend(semantic_analysis.get("suggestions", []))
        
        # Ensure score is within bounds
        score = max(0, min(100, score))
        
        # Generate summary
        summary = self._generate_seo_summary(score, len(issues))
        
        # Calculate confidence
        confidence = 0.9  # High confidence for automated checks
        
        return CategoryScore(
            score=score,
            summary=summary,
            suggestions=suggestions,
            issues=issues,
            confidence=confidence
        )
    
    async def _audit_accessibility(self, soup: BeautifulSoup, html_code: str) -> CategoryScore:
        """
        Audit accessibility compliance using WCAG guidelines.
        
        Checks:
        - ARIA labels and roles
        - Color contrast (basic check)
        - Keyboard navigation support
        - Form label associations
        - Alt text for images
        - Semantic landmarks
        """
        issues = []
        score = 100
        suggestions = []
        
        # Check for ARIA labels on interactive elements
        buttons = soup.find_all('button')
        links = soup.find_all('a')
        
        buttons_without_label = [
            btn for btn in buttons 
            if not btn.get('aria-label') and not btn.get_text().strip()
        ]
        if buttons_without_label:
            issues.append(AuditIssue(
                category=AuditCategory.ACCESSIBILITY,
                severity=SeverityLevel.WARNING,
                description=f"{len(buttons_without_label)} button(s) without accessible labels",
                location="<button> tags",
                fix_suggestion="Add aria-label or text content to all buttons"
            ))
            score -= min(10, len(buttons_without_label) * 3)
        
        # Check links have descriptive text
        links_without_text = [
            link for link in links 
            if not link.get_text().strip() and not link.get('aria-label')
        ]
        if links_without_text:
            issues.append(AuditIssue(
                category=AuditCategory.ACCESSIBILITY,
                severity=SeverityLevel.CRITICAL,
                description=f"{len(links_without_text)} link(s) without accessible text",
                location="<a> tags",
                fix_suggestion="Add descriptive text or aria-label to all links"
            ))
            score -= min(15, len(links_without_text) * 5)
        
        # Check for alt text on images (accessibility perspective)
        images = soup.find_all('img')
        images_without_alt = [img for img in images if not img.get('alt')]
        if images_without_alt:
            issues.append(AuditIssue(
                category=AuditCategory.ACCESSIBILITY,
                severity=SeverityLevel.CRITICAL,
                description=f"{len(images_without_alt)} image(s) missing alt text",
                location="<img> tags",
                fix_suggestion="Add descriptive alt text to all images (use alt='' for decorative images)"
            ))
            score -= min(15, len(images_without_alt) * 3)
        
        # Check form labels
        inputs = soup.find_all('input', type=lambda t: t not in ['hidden', 'submit', 'button'])
        inputs_without_label = []
        for input_elem in inputs:
            input_id = input_elem.get('id')
            aria_label = input_elem.get('aria-label')
            aria_labelledby = input_elem.get('aria-labelledby')
            
            # Check if there's a label for this input
            has_label = False
            if input_id:
                label = soup.find('label', attrs={'for': input_id})
                if label:
                    has_label = True
            
            if not has_label and not aria_label and not aria_labelledby:
                inputs_without_label.append(input_elem)
        
        if inputs_without_label:
            issues.append(AuditIssue(
                category=AuditCategory.ACCESSIBILITY,
                severity=SeverityLevel.CRITICAL,
                description=f"{len(inputs_without_label)} form input(s) without labels",
                location="<input> tags",
                fix_suggestion="Associate each input with a <label> or add aria-label"
            ))
            score -= min(15, len(inputs_without_label) * 5)
        
        # Check for semantic landmarks
        landmarks = soup.find_all(['header', 'nav', 'main', 'aside', 'footer'])
        if len(landmarks) < 2:
            issues.append(AuditIssue(
                category=AuditCategory.ACCESSIBILITY,
                severity=SeverityLevel.WARNING,
                description="Limited use of semantic landmark elements",
                location="<body>",
                fix_suggestion="Use semantic HTML5 landmarks for better screen reader navigation"
            ))
            score -= 10
        
        # Check for main landmark
        main_tag = soup.find('main')
        if not main_tag:
            issues.append(AuditIssue(
                category=AuditCategory.ACCESSIBILITY,
                severity=SeverityLevel.WARNING,
                description="Missing <main> landmark",
                location="<body>",
                fix_suggestion="Wrap main content in a <main> tag"
            ))
            score -= 5
        
        # Check for language attribute
        html_tag = soup.find('html')
        if not html_tag or not html_tag.get('lang'):
            issues.append(AuditIssue(
                category=AuditCategory.ACCESSIBILITY,
                severity=SeverityLevel.WARNING,
                description="Missing lang attribute on <html> tag",
                location="<html>",
                fix_suggestion='Add lang="en" (or appropriate language) to <html> tag'
            ))
            score -= 5
        
        # Check for skip navigation link
        skip_link = soup.find('a', href='#main') or soup.find('a', href='#content')
        if not skip_link:
            issues.append(AuditIssue(
                category=AuditCategory.ACCESSIBILITY,
                severity=SeverityLevel.INFO,
                description="No skip navigation link found",
                location="<body>",
                fix_suggestion="Add a skip link at the beginning of the page for keyboard users"
            ))
            score -= 3
        
        # Check for ARIA roles on custom interactive elements
        divs_with_click = soup.find_all('div', onclick=True)
        if divs_with_click:
            issues.append(AuditIssue(
                category=AuditCategory.ACCESSIBILITY,
                severity=SeverityLevel.WARNING,
                description=f"{len(divs_with_click)} non-semantic clickable element(s)",
                location="<div> with onclick",
                fix_suggestion="Use <button> instead of <div> for clickable elements, or add role='button'"
            ))
            score -= min(10, len(divs_with_click) * 3)
        
        # Use Gemini for semantic quality analysis
        semantic_analysis = await self._analyze_semantic_quality(soup, "Accessibility")
        if semantic_analysis:
            suggestions.extend(semantic_analysis.get("suggestions", []))
        
        # Ensure score is within bounds
        score = max(0, min(100, score))
        
        # Generate summary
        summary = self._generate_accessibility_summary(score, len(issues))
        
        # Calculate confidence
        confidence = 0.85  # Slightly lower confidence as some checks are heuristic
        
        return CategoryScore(
            score=score,
            summary=summary,
            suggestions=suggestions,
            issues=issues,
            confidence=confidence
        )
    
    async def _audit_performance(self, soup: BeautifulSoup, html_code: str) -> CategoryScore:
        """
        Audit performance metrics.
        
        Checks:
        - Resource count and size estimation
        - Image optimization (format, lazy loading)
        - CSS/JS minification potential
        - Render-blocking resources
        - Font loading strategy
        """
        issues = []
        score = 100
        suggestions = []
        
        # Count resources
        scripts = soup.find_all('script')
        stylesheets = soup.find_all('link', rel='stylesheet')
        images = soup.find_all('img')
        
        # Check number of external scripts
        external_scripts = [s for s in scripts if s.get('src')]
        if len(external_scripts) > 10:
            issues.append(AuditIssue(
                category=AuditCategory.PERFORMANCE,
                severity=SeverityLevel.WARNING,
                description=f"High number of external scripts ({len(external_scripts)})",
                location="<script> tags",
                fix_suggestion="Consider bundling scripts or using async/defer attributes"
            ))
            score -= 10
        
        # Check for async/defer on scripts
        blocking_scripts = [
            s for s in external_scripts 
            if not s.get('async') and not s.get('defer')
        ]
        if blocking_scripts:
            issues.append(AuditIssue(
                category=AuditCategory.PERFORMANCE,
                severity=SeverityLevel.WARNING,
                description=f"{len(blocking_scripts)} render-blocking script(s)",
                location="<script> tags",
                fix_suggestion="Add async or defer attributes to non-critical scripts"
            ))
            score -= min(15, len(blocking_scripts) * 3)
        
        # Check for lazy loading on images
        images_without_lazy = [
            img for img in images 
            if not img.get('loading') == 'lazy' and img.get('src')
        ]
        if len(images_without_lazy) > 3:
            issues.append(AuditIssue(
                category=AuditCategory.PERFORMANCE,
                severity=SeverityLevel.INFO,
                description=f"{len(images_without_lazy)} image(s) without lazy loading",
                location="<img> tags",
                fix_suggestion='Add loading="lazy" to images below the fold'
            ))
            score -= min(10, len(images_without_lazy) * 2)
        
        # Check for large inline styles or scripts
        inline_styles = soup.find_all('style')
        large_inline_styles = [
            style for style in inline_styles 
            if len(style.get_text()) > 5000
        ]
        if large_inline_styles:
            issues.append(AuditIssue(
                category=AuditCategory.PERFORMANCE,
                severity=SeverityLevel.WARNING,
                description=f"{len(large_inline_styles)} large inline style block(s)",
                location="<style> tags",
                fix_suggestion="Consider extracting large CSS to external files"
            ))
            score -= 10
        
        inline_scripts = [s for s in scripts if not s.get('src') and len(s.get_text()) > 1000]
        if inline_scripts:
            issues.append(AuditIssue(
                category=AuditCategory.PERFORMANCE,
                severity=SeverityLevel.INFO,
                description=f"{len(inline_scripts)} large inline script(s)",
                location="<script> tags",
                fix_suggestion="Consider extracting large JavaScript to external files"
            ))
            score -= 5
        
        # Check for font loading optimization
        font_links = soup.find_all('link', href=re.compile(r'fonts\.googleapis\.com|fonts\.gstatic\.com'))
        if font_links:
            preconnect_links = soup.find_all('link', rel='preconnect')
            has_font_preconnect = any(
                'fonts.googleapis.com' in link.get('href', '') or 'fonts.gstatic.com' in link.get('href', '')
                for link in preconnect_links
            )
            if not has_font_preconnect:
                issues.append(AuditIssue(
                    category=AuditCategory.PERFORMANCE,
                    severity=SeverityLevel.INFO,
                    description="Missing preconnect for Google Fonts",
                    location="<head>",
                    fix_suggestion='Add <link rel="preconnect" href="https://fonts.googleapis.com"> for faster font loading'
                ))
                score -= 5
        
        # Check for excessive DOM size
        all_elements = soup.find_all()
        if len(all_elements) > 1500:
            issues.append(AuditIssue(
                category=AuditCategory.PERFORMANCE,
                severity=SeverityLevel.WARNING,
                description=f"Large DOM size ({len(all_elements)} elements)",
                location="<body>",
                fix_suggestion="Simplify page structure to reduce DOM size"
            ))
            score -= 10
        
        # Check for image format optimization hints
        jpg_images = [img for img in images if img.get('src', '').lower().endswith(('.jpg', '.jpeg'))]
        if len(jpg_images) > 5:
            issues.append(AuditIssue(
                category=AuditCategory.PERFORMANCE,
                severity=SeverityLevel.INFO,
                description=f"{len(jpg_images)} JPEG image(s) detected",
                location="<img> tags",
                fix_suggestion="Consider using modern formats like WebP for better compression"
            ))
            score -= 3
        
        # Check for viewport meta tag (affects mobile performance)
        viewport_meta = soup.find('meta', attrs={'name': 'viewport'})
        if not viewport_meta:
            issues.append(AuditIssue(
                category=AuditCategory.PERFORMANCE,
                severity=SeverityLevel.WARNING,
                description="Missing viewport meta tag",
                location="<head>",
                fix_suggestion='Add <meta name="viewport" content="width=device-width, initial-scale=1.0">'
            ))
            score -= 10
        
        # Use Gemini for semantic quality analysis
        semantic_analysis = await self._analyze_semantic_quality(soup, "Performance")
        if semantic_analysis:
            suggestions.extend(semantic_analysis.get("suggestions", []))
        
        # Ensure score is within bounds
        score = max(0, min(100, score))
        
        # Generate summary
        summary = self._generate_performance_summary(score, len(issues))
        
        # Calculate confidence
        confidence = 0.8  # Lower confidence as we can't measure actual load times
        
        return CategoryScore(
            score=score,
            summary=summary,
            suggestions=suggestions,
            issues=issues,
            confidence=confidence
        )
    
    async def _analyze_semantic_quality(
        self,
        soup: BeautifulSoup,
        category: str
    ) -> Optional[Dict[str, Any]]:
        """
        Use Gemini to analyze semantic quality of the HTML.
        
        Args:
            soup: Parsed HTML
            category: Category being analyzed (SEO, Accessibility, Performance)
            
        Returns:
            Dictionary with suggestions or None if analysis fails
        """
        try:
            # Extract key content for analysis
            title = soup.find('title')
            title_text = title.get_text() if title else "No title"
            
            headings = soup.find_all(['h1', 'h2', 'h3'])
            heading_texts = [h.get_text().strip() for h in headings[:5]]
            
            # Build prompt for semantic analysis
            prompt = f"""Analyze the following HTML content for {category} quality and provide 2-3 specific, actionable suggestions for improvement.

Title: {title_text}
Headings: {', '.join(heading_texts) if heading_texts else 'None'}

Focus on {category}-specific improvements. Be concise and specific.

Respond with a JSON object containing a "suggestions" array of strings.
Example: {{"suggestions": ["Add more descriptive meta description", "Improve heading hierarchy"]}}
"""
            
            # Call Gemini with low temperature for consistency
            response = await self.gemini.generate_json(
                prompt=prompt,
                temperature=0.3,
            )
            
            return response
            
        except Exception as e:
            logger.warning(f"Semantic quality analysis failed: {str(e)}")
            return None
    
    def _calculate_overall_score(
        self,
        seo_score: int,
        accessibility_score: int,
        performance_score: int,
        framework_score: Optional[int] = None
    ) -> int:
        """
        Calculate weighted average overall score.
        
        Weights (without framework):
        - SEO: 30%
        - Accessibility: 40% (most important)
        - Performance: 30%
        
        Weights (with framework):
        - SEO: 25%
        - Accessibility: 35%
        - Performance: 25%
        - Framework: 15%
        """
        if framework_score is not None:
            weighted_score = (
                seo_score * 0.25 +
                accessibility_score * 0.35 +
                performance_score * 0.25 +
                framework_score * 0.15
            )
        else:
            weighted_score = (
                seo_score * 0.3 +
                accessibility_score * 0.4 +
                performance_score * 0.3
            )
        return int(round(weighted_score))
    
    def _calculate_overall_confidence(self, audit_result: AuditResult) -> float:
        """Calculate overall confidence score."""
        confidences = [
            audit_result.seo.confidence,
            audit_result.accessibility.confidence,
            audit_result.performance.confidence
        ]
        return sum(confidences) / len(confidences)
    
    def _generate_seo_summary(self, score: int, issue_count: int) -> str:
        """Generate summary for SEO audit."""
        if score >= 90:
            return f"Excellent SEO optimization with {issue_count} minor issue(s)"
        elif score >= 75:
            return f"Good SEO practices with {issue_count} issue(s) to address"
        elif score >= 60:
            return f"Moderate SEO optimization with {issue_count} issue(s) requiring attention"
        else:
            return f"Poor SEO optimization with {issue_count} critical issue(s)"
    
    def _generate_accessibility_summary(self, score: int, issue_count: int) -> str:
        """Generate summary for accessibility audit."""
        if score >= 90:
            return f"Excellent accessibility with {issue_count} minor issue(s)"
        elif score >= 80:
            return f"Good accessibility with {issue_count} issue(s) to address"
        elif score >= 65:
            return f"Moderate accessibility with {issue_count} issue(s) requiring attention"
        else:
            return f"Poor accessibility with {issue_count} critical issue(s)"
    
    def _generate_performance_summary(self, score: int, issue_count: int) -> str:
        """Generate summary for performance audit."""
        if score >= 90:
            return f"Excellent performance optimization with {issue_count} minor issue(s)"
        elif score >= 75:
            return f"Good performance with {issue_count} issue(s) to address"
        elif score >= 60:
            return f"Moderate performance with {issue_count} issue(s) requiring attention"
        else:
            return f"Poor performance with {issue_count} critical issue(s)"
    
    async def _audit_framework_specific(
        self,
        code: str,
        framework: FrameworkType
    ) -> FrameworkAuditScore:
        """
        Run framework-specific audit checks.
        
        Args:
            code: Source code to audit
            framework: Framework type
            
        Returns:
            FrameworkAuditScore with framework-specific results
        """
        if framework == FrameworkType.REACT:
            return await self._audit_react(code)
        elif framework == FrameworkType.VUE:
            return await self._audit_vue(code)
        elif framework == FrameworkType.NEXTJS:
            return await self._audit_nextjs(code)
        elif framework == FrameworkType.SVELTE:
            return await self._audit_svelte(code)
        else:
            # Return perfect score for vanilla HTML (no framework-specific checks)
            return FrameworkAuditScore(
                score=100,
                summary="No framework-specific checks for vanilla HTML",
                framework=framework,
                confidence=1.0
            )
    
    async def _audit_react(self, code: str) -> FrameworkAuditScore:
        """
        Audit React-specific best practices.
        
        Checks:
        - Hooks rules (no hooks in conditionals/loops)
        - Proper key props in lists
        - State management patterns
        - Unnecessary re-renders
        - Error boundaries
        """
        issues = []
        score = 100
        suggestions = []
        
        # Check for key props in map/list rendering
        if '.map(' in code and 'key=' not in code:
            issues.append(AuditIssue(
                category=AuditCategory.PERFORMANCE,
                severity=SeverityLevel.CRITICAL,
                description="Missing key props in list rendering",
                location="Array.map() calls",
                fix_suggestion="Add unique key prop to each element in .map(): <Component key={item.id} />"
            ))
            score -= 20
        
        # Check for hooks in conditionals (basic pattern check)
        if re.search(r'if\s*\([^)]*\)\s*{[^}]*use[A-Z]', code):
            issues.append(AuditIssue(
                category=AuditCategory.PERFORMANCE,
                severity=SeverityLevel.CRITICAL,
                description="Hooks called conditionally (violates Rules of Hooks)",
                location="Conditional blocks",
                fix_suggestion="Move hooks to the top level of the component, before any conditionals"
            ))
            score -= 25
        
        # Check for useState with objects (potential unnecessary re-renders)
        if 'useState({' in code or 'useState([' in code:
            issues.append(AuditIssue(
                category=AuditCategory.PERFORMANCE,
                severity=SeverityLevel.INFO,
                description="useState with object/array detected",
                location="useState declarations",
                fix_suggestion="Consider using multiple useState calls or useReducer for complex state"
            ))
            score -= 5
        
        # Check for inline function definitions in JSX (performance issue)
        inline_functions = len(re.findall(r'onClick=\{[^}]*=>', code))
        if inline_functions > 3:
            issues.append(AuditIssue(
                category=AuditCategory.PERFORMANCE,
                severity=SeverityLevel.WARNING,
                description=f"{inline_functions} inline arrow functions in JSX",
                location="Event handlers",
                fix_suggestion="Use useCallback or define functions outside JSX to prevent unnecessary re-renders"
            ))
            score -= min(15, inline_functions * 2)
        
        # Check for error boundaries
        if 'componentDidCatch' not in code and 'ErrorBoundary' not in code:
            issues.append(AuditIssue(
                category=AuditCategory.PERFORMANCE,
                severity=SeverityLevel.INFO,
                description="No error boundary detected",
                location="Component structure",
                fix_suggestion="Wrap components with ErrorBoundary to handle runtime errors gracefully"
            ))
            score -= 5
        
        # Check for proper dependency arrays in useEffect
        if 'useEffect(' in code:
            # Check for missing dependency arrays
            if re.search(r'useEffect\([^)]+\)\s*(?!,)', code):
                issues.append(AuditIssue(
                    category=AuditCategory.PERFORMANCE,
                    severity=SeverityLevel.WARNING,
                    description="useEffect without dependency array",
                    location="useEffect hooks",
                    fix_suggestion="Add dependency array to useEffect to control when it runs"
                ))
                score -= 10
        
        # Check for memo/useMemo usage for expensive computations
        if 'filter(' in code or 'sort(' in code or 'reduce(' in code:
            if 'useMemo' not in code:
                issues.append(AuditIssue(
                    category=AuditCategory.PERFORMANCE,
                    severity=SeverityLevel.INFO,
                    description="Expensive computations without useMemo",
                    location="Array operations",
                    fix_suggestion="Consider wrapping expensive computations in useMemo"
                ))
                score -= 5
        
        # Use Gemini for deeper React analysis
        try:
            prompt = f"""Analyze this React code for best practices and common issues:

{code[:2000]}  # Limit code length

Focus on:
1. Component structure and organization
2. State management patterns
3. Performance optimization opportunities
4. React-specific anti-patterns

Provide 2-3 specific, actionable suggestions.
Respond with JSON: {{"suggestions": ["suggestion1", "suggestion2"]}}
"""
            
            analysis = await self.gemini.generate_json(prompt=prompt, temperature=0.3)
            if analysis and 'suggestions' in analysis:
                suggestions.extend(analysis['suggestions'])
        except Exception as e:
            logger.warning(f"React semantic analysis failed: {str(e)}")
        
        # Ensure score is within bounds
        score = max(0, min(100, score))
        
        # Generate summary
        summary = self._generate_framework_summary("React", score, len(issues))
        
        return FrameworkAuditScore(
            score=score,
            summary=summary,
            suggestions=suggestions,
            issues=issues,
            confidence=0.85,
            framework=FrameworkType.REACT
        )
    
    async def _audit_vue(self, code: str) -> FrameworkAuditScore:
        """
        Audit Vue-specific best practices.
        
        Checks:
        - Proper v-for key bindings
        - Reactivity patterns
        - Component lifecycle usage
        - Memory leaks in watchers
        - Component communication patterns
        """
        issues = []
        score = 100
        suggestions = []
        
        # Check for v-for without key
        if 'v-for=' in code and ':key=' not in code and 'v-bind:key=' not in code:
            issues.append(AuditIssue(
                category=AuditCategory.PERFORMANCE,
                severity=SeverityLevel.CRITICAL,
                description="v-for without :key binding",
                location="v-for directives",
                fix_suggestion="Add :key binding to v-for: <div v-for='item in items' :key='item.id'>"
            ))
            score -= 20
        
        # Check for proper watcher cleanup
        if '$watch(' in code or 'watch(' in code:
            if 'unwatch' not in code and 'onUnmounted' not in code and 'beforeDestroy' not in code:
                issues.append(AuditIssue(
                    category=AuditCategory.PERFORMANCE,
                    severity=SeverityLevel.WARNING,
                    description="Watchers without cleanup (potential memory leak)",
                    location="watch() calls",
                    fix_suggestion="Store watcher return value and call it in onUnmounted/beforeDestroy"
                ))
                score -= 15
        
        # Check for reactive() vs ref() usage
        if 'reactive({' in code and 'ref(' not in code:
            issues.append(AuditIssue(
                category=AuditCategory.PERFORMANCE,
                severity=SeverityLevel.INFO,
                description="Using only reactive() without ref()",
                location="Composition API",
                fix_suggestion="Consider using ref() for primitive values for better reactivity tracking"
            ))
            score -= 5
        
        # Check for proper component communication
        if '$emit(' in code:
            # Check if emits option is defined
            if 'emits:' not in code and 'defineEmits' not in code:
                issues.append(AuditIssue(
                    category=AuditCategory.PERFORMANCE,
                    severity=SeverityLevel.WARNING,
                    description="Using $emit without declaring emits",
                    location="Component events",
                    fix_suggestion="Declare emits in component options or use defineEmits() in <script setup>"
                ))
                score -= 10
        
        # Check for v-if with v-for (anti-pattern)
        if re.search(r'v-for=[^>]*v-if=|v-if=[^>]*v-for=', code):
            issues.append(AuditIssue(
                category=AuditCategory.PERFORMANCE,
                severity=SeverityLevel.WARNING,
                description="v-if and v-for on same element (anti-pattern)",
                location="Template directives",
                fix_suggestion="Use computed property to filter list or wrap with template element"
            ))
            score -= 15
        
        # Check for proper props validation
        if 'props:' in code or 'defineProps' in code:
            # Basic check for type validation
            if 'type:' not in code and 'PropType' not in code:
                issues.append(AuditIssue(
                    category=AuditCategory.PERFORMANCE,
                    severity=SeverityLevel.INFO,
                    description="Props without type validation",
                    location="Props definition",
                    fix_suggestion="Add type validation to props for better type safety"
                ))
                score -= 5
        
        # Check for Composition API vs Options API consistency
        has_composition = 'setup(' in code or '<script setup>' in code
        has_options = 'data()' in code or 'methods:' in code
        if has_composition and has_options:
            issues.append(AuditIssue(
                category=AuditCategory.PERFORMANCE,
                severity=SeverityLevel.INFO,
                description="Mixing Composition API and Options API",
                location="Component structure",
                fix_suggestion="Use consistent API style (prefer Composition API for new code)"
            ))
            score -= 5
        
        # Use Gemini for deeper Vue analysis
        try:
            prompt = f"""Analyze this Vue code for best practices and common issues:

{code[:2000]}

Focus on:
1. Reactivity patterns
2. Component lifecycle management
3. Performance optimization
4. Vue-specific anti-patterns

Provide 2-3 specific, actionable suggestions.
Respond with JSON: {{"suggestions": ["suggestion1", "suggestion2"]}}
"""
            
            analysis = await self.gemini.generate_json(prompt=prompt, temperature=0.3)
            if analysis and 'suggestions' in analysis:
                suggestions.extend(analysis['suggestions'])
        except Exception as e:
            logger.warning(f"Vue semantic analysis failed: {str(e)}")
        
        # Ensure score is within bounds
        score = max(0, min(100, score))
        
        # Generate summary
        summary = self._generate_framework_summary("Vue", score, len(issues))
        
        return FrameworkAuditScore(
            score=score,
            summary=summary,
            suggestions=suggestions,
            issues=issues,
            confidence=0.85,
            framework=FrameworkType.VUE
        )
    
    async def _audit_nextjs(self, code: str) -> FrameworkAuditScore:
        """
        Audit Next.js-specific best practices.
        
        Checks:
        - App Router structure
        - Server vs client components
        - Metadata configuration
        - Image optimization with next/image
        - Data fetching patterns
        - API route security
        """
        issues = []
        score = 100
        suggestions = []
        
        # Check for proper metadata export
        if 'page.' in code or 'layout.' in code:
            if 'export const metadata' not in code and 'generateMetadata' not in code:
                issues.append(AuditIssue(
                    category=AuditCategory.SEO,
                    severity=SeverityLevel.WARNING,
                    description="Missing metadata export in page/layout",
                    location="Page/Layout component",
                    fix_suggestion="Export metadata object or generateMetadata function for SEO"
                ))
                score -= 15
        
        # Check for next/image usage
        if '<img' in code and 'next/image' not in code:
            issues.append(AuditIssue(
                category=AuditCategory.PERFORMANCE,
                severity=SeverityLevel.WARNING,
                description="Using <img> instead of next/image",
                location="Image elements",
                fix_suggestion="Use next/image Image component for automatic optimization"
            ))
            score -= 10
        
        # Check for 'use client' directive usage
        if "'use client'" in code or '"use client"' in code:
            # Check if it's actually needed (has client-side features)
            has_client_features = any(x in code for x in ['useState', 'useEffect', 'onClick', 'onChange'])
            if not has_client_features:
                issues.append(AuditIssue(
                    category=AuditCategory.PERFORMANCE,
                    severity=SeverityLevel.INFO,
                    description="'use client' directive without client-side features",
                    location="Component top",
                    fix_suggestion="Remove 'use client' if component doesn't need client-side interactivity"
                ))
                score -= 5
        
        # Check for proper data fetching patterns
        if 'fetch(' in code:
            # Check for caching configuration
            if 'cache:' not in code and 'revalidate' not in code:
                issues.append(AuditIssue(
                    category=AuditCategory.PERFORMANCE,
                    severity=SeverityLevel.INFO,
                    description="fetch() without cache configuration",
                    location="Data fetching",
                    fix_suggestion="Add cache or revalidate options to fetch() for better performance"
                ))
                score -= 5
        
        # Check for API route security
        if 'route.' in code or 'api/' in code:
            # Check for request validation
            if 'POST' in code or 'PUT' in code or 'DELETE' in code:
                if 'headers' not in code and 'authorization' not in code.lower():
                    issues.append(AuditIssue(
                        category=AuditCategory.PERFORMANCE,
                        severity=SeverityLevel.CRITICAL,
                        description="API route without authentication/authorization",
                        location="API route handler",
                        fix_suggestion="Add authentication and authorization checks to API routes"
                    ))
                    score -= 20
        
        # Check for proper loading states
        if 'loading.' in code:
            # Good practice - using loading.js
            pass
        elif 'Suspense' not in code and 'async' in code:
            issues.append(AuditIssue(
                category=AuditCategory.PERFORMANCE,
                severity=SeverityLevel.INFO,
                description="Async component without Suspense boundary",
                location="Async components",
                fix_suggestion="Wrap async components with Suspense for better loading UX"
            ))
            score -= 5
        
        # Check for proper error handling
        if 'error.' not in code and 'ErrorBoundary' not in code:
            issues.append(AuditIssue(
                category=AuditCategory.PERFORMANCE,
                severity=SeverityLevel.INFO,
                description="No error boundary detected",
                location="Component structure",
                fix_suggestion="Add error.js file or ErrorBoundary for better error handling"
            ))
            score -= 5
        
        # Check for dynamic imports for code splitting
        if 'import(' not in code and 'dynamic(' not in code:
            # Check if there are large components that could be lazy loaded
            if code.count('function') > 5 or code.count('const') > 10:
                issues.append(AuditIssue(
                    category=AuditCategory.PERFORMANCE,
                    severity=SeverityLevel.INFO,
                    description="No dynamic imports detected",
                    location="Component imports",
                    fix_suggestion="Consider using dynamic imports for large components to reduce bundle size"
                ))
                score -= 5
        
        # Use Gemini for deeper Next.js analysis
        try:
            prompt = f"""Analyze this Next.js code for best practices and common issues:

{code[:2000]}

Focus on:
1. App Router patterns
2. Server vs Client component usage
3. Performance optimization
4. SEO and metadata
5. Security in API routes

Provide 2-3 specific, actionable suggestions.
Respond with JSON: {{"suggestions": ["suggestion1", "suggestion2"]}}
"""
            
            analysis = await self.gemini.generate_json(prompt=prompt, temperature=0.3)
            if analysis and 'suggestions' in analysis:
                suggestions.extend(analysis['suggestions'])
        except Exception as e:
            logger.warning(f"Next.js semantic analysis failed: {str(e)}")
        
        # Ensure score is within bounds
        score = max(0, min(100, score))
        
        # Generate summary
        summary = self._generate_framework_summary("Next.js", score, len(issues))
        
        return FrameworkAuditScore(
            score=score,
            summary=summary,
            suggestions=suggestions,
            issues=issues,
            confidence=0.85,
            framework=FrameworkType.NEXTJS
        )
    
    async def _audit_svelte(self, code: str) -> FrameworkAuditScore:
        """
        Audit Svelte-specific best practices.
        
        Checks:
        - Reactive statements ($:)
        - Store subscriptions and cleanup
        - Component lifecycle usage
        - Unnecessary reactivity
        - Event handling patterns
        """
        issues = []
        score = 100
        suggestions = []
        
        # Check for proper store subscriptions
        if '$' in code and 'subscribe(' in code:
            issues.append(AuditIssue(
                category=AuditCategory.PERFORMANCE,
                severity=SeverityLevel.WARNING,
                description="Manual store subscription instead of auto-subscription",
                location="Store usage",
                fix_suggestion="Use $ prefix for auto-subscription: $storeName instead of storeName.subscribe()"
            ))
            score -= 10
        
        # Check for reactive statement patterns
        if '$:' in code:
            # Check for complex reactive statements that should be functions
            complex_reactive = len(re.findall(r'\$:\s*\w+\s*=\s*[^;]{50,}', code))
            if complex_reactive > 0:
                issues.append(AuditIssue(
                    category=AuditCategory.PERFORMANCE,
                    severity=SeverityLevel.INFO,
                    description=f"{complex_reactive} complex reactive statement(s)",
                    location="Reactive declarations",
                    fix_suggestion="Consider extracting complex reactive logic into functions"
                ))
                score -= 5
        
        # Check for proper event handling
        if 'on:' in code:
            # Check for event modifiers usage
            if 'preventDefault' in code and '|preventDefault' not in code:
                issues.append(AuditIssue(
                    category=AuditCategory.PERFORMANCE,
                    severity=SeverityLevel.INFO,
                    description="Manual preventDefault instead of event modifier",
                    location="Event handlers",
                    fix_suggestion="Use event modifiers: on:click|preventDefault instead of e.preventDefault()"
                ))
                score -= 5
        
        # Check for component lifecycle
        if 'onMount(' in code:
            # Check for cleanup in onMount
            if 'return' not in code:
                issues.append(AuditIssue(
                    category=AuditCategory.PERFORMANCE,
                    severity=SeverityLevel.WARNING,
                    description="onMount without cleanup function",
                    location="onMount lifecycle",
                    fix_suggestion="Return cleanup function from onMount if setting up subscriptions/listeners"
                ))
                score -= 10
        
        # Check for unnecessary reactivity
        if re.search(r'\$:\s*\w+\s*=\s*\w+\s*;', code):
            issues.append(AuditIssue(
                category=AuditCategory.PERFORMANCE,
                severity=SeverityLevel.INFO,
                description="Simple reactive assignment (may be unnecessary)",
                location="Reactive declarations",
                fix_suggestion="Consider if reactive statement is needed for simple assignments"
            ))
            score -= 5
        
        # Check for proper component props
        if 'export let' in code:
            # Check for default values
            props_without_defaults = len(re.findall(r'export let \w+;', code))
            if props_without_defaults > 2:
                issues.append(AuditIssue(
                    category=AuditCategory.PERFORMANCE,
                    severity=SeverityLevel.INFO,
                    description=f"{props_without_defaults} props without default values",
                    location="Component props",
                    fix_suggestion="Consider adding default values to props: export let prop = defaultValue"
                ))
                score -= 5
        
        # Check for store creation patterns
        if 'writable(' in code or 'readable(' in code or 'derived(' in code:
            # Check if stores are properly exported
            if 'export const' not in code and 'export {' not in code:
                issues.append(AuditIssue(
                    category=AuditCategory.PERFORMANCE,
                    severity=SeverityLevel.WARNING,
                    description="Store created but not exported",
                    location="Store definitions",
                    fix_suggestion="Export stores so they can be imported and used in other components"
                ))
                score -= 10
        
        # Check for proper each block keys
        if '{#each' in code and ':key=' not in code and '(item)' not in code:
            issues.append(AuditIssue(
                category=AuditCategory.PERFORMANCE,
                severity=SeverityLevel.WARNING,
                description="each block without key",
                location="{#each} blocks",
                fix_suggestion="Add key to each block: {#each items as item (item.id)}"
            ))
            score -= 15
        
        # Check for proper await block usage
        if '{#await' in code:
            # Check for error handling
            if ':catch' not in code:
                issues.append(AuditIssue(
                    category=AuditCategory.PERFORMANCE,
                    severity=SeverityLevel.WARNING,
                    description="await block without error handling",
                    location="{#await} blocks",
                    fix_suggestion="Add {:catch error} block to handle promise rejections"
                ))
                score -= 10
        
        # Use Gemini for deeper Svelte analysis
        try:
            prompt = f"""Analyze this Svelte code for best practices and common issues:

{code[:2000]}

Focus on:
1. Reactive statements and patterns
2. Store usage and management
3. Component lifecycle
4. Performance optimization
5. Svelte-specific anti-patterns

Provide 2-3 specific, actionable suggestions.
Respond with JSON: {{"suggestions": ["suggestion1", "suggestion2"]}}
"""
            
            analysis = await self.gemini.generate_json(prompt=prompt, temperature=0.3)
            if analysis and 'suggestions' in analysis:
                suggestions.extend(analysis['suggestions'])
        except Exception as e:
            logger.warning(f"Svelte semantic analysis failed: {str(e)}")
        
        # Ensure score is within bounds
        score = max(0, min(100, score))
        
        # Generate summary
        summary = self._generate_framework_summary("Svelte", score, len(issues))
        
        return FrameworkAuditScore(
            score=score,
            summary=summary,
            suggestions=suggestions,
            issues=issues,
            confidence=0.85,
            framework=FrameworkType.SVELTE
        )
    
    def _generate_framework_summary(self, framework_name: str, score: int, issue_count: int) -> str:
        """Generate summary for framework-specific audit."""
        if score >= 90:
            return f"Excellent {framework_name} best practices with {issue_count} minor issue(s)"
        elif score >= 75:
            return f"Good {framework_name} practices with {issue_count} issue(s) to address"
        elif score >= 60:
            return f"Moderate {framework_name} compliance with {issue_count} issue(s) requiring attention"
        else:
            return f"Poor {framework_name} practices with {issue_count} critical issue(s)"
    
    def validate(self, output: AgentOutput) -> ValidationResult:
        """
        Validate Audit Agent output.
        
        Args:
            output: Output to validate
            
        Returns:
            ValidationResult with validation status
        """
        result = ValidationResult(is_valid=True, confidence=1.0)
        
        if not output.success:
            result.add_error("Operation failed")
            return result
        
        if not isinstance(output, AuditOutput):
            result.add_error("Invalid output type")
            return result
        
        if not output.audit_result:
            result.add_error("No audit result in output")
            return result
        
        audit_result = output.audit_result
        
        # Validate scores are within range
        if not (0 <= audit_result.seo.score <= 100):
            result.add_error(f"SEO score out of range: {audit_result.seo.score}")
        
        if not (0 <= audit_result.accessibility.score <= 100):
            result.add_error(f"Accessibility score out of range: {audit_result.accessibility.score}")
        
        if not (0 <= audit_result.performance.score <= 100):
            result.add_error(f"Performance score out of range: {audit_result.performance.score}")
        
        if not (0 <= audit_result.overall_score <= 100):
            result.add_error(f"Overall score out of range: {audit_result.overall_score}")
        
        # Check for critical issues
        all_issues = (
            audit_result.seo.issues +
            audit_result.accessibility.issues +
            audit_result.performance.issues
        )
        
        if audit_result.framework_specific:
            all_issues.extend(audit_result.framework_specific.issues)
        
        critical_issues = [i for i in all_issues if i.severity == SeverityLevel.CRITICAL]
        if critical_issues:
            result.add_warning(f"{len(critical_issues)} critical issue(s) found")
        
        # Set confidence from audit result
        result.confidence = self._calculate_overall_confidence(audit_result)
        
        return result
