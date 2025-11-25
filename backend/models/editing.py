"""
Models for natural language editing.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Any, Dict, Union
from enum import Enum

class EditScope(str, Enum):
    ELEMENT = "element"
    SECTION = "section"
    GLOBAL = "global"

class EditType(str, Enum):
    CHANGE_COLOR = "change_color"
    CHANGE_TEXT = "change_text"
    CHANGE_STYLE = "change_style"
    ADD_SECTION = "add_section"
    REMOVE_SECTION = "remove_section"
    MOVE_SECTION = "move_section"
    OTHER = "other"

class EditCommand(BaseModel):
    """Structured representation of a natural language edit command."""
    original_prompt: str
    type: EditType
    target: str = Field(..., description="CSS selector or description of the target element(s)")
    value: Any = Field(..., description="The new value, content, or style to apply")
    scope: EditScope
    confidence: float = Field(0.0, ge=0.0, le=1.0)

class SiteContext(BaseModel):
    """Context of the site being edited."""
    html_code: str
    css_code: str
    selected_element: Optional[str] = None  # CSS selector of currently selected element

class EditResult(BaseModel):
    """Result of an edit operation."""
    success: bool
    html_code: str
    css_code: str
    js_code: Optional[str] = None
    affected_selectors: List[str] = []
    message: str
