"""
Database configuration and session management.
"""

from sqlmodel import SQLModel, create_engine, Session
from .config import get_settings
from .logging import get_logger

logger = get_logger(__name__)

# Database configuration
settings = get_settings()
engine = create_engine(
    settings.database_url,
    echo=settings.api_debug,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {}
)


def create_db_and_tables():
    """Create database and tables."""
    from .models import Prompt, OptimizationSession  # Import here to avoid circular imports
    
    logger.info("Creating database tables...")
    SQLModel.metadata.create_all(engine)
    logger.info("Database tables created successfully")


def get_session():
    """Get database session."""
    with Session(engine) as session:
        yield session