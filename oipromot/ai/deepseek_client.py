"""
DeepSeek API client for Office command optimization.
"""

import httpx
import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class DeepSeekClient:
    """Client for DeepSeek API integration."""
    
    def __init__(self):
        self.base_url = "https://api.deepseek.com/v1"
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        
        self.office_optimization_prompt = """
You are an OfficeAI assistant for Word and Excel automation. Follow this strategy:

1. App Selection: Use "0=Word, 1=Excel" for app choice
2. Task Categories:
   - Content generation (Word) → Ask for content details (topic, format, length)
   - Function operations → Generate VBA prompt requirements (objects, conditions, expected results)
   - Direct commands → Provide specific UI steps

Rules:
- CRITICAL: Respond in SAME LANGUAGE as input (Chinese→Chinese, English→English)
- Keep responses very short (1-2 lines max)
- Use specific parameters (14pt, A1:B10, etc.)
- For content tasks → focus on Word + content prompts
- For functional tasks → create prompts for VBA generation (DO NOT write VBA code)

User request: "{user_input}"

Response strategy IN SAME LANGUAGE:
"""
    
    def optimize_prompt(self, user_input: str) -> Optional[str]:
        """Send user input to DeepSeek API for Office command optimization."""
        if not self.api_key:
            return None
            
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "deepseek-chat",
                "messages": [
                    {
                        "role": "system", 
                        "content": "You are an expert in Microsoft Office automation. Convert imprecise user requests into specific, actionable Office commands."
                    },
                    {
                        "role": "user", 
                        "content": f"Convert this request into a precise Office command: {user_input}"
                    }
                ],
                "max_tokens": 150,
                "temperature": 0.1
            }
            
            with httpx.Client() as client:
                response = client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=data,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result["choices"][0]["message"]["content"].strip()
                else:
                    return None
                    
        except Exception:
            return None
    
    def optimize_with_context(self, full_prompt: str) -> Optional[str]:
        """Send contextual prompt to DeepSeek API for conversational optimization."""
        if not self.api_key:
            return None
            
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "deepseek-chat",
                "messages": [
                    {
                        "role": "user", 
                        "content": full_prompt
                    }
                ],
                "max_tokens": 100,
                "temperature": 0.3
            }
            
            with httpx.Client() as client:
                response = client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=data,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result["choices"][0]["message"]["content"].strip()
                else:
                    return None
                    
        except Exception:
            return None