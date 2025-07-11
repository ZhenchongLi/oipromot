#!/usr/bin/env python3
"""
启动需求优化器 Web 应用
"""

import os
import uvicorn
from dotenv import load_dotenv
from logger_config import get_logger

# Load environment variables
load_dotenv()

logger = get_logger(__name__)

def main():
    """Main entry point for the web application."""
    # Get configuration from environment variables
    host = os.getenv("WEB_HOST", "0.0.0.0")
    port = int(os.getenv("WEB_PORT", "8000"))
    reload = os.getenv("WEB_RELOAD", "true").lower() == "true"
    
    logger.info(f"Starting Requirement Optimizer Web Application on {host}:{port}")
    logger.info(f"Reload mode: {reload}")
    
    try:
        uvicorn.run(
            "htmx_app:app",
            host=host,
            port=port,
            reload=reload,
            log_level="info"
        )
    except Exception as e:
        logger.error(f"Failed to start web application: {str(e)}")
        raise

if __name__ == "__main__":
    main()