"""
Configuration management for OiPromot application.
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import validator
from .exceptions import ConfigurationError


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Database settings
    database_url: str = "duckdb:///oipromot.db"
    
    # API settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_debug: bool = False
    
    # AI service settings (unified for all providers)
    ai_provider: str = "ollama"  # openai, deepseek, ollama
    ai_api_key: Optional[str] = None
    ai_base_url: str = "http://localhost:11434"
    ai_model: str = "qwen3:1.7b"
    
    # Legacy support for backwards compatibility
    openai_api_key: Optional[str] = None
    deepseek_api_key: Optional[str] = None
    
    # CORS settings
    cors_origins: list[str] = ["*"]
    
    # Logging settings
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    @validator("log_level")
    def validate_log_level(cls, v: str) -> str:
        """Validate log level."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ConfigurationError(f"Invalid log level: {v}. Must be one of {valid_levels}")
        return v.upper()
    
    @validator("api_port")
    def validate_api_port(cls, v: int) -> int:
        """Validate API port."""
        if not 1 <= v <= 65535:
            raise ConfigurationError(f"Invalid API port: {v}. Must be between 1 and 65535")
        return v
    
    @validator("ai_provider")
    def validate_ai_provider(cls, v: str) -> str:
        """Validate AI provider."""
        valid_providers = ["openai", "deepseek", "ollama"]
        if v.lower() not in valid_providers:
            raise ConfigurationError(f"Invalid AI provider: {v}. Must be one of {valid_providers}")
        return v.lower()
    
    def model_post_init(self, __context) -> None:
        """Post-initialization to handle legacy configuration migration."""
        # If ai_api_key is not set but legacy keys are available, use them
        if not self.ai_api_key:
            if self.ai_provider == "openai" and self.openai_api_key:
                self.ai_api_key = self.openai_api_key
            elif self.ai_provider == "deepseek" and self.deepseek_api_key:
                self.ai_api_key = self.deepseek_api_key
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings."""
    return settings 