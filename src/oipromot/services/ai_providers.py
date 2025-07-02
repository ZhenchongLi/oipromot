"""
AI provider interfaces and implementations with unified configuration.
"""

from typing import Optional, Dict, Any
from abc import ABC, abstractmethod
import httpx
import json

from ..core.config import get_settings
from ..core.exceptions import AIServiceError
from ..core.logging import get_logger

logger = get_logger(__name__)


class AIProvider(ABC):
    """Abstract base class for AI providers."""
    
    @abstractmethod
    async def process_message(self, message: str) -> str:
        """Process a message using the AI model."""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the AI provider is available."""
        pass
    
    @abstractmethod
    def get_status(self) -> Dict[str, Any]:
        """Get the status of the AI provider."""
        pass


class OpenAIProvider(AIProvider):
    """OpenAI provider implementation using unified config."""
    
    def __init__(self):
        self.settings = get_settings()
    
    async def process_message(self, message: str) -> str:
        """Process a message using OpenAI API."""
        try:
            if not self.settings.ai_api_key:
                raise AIServiceError("AI API key not configured")
            
            if not message or not message.strip():
                raise AIServiceError("Message cannot be empty")
            
            headers = {
                "Authorization": f"Bearer {self.settings.ai_api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.settings.ai_model,
                "messages": [
                    {"role": "user", "content": message.strip()}
                ],
                "temperature": 0.7,
                "max_tokens": 1000
            }
            
            url = f"{self.settings.ai_base_url}/chat/completions"
            logger.debug(f"Processing message with OpenAI: {message[:100]}...")
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    headers=headers,
                    json=payload,
                    timeout=30.0
                )
                
                if response.status_code != 200:
                    error_msg = f"OpenAI API error: {response.status_code} - {response.text}"
                    logger.error(error_msg)
                    raise AIServiceError(error_msg)
                
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                
                logger.debug("Message processed successfully by OpenAI")
                return content
                
        except AIServiceError:
            raise
        except Exception as e:
            logger.error(f"Failed to process message with OpenAI: {e}")
            raise AIServiceError(f"Failed to process message with OpenAI: {e}")
    
    def is_available(self) -> bool:
        """Check if OpenAI is available."""
        return self.settings.ai_api_key is not None
    
    def get_status(self) -> Dict[str, Any]:
        """Get OpenAI status."""
        return {
            "provider": "openai",
            "available": self.is_available(),
            "model": self.settings.ai_model,
            "base_url": self.settings.ai_base_url
        }


class DeepSeekProvider(AIProvider):
    """DeepSeek provider implementation using unified config."""
    
    def __init__(self):
        self.settings = get_settings()
    
    async def process_message(self, message: str) -> str:
        """Process a message using DeepSeek API."""
        try:
            if not self.settings.ai_api_key:
                raise AIServiceError("AI API key not configured")
            
            if not message or not message.strip():
                raise AIServiceError("Message cannot be empty")
            
            headers = {
                "Authorization": f"Bearer {self.settings.ai_api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.settings.ai_model,
                "messages": [
                    {"role": "user", "content": message.strip()}
                ],
                "temperature": 0.7,
                "max_tokens": 1000
            }
            
            url = f"{self.settings.ai_base_url}/chat/completions"
            logger.debug(f"Processing message with DeepSeek: {message[:100]}...")
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    headers=headers,
                    json=payload,
                    timeout=30.0
                )
                
                if response.status_code != 200:
                    error_msg = f"DeepSeek API error: {response.status_code} - {response.text}"
                    logger.error(error_msg)
                    raise AIServiceError(error_msg)
                
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                
                logger.debug("Message processed successfully by DeepSeek")
                return content
                
        except AIServiceError:
            raise
        except Exception as e:
            logger.error(f"Failed to process message with DeepSeek: {e}")
            raise AIServiceError(f"Failed to process message with DeepSeek: {e}")
    
    def is_available(self) -> bool:
        """Check if DeepSeek is available."""
        return self.settings.ai_api_key is not None
    
    def get_status(self) -> Dict[str, Any]:
        """Get DeepSeek status."""
        return {
            "provider": "deepseek",
            "available": self.is_available(),
            "model": self.settings.ai_model,
            "base_url": self.settings.ai_base_url
        }


class OllamaProvider(AIProvider):
    """Ollama provider implementation using unified config."""
    
    def __init__(self):
        self.settings = get_settings()
    
    async def process_message(self, message: str) -> str:
        """Process a message using Ollama API."""
        try:
            if not message or not message.strip():
                raise AIServiceError("Message cannot be empty")
            
            # Check if Ollama is available first
            if not await self._check_ollama_connection():
                raise AIServiceError("Ollama server is not available")
            
            payload = {
                "model": self.settings.ai_model,
                "messages": [
                    {"role": "user", "content": message.strip()}
                ],
                "stream": False
            }
            
            url = f"{self.settings.ai_base_url}/api/chat"
            logger.debug(f"Processing message with Ollama: {message[:100]}...")
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    json=payload,
                    timeout=60.0  # Ollama can be slower
                )
                
                if response.status_code != 200:
                    error_msg = f"Ollama API error: {response.status_code} - {response.text}"
                    logger.error(error_msg)
                    raise AIServiceError(error_msg)
                
                data = response.json()
                content = data["message"]["content"]
                
                logger.debug("Message processed successfully by Ollama")
                return content
                
        except AIServiceError:
            raise
        except Exception as e:
            logger.error(f"Failed to process message with Ollama: {e}")
            raise AIServiceError(f"Failed to process message with Ollama: {e}")
    
    async def _check_ollama_connection(self) -> bool:
        """Check if Ollama server is running."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.settings.ai_base_url}/api/tags", timeout=5.0)
                return response.status_code == 200
        except Exception:
            return False
    
    def is_available(self) -> bool:
        """Check if Ollama is available (sync version)."""
        return bool(self.settings.ai_base_url)
    
    async def is_available_async(self) -> bool:
        """Check if Ollama is available (async version)."""
        return await self._check_ollama_connection()
    
    def get_status(self) -> Dict[str, Any]:
        """Get Ollama status."""
        return {
            "provider": "ollama",
            "available": self.is_available(),
            "model": self.settings.ai_model,
            "base_url": self.settings.ai_base_url
        }


def get_ai_provider() -> AIProvider:
    """Factory function to get the configured AI provider."""
    settings = get_settings()
    provider_name = settings.ai_provider.lower()
    
    if provider_name == "openai":
        return OpenAIProvider()
    elif provider_name == "deepseek":
        return DeepSeekProvider()
    elif provider_name == "ollama":
        return OllamaProvider()
    else:
        raise AIServiceError(f"Unknown AI provider: {provider_name}")