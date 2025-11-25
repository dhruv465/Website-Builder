import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from main import app

client = TestClient(app)

@pytest.fixture
def mock_export_service():
    with patch("api.export.export_service") as mock:
        yield mock

def test_export_zip(mock_export_service):
    # Mock return value as BytesIO
    import io
    mock_export_service.create_zip_export.return_value = io.BytesIO(b"zip_content")
    
    response = client.post(
        "/api/export/zip",
        json={
            "html_code": "<html></html>",
            "css_code": "body {}",
            "js_code": "console.log('hi')"
        }
    )
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/zip"

def test_export_github(mock_export_service):
    mock_export_service.export_to_github.return_value = "Success"
    
    response = client.post(
        "/api/export/github",
        json={
            "repo_url": "https://github.com/test/repo.git",
            "token": "token",
            "html_code": "<html></html>",
            "css_code": "body {}",
            "js_code": "console.log('hi')"
        }
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Success"
