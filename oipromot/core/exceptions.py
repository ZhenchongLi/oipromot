"""
Custom exceptions for the OiPromot application.
"""

from typing import Optional


class OiPromotException(Exception):
    """Base exception for OiPromot application."""
    
    def __init__(self, message: str, error_code: Optional[str] = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class DatabaseError(OiPromotException):
    """Raised when database operations fail."""
    pass


class ValidationError(OiPromotException):
    """Raised when input validation fails."""
    pass


class AIServiceError(OiPromotException):
    """Raised when AI service operations fail."""
    pass


class ConfigurationError(OiPromotException):
    """Raised when configuration is invalid or missing."""
    pass


class PromptNotFoundError(OiPromotException):
    """Raised when a prompt is not found."""
    pass 