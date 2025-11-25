import pytest
from unittest.mock import AsyncMock, MagicMock
from services.editing_service import EditingService, EditType, EditScope
from models.editing import SiteContext, EditCommand

@pytest.mark.asyncio
async def test_parse_command(mock_gemini_service, monkeypatch):
    # Patch the gemini_service used in editing_service
    monkeypatch.setattr("services.editing_service.gemini_service", mock_gemini_service)
    
    # Mock response for parse_command
    mock_gemini_service.generate_json.return_value = {
        "type": "change_color",
        "target": "header",
        "value": "#ff0000",
        "scope": "element",
        "confidence": 0.95
    }
    
    service = EditingService()
    prompt = "Make the header red"
    
    command = await service.parse_command(prompt)
    
    assert command.type == EditType.CHANGE_COLOR
    assert command.target == "header"
    assert command.value == "#ff0000"
    assert command.scope == EditScope.ELEMENT
    assert command.original_prompt == prompt

@pytest.mark.asyncio
async def test_apply_local_edit(mock_gemini_service, monkeypatch):
    monkeypatch.setattr("services.editing_service.gemini_service", mock_gemini_service)
    
    # Mock response for apply_edit
    mock_gemini_service.generate_json.return_value = {
        "html_code": "<div>Updated</div>",
        "css_code": ".test { color: red; }",
        "affected_selectors": [".test"]
    }
    
    service = EditingService()
    command = EditCommand(
        original_prompt="Update text",
        type=EditType.CHANGE_TEXT,
        target="div",
        value="Updated",
        scope=EditScope.ELEMENT,
        confidence=1.0
    )
    context = SiteContext(
        html_code="<div>Original</div>",
        css_code=".test { color: blue; }",
        selected_element="div"
    )
    
    result = await service.apply_edit(command, context)
    
    assert result.success is True
    assert result.html_code == "<div>Updated</div>"
    assert result.css_code == ".test { color: red; }"

@pytest.mark.asyncio
async def test_apply_global_edit(mock_gemini_service, monkeypatch):
    monkeypatch.setattr("services.editing_service.gemini_service", mock_gemini_service)
    
    # Mock response for global edit (returns text, not JSON)
    mock_gemini_service.generate_text.return_value = "body { background: black; }"
    
    service = EditingService()
    command = EditCommand(
        original_prompt="Make background black",
        type=EditType.CHANGE_COLOR,
        target="body",
        value="black",
        scope=EditScope.GLOBAL,
        confidence=1.0
    )
    context = SiteContext(
        html_code="<div>Content</div>",
        css_code="body { background: white; }",
        selected_element=None
    )
    
    result = await service.apply_edit(command, context)
    
    assert result.success is True
    assert result.css_code == "body { background: black; }"
    # Global edits shouldn't change HTML
    assert result.html_code == context.html_code
