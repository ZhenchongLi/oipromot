"""
AI service for language model interactions with multiple provider support.
"""

from typing import Dict, Any
from ..core.config import get_settings
from ..core.exceptions import AIServiceError
from ..core.logging import get_logger
from .ai_providers import get_ai_provider, AIProvider

logger = get_logger(__name__)


class AIService:
    """Service for AI model interactions with multiple provider support."""
    
    def __init__(self):
        self.settings = get_settings()
        self.provider = self._initialize_provider()
    
    def _initialize_provider(self) -> AIProvider:
        """Initialize the AI provider based on configuration."""
        try:
            provider = get_ai_provider()
            logger.info(f"AI provider '{self.settings.ai_provider}' initialized successfully")
            return provider
            
        except Exception as e:
            logger.error(f"Failed to initialize AI provider: {e}")
            raise AIServiceError(f"Failed to initialize AI provider: {e}")
    
    async def process_message(self, message: str) -> str:
        """Process a message using the configured AI provider."""
        try:
            if not self.provider:
                raise AIServiceError("AI service not properly configured")
            
            if not message or not message.strip():
                raise AIServiceError("Message cannot be empty")
            
            logger.debug(f"Processing message with {self.settings.ai_provider}: {message[:100]}...")
            response = await self.provider.process_message(message.strip())
            
            logger.debug("Message processed successfully")
            return response
            
        except AIServiceError:
            raise
        except Exception as e:
            logger.error(f"Failed to process message: {e}")
            raise AIServiceError(f"Failed to process message: {e}")
    
    def is_available(self) -> bool:
        """Check if the AI service is available."""
        return self.provider is not None and self.provider.is_available()
    
    def get_status(self) -> Dict[str, Any]:
        """Get the status of the AI service."""
        if self.provider:
            status = self.provider.get_status()
            status["configured_provider"] = self.settings.ai_provider
            return status
        else:
            return {
                "available": False,
                "provider": "none",
                "configured_provider": self.settings.ai_provider,
                "error": "Provider not initialized"
            }
    
    def switch_provider(self, provider_name: str) -> bool:
        """Switch to a different AI provider."""
        try:
            # Temporarily update the provider setting
            old_provider = self.settings.ai_provider
            self.settings.ai_provider = provider_name
            
            # Try to initialize the new provider
            new_provider = get_ai_provider()
            
            # If successful, update the current provider
            self.provider = new_provider
            logger.info(f"Successfully switched from {old_provider} to {provider_name}")
            return True
            
        except Exception as e:
            # Restore the old provider setting on failure
            self.settings.ai_provider = old_provider
            logger.error(f"Failed to switch to provider {provider_name}: {e}")
            return False
    
    def get_available_providers(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all available providers."""
        providers = {}
        current_provider = self.settings.ai_provider
        
        for provider_name in ["openai", "deepseek", "ollama"]:
            try:
                # Temporarily switch to test each provider
                self.settings.ai_provider = provider_name
                test_provider = get_ai_provider()
                providers[provider_name] = test_provider.get_status()
            except Exception as e:
                providers[provider_name] = {
                    "provider": provider_name,
                    "available": False,
                    "error": str(e)
                }
        
        # Restore original provider
        self.settings.ai_provider = current_provider
        return providers 