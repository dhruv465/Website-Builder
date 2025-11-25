import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from main import app
from models.editing import EditCommand, SiteContext, EditType, EditScope

client = TestClient(app)

@pytest.fixture
def mock_gemini():
    with patch("services.editing_service.gemini_service") as mock:
        yield mock

def test_parse_command(mock_gemini):
    # Mock the generate_json response
    mock_gemini.generate_json = AsyncMock(return_value={
        "type": "change_color",
        "target": "header",
        "value": "blue",
        "scope": "element",
        "confidence": 0.95
    })
    
    response = client.post(
        "/api/edit/parse",
        json={
            "prompt": "Change the header background to blue",
            "context": {
                "html_code": "<header>Header</header>",
                "css_code": "header { background: red; }"
            }
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["type"] == "change_color"
    assert "header" in data["target"]
    assert "blue" in data["value"]

def test_apply_edit(mock_gemini):
    # Mock the generate_json response for apply_edit
    mock_gemini.generate_json = AsyncMock(return_value={
        "html_code": "<header>Header</header>",
        "css_code": "header { background: blue; }",
        "affected_selectors": ["header"]
    })
    
    command = {
        "original_prompt": "Change the header background to blue",
        "type": "change_color",
        "target": "header",
        "value": "blue",
        "scope": "element",
        "confidence": 0.9
    }
    context = {
        "html_code": "<header>Header</header>",
        "css_code": "header { background: red; }"
    }
    
    response = client.post(
        "/api/edit/apply",
        json={
            "command": command,
            "context": context
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "blue" in data["css_code"]
