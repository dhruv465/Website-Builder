import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_create_form():
    response = client.post(
        "/api/forms",
        json={
            "site_id": "site-123",
            "name": "Contact Form",
            "fields": [
                {"id": "1", "type": "text", "label": "Name", "required": True},
                {"id": "2", "type": "email", "label": "Email", "required": True}
            ],
            "settings": {
                "email_to": "test@example.com"
            }
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Contact Form"
    assert len(data["fields"]) == 2
    assert data["settings"]["email_to"] == "test@example.com"

def test_get_form():
    # Since we are mocking the DB in the endpoint for now, we can just test the GET
    response = client.get("/api/forms/form-123")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "form-123"

def test_submit_form():
    response = client.post(
        "/api/forms/form-123/submit",
        json={
            "data": {"name": "Test User", "email": "test@example.com"}
        }
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Form submitted successfully"
