"""
Service for natural language editing of websites.
"""
from typing import Dict, Any, Optional, Tuple
import json
from bs4 import BeautifulSoup

from models.editing import EditCommand, SiteContext, EditResult, EditType, EditScope
from services.gemini_service import gemini_service
from utils.logging import logger

class EditingService:
    """Service for handling natural language website edits."""

    async def parse_command(self, prompt: str, context: Optional[SiteContext] = None) -> EditCommand:
        """
        Parse a natural language prompt into a structured EditCommand.
        """
        system_prompt = """
        You are an expert web developer and UI designer. 
        Your task is to parse a natural language request for website editing into a structured command.
        
        Analyze the user's request and categorize it into one of the following types:
        - change_color: Changing text, background, or border colors
        - change_text: Modifying text content
        - change_style: Changing fonts, sizes, margins, padding, etc.
        - add_section: Adding new content sections
        - remove_section: Deleting sections
        - move_section: Reordering sections
        - other: Any other change
        
        Determine the scope:
        - element: Specific element (button, heading, etc.)
        - section: A full section (hero, footer, etc.)
        - global: Site-wide changes (theme, typography)
        
        Identify the target:
        - Provide a descriptive name or CSS selector for the target.
        
        Extract the value:
        - The specific change to apply (e.g., hex color, new text, style rules).
        """
        
        user_prompt = f"User Request: {prompt}\n"
        if context and context.selected_element:
            user_prompt += f"Selected Element: {context.selected_element}\n"
            
        schema = {
            "type": "object",
            "properties": {
                "type": {"type": "string", "enum": [t.value for t in EditType]},
                "target": {"type": "string"},
                "value": {"type": "string"},
                "scope": {"type": "string", "enum": [s.value for s in EditScope]},
                "confidence": {"type": "number"}
            },
            "required": ["type", "target", "value", "scope", "confidence"]
        }
        
        try:
            result = await gemini_service.generate_json(
                prompt=system_prompt + "\n" + user_prompt,
                schema=schema
            )
            
            return EditCommand(
                original_prompt=prompt,
                **result
            )
        except Exception as e:
            logger.error(f"Error parsing edit command: {e}")
            # Fallback for simple cases or error handling
            return EditCommand(
                original_prompt=prompt,
                type=EditType.OTHER,
                target="unknown",
                value=prompt,
                scope=EditScope.GLOBAL,
                confidence=0.0
            )

    async def apply_edit(self, command: EditCommand, context: SiteContext) -> EditResult:
        """
        Apply an edit command to the site context.
        """
        if command.scope == EditScope.GLOBAL:
            return await self._apply_global_edit(command, context)
        else:
            return await self._apply_local_edit(command, context)

    async def _apply_global_edit(self, command: EditCommand, context: SiteContext) -> EditResult:
        """Apply global changes (usually CSS variables or body styles)."""
        prompt = f"""
        You are an expert web developer. Apply the following global edit to the CSS.
        
        Request: {command.original_prompt}
        Command Type: {command.type}
        Target: {command.target}
        Value: {command.value}
        
        Current CSS:
        ```css
        {context.css_code}
        ```
        
        Return the FULL updated CSS code. Do not modify the HTML.
        """
        
        try:
            updated_css = await gemini_service.generate_text(prompt)
            # Clean up markdown code blocks if present
            updated_css = self._clean_code_block(updated_css, "css")
            
            return EditResult(
                success=True,
                html_code=context.html_code,
                css_code=updated_css,
                message=f"Applied global edit: {command.original_prompt}"
            )
        except Exception as e:
            logger.error(f"Error applying global edit: {e}")
            return EditResult(
                success=False,
                html_code=context.html_code,
                css_code=context.css_code,
                message=f"Failed to apply edit: {str(e)}"
            )

    async def _apply_local_edit(self, command: EditCommand, context: SiteContext) -> EditResult:
        """Apply local changes to HTML or specific CSS rules."""
        # For local edits, we might need to modify HTML (content/structure) or CSS (styles)
        
        prompt = f"""
        You are an expert web developer. Apply the following edit to the website.
        
        Request: {command.original_prompt}
        Command Type: {command.type}
        Target: {command.target}
        Value: {command.value}
        
        Current HTML:
        ```html
        {context.html_code}
        ```
        
        Current CSS:
        ```css
        {context.css_code}
        ```
        
        Return a JSON object with the updated HTML and CSS.
        """
        
        schema = {
            "type": "object",
            "properties": {
                "html_code": {"type": "string"},
                "css_code": {"type": "string"},
                "affected_selectors": {"type": "array", "items": {"type": "string"}}
            },
            "required": ["html_code", "css_code"]
        }
        
        try:
            result = await gemini_service.generate_json(prompt, schema=schema)
            
            return EditResult(
                success=True,
                html_code=result["html_code"],
                css_code=result["css_code"],
                affected_selectors=result.get("affected_selectors", []),
                message=f"Applied edit: {command.original_prompt}"
            )
        except Exception as e:
            logger.error(f"Error applying local edit: {e}")
            return EditResult(
                success=False,
                html_code=context.html_code,
                css_code=context.css_code,
                message=f"Failed to apply edit: {str(e)}"
            )

    def _clean_code_block(self, text: str, lang: str) -> str:
        """Clean markdown code blocks from text."""
        text = text.strip()
        if text.startswith(f"```{lang}"):
            text = text[len(lang)+3:]
        elif text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        return text.strip()

# Global instance
editing_service = EditingService()
