"""
Core data models for the OiPromot system.
"""

from typing import Optional
from sqlmodel import SQLModel, Field
from datetime import datetime


class PromptBase(SQLModel):
    """Base model for prompt data."""
    title: str
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Prompt(PromptBase, table=True):
    """Database model for prompts."""
    id: Optional[str] = Field(default_factory=lambda: str(__import__('uuid').uuid4()), primary_key=True)


class PromptCreate(PromptBase):
    """Model for creating new prompts."""
    pass


class PromptResponse(PromptBase):
    """Model for prompt API responses."""
    id: str


class OptimizationSession(SQLModel, table=True):
    """Database model for optimization sessions."""
    id: Optional[str] = Field(default_factory=lambda: str(__import__('uuid').uuid4()), primary_key=True)
    original_prompt: str
    optimized_prompt: Optional[str] = None
    target_model_type: str = "big"  # "big" or "small"
    recommendation: Optional[str] = None  # "AI", "VBA", or "HYBRID"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class CapabilityRecommendation:
    """Data class for capability recommendations."""
    
    def __init__(self, recommendation: str, reason: str, ai_score: int, vba_score: int, is_chinese: bool):
        self.recommendation = recommendation
        self.reason = reason
        self.ai_score = ai_score
        self.vba_score = vba_score
        self.is_chinese = is_chinese