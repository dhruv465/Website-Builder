import pytest
from unittest.mock import MagicMock

def test_parse_edit_command(client, mock_gemini_service, monkeypatch):
    # Patch gemini service in editing service
    monkeypatch.setattr("services.editing_service.gemini_service", mock_gemini_service)
    
    # Mock Gemini response
    mock_gemini_service.generate_json.return_value = {
        "type": "change_color",
        "target": "header",
        "value": "blue",
        "scope": "element",
        "confidence": 0.9
    }
    
    payload = {
        "prompt": "Make the header blue",
        "context": {
            "html_code": "<div>Header</div>",
            "css_code": ".header { color: red; }",
            "selected_element": "header"
        }
    }
    
    response = client.post("/api/edit/parse", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert data["type"] == "change_color"
    assert data["target"] == "header"
    assert data["value"] == "blue"

def test_apply_edit_command(client, mock_gemini_service, monkeypatch):
    monkeypatch.setattr("services.editing_service.gemini_service", mock_gemini_service)
    
    # Mock Gemini response
    mock_gemini_service.generate_json.return_value = {
        "html_code": "<div>Updated Header</div>",
        "css_code": ".header { color: blue; }",
        "affected_selectors": [".header"]
    }
    
    payload = {
        "command": {
            "original_prompt": "Make the header blue",
            "type": "change_color",
            "target": "header",
            "value": "blue",
            "scope": "element",
            "confidence": 0.9
        },
        "context": {
            "html_code": "<div>Header</div>",
            "css_code": ".header { color: red; }",
            "selected_element": "header"
        }
    }
    
    response = client.post("/api/edit/apply", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["html_code"] == "<div>Updated Header</div>"
    assert data["css_code"] == ".header { color: blue; }"
