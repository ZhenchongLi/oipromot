"""
Prompt-related API routes.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from ..core.database import get_session
from ..core.models import PromptCreate, PromptResponse
from ..core.exceptions import ValidationError, PromptNotFoundError, DatabaseError
from ..services.prompt_service import PromptService
from ..services.ai_service import AIService
from ..core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()


def get_prompt_service(session: Session = Depends(get_session)) -> PromptService:
    """Dependency to get prompt service."""
    return PromptService(session)


def get_ai_service() -> AIService:
    """Dependency to get AI service."""
    return AIService()


@router.post("/", response_model=PromptResponse, status_code=status.HTTP_201_CREATED)
async def create_prompt(
    prompt: PromptCreate,
    service: PromptService = Depends(get_prompt_service)
):
    """Create a new prompt."""
    try:
        return await service.create_prompt(prompt)
    except ValidationError as e:
        logger.warning(f"Validation error creating prompt: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error creating prompt: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/", response_model=List[PromptResponse])
async def get_prompts(service: PromptService = Depends(get_prompt_service)):
    """Get all prompts."""
    try:
        return await service.get_all_prompts()
    except Exception as e:
        logger.error(f"Error getting prompts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/{prompt_id}", response_model=PromptResponse)
async def get_prompt(
    prompt_id: str,
    service: PromptService = Depends(get_prompt_service)
):
    """Get a prompt by ID."""
    try:
        return await service.get_prompt(prompt_id)
    except PromptNotFoundError as e:
        logger.warning(f"Prompt not found: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error getting prompt {prompt_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.put("/{prompt_id}", response_model=PromptResponse)
async def update_prompt(
    prompt_id: str,
    prompt: PromptCreate,
    service: PromptService = Depends(get_prompt_service)
):
    """Update a prompt."""
    try:
        return await service.update_prompt(prompt_id, prompt)
    except (ValidationError, PromptNotFoundError) as e:
        logger.warning(f"Error updating prompt {prompt_id}: {e}")
        status_code = status.HTTP_404_NOT_FOUND if isinstance(e, PromptNotFoundError) else status.HTTP_400_BAD_REQUEST
        raise HTTPException(
            status_code=status_code,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error updating prompt {prompt_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.delete("/{prompt_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_prompt(
    prompt_id: str,
    service: PromptService = Depends(get_prompt_service)
):
    """Delete a prompt."""
    try:
        await service.delete_prompt(prompt_id)
    except PromptNotFoundError as e:
        logger.warning(f"Prompt not found for deletion: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error deleting prompt {prompt_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/chat")
async def chat_with_ai(
    message: str,
    ai_service: AIService = Depends(get_ai_service)
):
    """Chat with AI service."""
    try:
        if not ai_service.is_available():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="AI service is not available"
            )
        
        response = await ai_service.process_message(message)
        return {"response": response}
        
    except Exception as e:
        logger.error(f"Error processing chat message: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/ai/status")
async def get_ai_status(ai_service: AIService = Depends(get_ai_service)):
    """Get current AI service status."""
    try:
        return ai_service.get_status()
    except Exception as e:
        logger.error(f"Error getting AI status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/ai/providers")
async def get_available_providers(ai_service: AIService = Depends(get_ai_service)):
    """Get status of all available AI providers."""
    try:
        return ai_service.get_available_providers()
    except Exception as e:
        logger.error(f"Error getting available providers: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/ai/provider/{provider_name}")
async def switch_ai_provider(
    provider_name: str,
    ai_service: AIService = Depends(get_ai_service)
):
    """Switch to a different AI provider."""
    try:
        valid_providers = ["openai", "deepseek", "ollama"]
        if provider_name.lower() not in valid_providers:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid provider. Must be one of: {valid_providers}"
            )
        
        success = ai_service.switch_provider(provider_name.lower())
        if success:
            return {
                "message": f"Successfully switched to {provider_name}",
                "provider": provider_name.lower(),
                "status": ai_service.get_status()
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to switch to provider {provider_name}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error switching AI provider: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        ) 