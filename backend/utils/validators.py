"""
Validation utilities for the Smart Website Builder.
"""
from typing import Optional
from html.parser import HTMLParser
import re


class HTMLValidator(HTMLParser):
    """Simple HTML validator to check for basic syntax errors."""
    
    def __init__(self):
        super().__init__()
        self.errors = []
        self.tag_stack = []
    
    def handle_starttag(self, tag, attrs):
        """Handle opening tags."""
        self.tag_stack.append(tag)
    
    def handle_endtag(self, tag):
        """Handle closing tags."""
        if not self.tag_stack:
            self.errors.append(f"Unexpected closing tag: {tag}")
        elif self.tag_stack[-1] != tag:
            self.errors.append(f"Mismatched tags: expected {self.tag_stack[-1]}, got {tag}")
        else:
            self.tag_stack.pop()
    
    def error(self, message):
        """Handle parsing errors."""
        self.errors.append(message)


def validate_html(html: str) -> tuple[bool, list[str]]:
    """
    Validate HTML syntax.
    
    Args:
        html: HTML string to validate
        
    Returns:
        Tuple of (is_valid, error_messages)
    """
    validator = HTMLValidator()
    try:
        validator.feed(html)
        
        # Check for unclosed tags
        if validator.tag_stack:
            validator.errors.append(f"Unclosed tags: {', '.join(validator.tag_stack)}")
        
        is_valid = len(validator.errors) == 0
        return is_valid, validator.errors
    except Exception as e:
        return False, [f"HTML parsing error: {str(e)}"]


def validate_url(url: str) -> bool:
    """
    Validate URL format.
    
    Args:
        url: URL string to validate
        
    Returns:
        True if valid, False otherwise
    """
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain
        r'localhost|'  # localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # or IP
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE
    )
    return bool(url_pattern.match(url))


def validate_site_name(name: str) -> tuple[bool, Optional[str]]:
    """
    Validate site name for deployment.
    
    Args:
        name: Site name to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not name:
        return False, "Site name cannot be empty"
    
    if len(name) < 3:
        return False, "Site name must be at least 3 characters"
    
    if len(name) > 63:
        return False, "Site name must be less than 63 characters"
    
    # Check for valid characters (alphanumeric and hyphens)
    if not re.match(r'^[a-z0-9-]+$', name):
        return False, "Site name can only contain lowercase letters, numbers, and hyphens"
    
    # Cannot start or end with hyphen
    if name.startswith('-') or name.endswith('-'):
        return False, "Site name cannot start or end with a hyphen"
    
    return True, None


def sanitize_site_name(name: str) -> str:
    """
    Sanitize site name for deployment.
    
    Args:
        name: Site name to sanitize
        
    Returns:
        Sanitized site name
    """
    # Convert to lowercase
    name = name.lower()
    
    # Replace spaces and underscores with hyphens
    name = re.sub(r'[\s_]+', '-', name)
    
    # Remove invalid characters
    name = re.sub(r'[^a-z0-9-]', '', name)
    
    # Remove consecutive hyphens
    name = re.sub(r'-+', '-', name)
    
    # Remove leading/trailing hyphens
    name = name.strip('-')
    
    # Ensure minimum length
    if len(name) < 3:
        name = f"site-{name}"
    
    # Ensure maximum length
    if len(name) > 63:
        name = name[:63].rstrip('-')
    
    return name
