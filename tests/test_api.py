"""
API endpoint tests.
"""

import pytest
from fastapi import status


class TestHealthEndpoint:
    """Test health check endpoint."""
    
    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data


class TestPromptEndpoints:
    """Test prompt-related endpoints."""
    
    def test_create_prompt_success(self, client, sample_prompt):
        """Test successful prompt creation."""
        response = client.post("/api/v1/prompts/", json=sample_prompt)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["title"] == sample_prompt["title"]
        assert data["content"] == sample_prompt["content"]
        assert "id" in data
        assert "created_at" in data
    
    def test_create_prompt_missing_title(self, client):
        """Test prompt creation with missing title."""
        prompt_data = {"content": "Test content"}
        response = client.post("/api/v1/prompts/", json=prompt_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_create_prompt_missing_content(self, client):
        """Test prompt creation with missing content."""
        prompt_data = {"title": "Test title"}
        response = client.post("/api/v1/prompts/", json=prompt_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_get_prompts_empty(self, client):
        """Test getting prompts when none exist."""
        response = client.get("/api/v1/prompts/")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []
    
    def test_get_prompts_with_data(self, client, sample_prompt):
        """Test getting prompts when data exists."""
        # Create a prompt first
        client.post("/api/v1/prompts/", json=sample_prompt)
        
        # Get all prompts
        response = client.get("/api/v1/prompts/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == sample_prompt["title"]
    
    def test_get_prompt_by_id_success(self, client, sample_prompt):
        """Test getting a specific prompt by ID."""
        # Create a prompt first
        create_response = client.post("/api/v1/prompts/", json=sample_prompt)
        prompt_id = create_response.json()["id"]
        
        # Get the prompt by ID
        response = client.get(f"/api/v1/prompts/{prompt_id}")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == prompt_id
        assert data["title"] == sample_prompt["title"]
    
    def test_get_prompt_by_id_not_found(self, client):
        """Test getting a non-existent prompt."""
        response = client.get("/api/v1/prompts/non-existent-id")
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_update_prompt_success(self, client, sample_prompt):
        """Test successful prompt update."""
        # Create a prompt first
        create_response = client.post("/api/v1/prompts/", json=sample_prompt)
        prompt_id = create_response.json()["id"]
        
        # Update the prompt
        updated_data = {
            "title": "Updated Title",
            "content": "Updated content"
        }
        response = client.put(f"/api/v1/prompts/{prompt_id}", json=updated_data)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["title"] == updated_data["title"]
        assert data["content"] == updated_data["content"]
    
    def test_update_prompt_not_found(self, client, sample_prompt):
        """Test updating a non-existent prompt."""
        response = client.put("/api/v1/prompts/non-existent-id", json=sample_prompt)
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_delete_prompt_success(self, client, sample_prompt):
        """Test successful prompt deletion."""
        # Create a prompt first
        create_response = client.post("/api/v1/prompts/", json=sample_prompt)
        prompt_id = create_response.json()["id"]
        
        # Delete the prompt
        response = client.delete(f"/api/v1/prompts/{prompt_id}")
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify it's deleted
        get_response = client.get(f"/api/v1/prompts/{prompt_id}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_delete_prompt_not_found(self, client):
        """Test deleting a non-existent prompt."""
        response = client.delete("/api/v1/prompts/non-existent-id")
        assert response.status_code == status.HTTP_404_NOT_FOUND 