"""
Service layer for prompt-related business logic.
"""

from typing import List, Optional
from sqlmodel import Session
from ..core.models import Prompt, PromptCreate, PromptResponse
from ..core.repository import PromptRepository
from ..core.exceptions import ValidationError, PromptNotFoundError
from ..core.logging import get_logger

logger = get_logger(__name__)


class PromptService:
    """Service for prompt-related business operations."""
    
    def __init__(self, session: Session):
        self.repository = PromptRepository(session)
    
    async def create_prompt(self, prompt_data: PromptCreate) -> PromptResponse:
        """Create a new prompt."""
        try:
            # Validate input
            self._validate_prompt_data(prompt_data)
            
            # Create prompt model
            prompt = Prompt.model_validate(prompt_data)
            
            # Save to database
            created_prompt = self.repository.create(prompt)
            
            logger.info(f"Successfully created prompt: {created_prompt.title}")
            return PromptResponse.model_validate(created_prompt)
            
        except ValidationError:
            raise
        except Exception as e:
            logger.error(f"Failed to create prompt: {e}")
            raise
    
    async def get_prompt(self, prompt_id: str) -> PromptResponse:
        """Get a prompt by ID."""
        try:
            prompt = self.repository.get_by_id(prompt_id)
            if not prompt:
                raise PromptNotFoundError(f"Prompt with ID {prompt_id} not found")
            
            return PromptResponse.model_validate(prompt)
            
        except PromptNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Failed to get prompt {prompt_id}: {e}")
            raise
    
    async def get_all_prompts(self) -> List[PromptResponse]:
        """Get all prompts."""
        try:
            prompts = self.repository.get_all()
            return [PromptResponse.model_validate(prompt) for prompt in prompts]
            
        except Exception as e:
            logger.error(f"Failed to get all prompts: {e}")
            raise
    
    async def update_prompt(self, prompt_id: str, prompt_data: PromptCreate) -> PromptResponse:
        """Update a prompt."""
        try:
            # Validate input
            self._validate_prompt_data(prompt_data)
            
            # Get existing prompt
            existing_prompt = self.repository.get_by_id(prompt_id)
            if not existing_prompt:
                raise PromptNotFoundError(f"Prompt with ID {prompt_id} not found")
            
            # Update fields
            existing_prompt.title = prompt_data.title
            existing_prompt.content = prompt_data.content
            
            # Save changes
            updated_prompt = self.repository.update(existing_prompt)
            
            logger.info(f"Successfully updated prompt: {updated_prompt.title}")
            return PromptResponse.model_validate(updated_prompt)
            
        except (ValidationError, PromptNotFoundError):
            raise
        except Exception as e:
            logger.error(f"Failed to update prompt {prompt_id}: {e}")
            raise
    
    async def delete_prompt(self, prompt_id: str) -> bool:
        """Delete a prompt."""
        try:
            return self.repository.delete(prompt_id)
            
        except PromptNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Failed to delete prompt {prompt_id}: {e}")
            raise
    
    def _validate_prompt_data(self, prompt_data: PromptCreate) -> None:
        """Validate prompt data."""
        if not prompt_data.title or not prompt_data.title.strip():
            raise ValidationError("Prompt title is required")
        
        if not prompt_data.content or not prompt_data.content.strip():
            raise ValidationError("Prompt content is required")
        
        if len(prompt_data.title) > 255:
            raise ValidationError("Prompt title is too long (max 255 characters)")
        
        if len(prompt_data.content) > 10000:
            raise ValidationError("Prompt content is too long (max 10000 characters)") 