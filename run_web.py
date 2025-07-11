#!/usr/bin/env python3
"""
启动需求优化器 Web 应用
"""

import uvicorn
from logger_config import get_logger

logger = get_logger(__name__)

def main():
    """Main entry point for the web application."""
    logger.info("Starting Requirement Optimizer Web Application")
    
    try:
        uvicorn.run(
            "htmx_app:app",
            host="0.0.0.0",
            port=8001,
            reload=True,
            log_level="info"
        )
    except Exception as e:
        logger.error(f"Failed to start web application: {str(e)}")
        raise

if __name__ == "__main__":
    main()