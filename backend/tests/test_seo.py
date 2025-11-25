import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from main import app

client = TestClient(app)

@pytest.fixture
def mock_gemini():
    with patch("services.seo_service.gemini_service") as mock:
        yield mock

def test_generate_meta_tags(mock_gemini):
    mock_gemini.generate_json = AsyncMock(return_value={
        "title": "Optimized Title",
        "description": "Optimized Description",
        "keywords": ["seo", "test"]
    })
    
    response = client.post(
        "/api/seo/meta-tags",
        json={
            "content": "This is a test page content.",
            "site_name": "Test Site"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Optimized Title"
    assert data["description"] == "Optimized Description"

def test_generate_sitemap():
    response = client.post(
        "/api/seo/sitemap",
        json={
            "base_url": "https://example.com",
            "pages": ["/", "/about", "/contact"]
        }
    )
    assert response.status_code == 200
    assert "https://example.com/about" in response.text
    assert "<?xml" in response.text

def test_generate_robots_txt():
    response = client.post(
        "/api/seo/robots-txt",
        json={
            "user_agent": "*",
            "allow": ["/"],
            "disallow": ["/admin"],
            "sitemap": "https://example.com/sitemap.xml"
        }
    )
    assert response.status_code == 200
    assert "User-agent: *" in response.text
    assert "Disallow: /admin" in response.text
