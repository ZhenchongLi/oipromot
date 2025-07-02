"""Main entry point for OfficeAI Prompt Project"""

import uvicorn
from src.oipromot.app import app
from src.oipromot.core.database import create_db_and_tables
from src.oipromot.core.config import get_settings
from src.oipromot.core.logging import setup_logging


def main():
    """Start the FastAPI web server."""
    # Set up logging
    logger = setup_logging()
    
    # Get settings
    settings = get_settings()
    
    # Create database and tables
    logger.info("Initializing database...")
    create_db_and_tables()
    
    # Start server
    logger.info(f"Starting server on {settings.api_host}:{settings.api_port}")
    uvicorn.run(
        app, 
        host=settings.api_host, 
        port=settings.api_port,
        log_level=settings.log_level.lower()
    )


if __name__ == "__main__":
    main()
