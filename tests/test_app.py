import pytest
from fastapi.testclient import TestClient
from src.oipromot.app import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_create_prompt():
    prompt_data = {
        "title": "Test Prompt",
        "content": "This is a test prompt"
    }
    response = client.post("/api/v1/prompts", json=prompt_data)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == prompt_data["title"]
    assert data["content"] == prompt_data["content"]
    assert "id" in data


def test_get_prompts():
    response = client.get("/api/v1/prompts")
    assert response.status_code == 200
    assert isinstance(response.json(), list)