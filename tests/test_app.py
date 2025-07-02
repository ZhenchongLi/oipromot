import pytest
from fastapi.testclient import TestClient


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "version": "0.1.0"}


def test_create_prompt(client):
    prompt_data = {
        "title": "Test Prompt",
        "content": "This is a test prompt"
    }
    response = client.post("/api/v1/prompts/", json=prompt_data)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == prompt_data["title"]
    assert data["content"] == prompt_data["content"]
    assert "id" in data


def test_get_prompts(client):
    response = client.get("/api/v1/prompts/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)