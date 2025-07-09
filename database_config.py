#!/usr/bin/env python3
"""
Database configuration module.
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class DatabaseConfig:
    """Database configuration class."""
    
    def __init__(self):
        """Initialize database configuration."""
        self.db_path = os.getenv("DB_PATH", "app.db")
        self.db_url = f"duckdb:///{self.db_path}"
    
    @property
    def database_path(self) -> str:
        """Get database file path."""
        return self.db_path
    
    @property
    def database_url(self) -> str:
        """Get database URL for SQLAlchemy."""
        return self.db_url
    
    def set_database_path(self, path: str) -> None:
        """Set custom database path."""
        self.db_path = path
        self.db_url = f"duckdb:///{path}"


# Global database configuration instance
db_config = DatabaseConfig()