#!/usr/bin/env python3
"""
Logging configuration module using loguru for the oipromot application.
Provides centralized logging setup with rotation, formatting, and level management.
"""

import sys
import os
from pathlib import Path
from loguru import logger


def setup_logging(level: str = "INFO"):
    """
    Configure application logging with best practices.
    
    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    # Remove default handler
    logger.remove()
    
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Console handler with color formatting
    logger.add(
        sys.stderr,
        level=level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        colorize=True,
        backtrace=True,
        diagnose=True,
    )
    
    # File handler with rotation
    logger.add(
        log_dir / "app.log",
        level=level,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        rotation="10 MB",
        retention="7 days",
        compression="gz",
        backtrace=True,
        diagnose=True,
    )
    
    # Error-only file handler
    logger.add(
        log_dir / "error.log",
        level="ERROR",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        rotation="5 MB",
        retention="30 days",
        compression="gz",
        backtrace=True,
        diagnose=True,
    )
    
    # Performance log for timing operations
    logger.add(
        log_dir / "performance.log",
        level="INFO",
        format="{time:YYYY-MM-DD HH:mm:ss} | {message}",
        rotation="5 MB",
        retention="7 days",
        compression="gz",
        filter=lambda record: "PERF" in record["extra"]
    )
    
    return logger


def get_logger(name: str = None):
    """
    Get a logger instance with the specified name.
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Logger instance
    """
    if name:
        return logger.bind(name=name)
    return logger


def log_performance(operation: str, duration: float):
    """
    Log performance metrics for operations.
    
    Args:
        operation: Operation name
        duration: Duration in seconds
    """
    logger.bind(PERF=True).info(f"PERF | {operation} | {duration:.4f}s")


# Initialize default logging
_default_level = os.getenv("LOG_LEVEL", "INFO").upper()
setup_logging(_default_level)

# Export the configured logger
__all__ = ["logger", "get_logger", "setup_logging", "log_performance"]