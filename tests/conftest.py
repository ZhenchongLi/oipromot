"""
Pytest configuration and fixtures.
"""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlalchemy.pool import StaticPool

from src.oipromot.app import app
from src.oipromot.core.database import get_session
from src.oipromot.core.models import Prompt, OptimizationSession


@pytest.fixture(name="session")
def session_fixture():
    """Create a test database session."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    """Create a test client with dependency override."""
    def get_session_override():
        return session
    
    app.dependency_overrides[get_session] = get_session_override
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


@pytest.fixture(name="sample_prompt")
def sample_prompt_fixture():
    """Create a sample prompt for testing."""
    return {
        "title": "Test Prompt",
        "content": "This is a test prompt content"
    }


@pytest.fixture(name="sample_optimization_session")
def sample_optimization_session_fixture():
    """Create a sample optimization session for testing."""
    return {
        "original_prompt": "Test original prompt",
        "target_model_type": "big",
        "recommendation": "AI"
    } 