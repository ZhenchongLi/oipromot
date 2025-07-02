"""
Repository layer for database operations.
"""

from typing import List, Optional
from sqlmodel import Session, select
from .models import Prompt, OptimizationSession
from .exceptions import DatabaseError, PromptNotFoundError
from .logging import get_logger

logger = get_logger(__name__)


class PromptRepository:
    """Repository for prompt-related database operations."""
    
    def __init__(self, session: Session):
        self.session = session
    
    def create(self, prompt: Prompt) -> Prompt:
        """Create a new prompt."""
        try:
            self.session.add(prompt)
            self.session.commit()
            self.session.refresh(prompt)
            logger.info(f"Created prompt with ID: {prompt.id}")
            return prompt
        except Exception as e:
            logger.error(f"Failed to create prompt: {e}")
            self.session.rollback()
            raise DatabaseError(f"Failed to create prompt: {e}")
    
    def get_by_id(self, prompt_id: str) -> Optional[Prompt]:
        """Get prompt by ID."""
        try:
            prompt = self.session.get(Prompt, prompt_id)
            if prompt:
                logger.debug(f"Retrieved prompt with ID: {prompt_id}")
            else:
                logger.warning(f"Prompt not found with ID: {prompt_id}")
            return prompt
        except Exception as e:
            logger.error(f"Failed to get prompt by ID {prompt_id}: {e}")
            raise DatabaseError(f"Failed to get prompt: {e}")
    
    def get_all(self) -> List[Prompt]:
        """Get all prompts."""
        try:
            prompts = self.session.exec(select(Prompt)).all()
            logger.debug(f"Retrieved {len(prompts)} prompts")
            return list(prompts)
        except Exception as e:
            logger.error(f"Failed to get all prompts: {e}")
            raise DatabaseError(f"Failed to get prompts: {e}")
    
    def update(self, prompt: Prompt) -> Prompt:
        """Update a prompt."""
        try:
            self.session.add(prompt)
            self.session.commit()
            self.session.refresh(prompt)
            logger.info(f"Updated prompt with ID: {prompt.id}")
            return prompt
        except Exception as e:
            logger.error(f"Failed to update prompt {prompt.id}: {e}")
            self.session.rollback()
            raise DatabaseError(f"Failed to update prompt: {e}")
    
    def delete(self, prompt_id: str) -> bool:
        """Delete a prompt by ID."""
        try:
            prompt = self.get_by_id(prompt_id)
            if not prompt:
                raise PromptNotFoundError(f"Prompt with ID {prompt_id} not found")
            
            self.session.delete(prompt)
            self.session.commit()
            logger.info(f"Deleted prompt with ID: {prompt_id}")
            return True
        except PromptNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Failed to delete prompt {prompt_id}: {e}")
            self.session.rollback()
            raise DatabaseError(f"Failed to delete prompt: {e}")


class OptimizationSessionRepository:
    """Repository for optimization session database operations."""
    
    def __init__(self, session: Session):
        self.session = session
    
    def create(self, session: OptimizationSession) -> OptimizationSession:
        """Create a new optimization session."""
        try:
            self.session.add(session)
            self.session.commit()
            self.session.refresh(session)
            logger.info(f"Created optimization session with ID: {session.id}")
            return session
        except Exception as e:
            logger.error(f"Failed to create optimization session: {e}")
            self.session.rollback()
            raise DatabaseError(f"Failed to create optimization session: {e}")
    
    def get_by_id(self, session_id: str) -> Optional[OptimizationSession]:
        """Get optimization session by ID."""
        try:
            session = self.session.get(OptimizationSession, session_id)
            if session:
                logger.debug(f"Retrieved optimization session with ID: {session_id}")
            else:
                logger.warning(f"Optimization session not found with ID: {session_id}")
            return session
        except Exception as e:
            logger.error(f"Failed to get optimization session by ID {session_id}: {e}")
            raise DatabaseError(f"Failed to get optimization session: {e}")
    
    def update(self, session: OptimizationSession) -> OptimizationSession:
        """Update an optimization session."""
        try:
            self.session.add(session)
            self.session.commit()
            self.session.refresh(session)
            logger.info(f"Updated optimization session with ID: {session.id}")
            return session
        except Exception as e:
            logger.error(f"Failed to update optimization session {session.id}: {e}")
            self.session.rollback()
            raise DatabaseError(f"Failed to update optimization session: {e}") 