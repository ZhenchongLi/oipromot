#!/usr/bin/env python3
"""
Simple prompt optimizer focused on describing user requirements clearly.
"""

import os
import json
import asyncio
from typing import Optional
from dataclasses import dataclass
import httpx


@dataclass
class Config:
    """Simple configuration for AI providers."""
    openai_api_key: Optional[str] = None
    deepseek_api_key: Optional[str] = None
    
    def __post_init__(self):
        # Load from environment variables
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")


class RequirementOptimizer:
    """Optimizes user input to clearly describe requirements without extra guidance."""
    
    def __init__(self):
        self.config = Config()
    
    async def optimize_requirement(self, user_input: str) -> str:
        """
        Optimize user input to clearly describe the requirement.
        
        Args:
            user_input: Raw user input describing what they want
            
        Returns:
            Optimized requirement description
        """
        # Detect language
        is_chinese = any('\u4e00' <= char <= '\u9fff' for char in user_input)
        
        if is_chinese:
            system_prompt = """你是一个需求分析专家。你的任务是将用户的原始输入转化为清晰、准确的需求描述。

要求：
1. 只描述用户想要什么，不要添加如何实现的建议
2. 使用简洁、专业的语言
3. 保持需求的核心意图
4. 去除冗余信息
5. 确保描述完整且明确

请将以下用户输入转化为清晰的需求描述："""
        else:
            system_prompt = """You are a requirement analysis expert. Your task is to transform the user's raw input into a clear, accurate requirement description.

Requirements:
1. Only describe what the user wants, do not add suggestions on how to implement
2. Use concise, professional language
3. Maintain the core intent of the requirement
4. Remove redundant information
5. Ensure the description is complete and clear

Please transform the following user input into a clear requirement description:"""
        
        # Try OpenAI first, then DeepSeek
        if self.config.openai_api_key:
            result = await self._call_openai(system_prompt, user_input)
            if result:
                return result
        
        if self.config.deepseek_api_key:
            result = await self._call_deepseek(system_prompt, user_input)
            if result:
                return result
        
        # Fallback: return cleaned input
        return self._simple_clean(user_input)
    
    async def _call_openai(self, system_prompt: str, user_input: str) -> Optional[str]:
        """Call OpenAI API."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.config.openai_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "gpt-3.5-turbo",
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_input}
                        ],
                        "max_tokens": 500,
                        "temperature": 0.3
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data["choices"][0]["message"]["content"].strip()
                    
        except Exception as e:
            print(f"OpenAI API error: {e}")
            return None
    
    async def _call_deepseek(self, system_prompt: str, user_input: str) -> Optional[str]:
        """Call DeepSeek API."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.deepseek.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.config.deepseek_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "deepseek-chat",
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_input}
                        ],
                        "max_tokens": 500,
                        "temperature": 0.3
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data["choices"][0]["message"]["content"].strip()
                    
        except Exception as e:
            print(f"DeepSeek API error: {e}")
            return None
    
    def _simple_clean(self, user_input: str) -> str:
        """Simple fallback cleaning when APIs are unavailable."""
        # Remove common filler words and phrases
        cleaned = user_input.strip()
        
        # Basic cleaning patterns
        filler_patterns = [
            "please help me", "can you help me", "i need help with",
            "i want to", "i would like to", "could you", "can you",
            "请帮我", "你能帮我", "我想要", "我需要", "能不能", "可以吗"
        ]
        
        lower_cleaned = cleaned.lower()
        for pattern in filler_patterns:
            if lower_cleaned.startswith(pattern):
                cleaned = cleaned[len(pattern):].strip()
                break
        
        # Capitalize first letter
        if cleaned:
            cleaned = cleaned[0].upper() + cleaned[1:]
        
        return cleaned


async def main():
    """CLI interface for the requirement optimizer."""
    optimizer = RequirementOptimizer()
    
    print("🎯 Requirement Optimizer")
    print("Transform user input into clear requirement descriptions")
    print("Type 'quit' to exit\n")
    
    while True:
        try:
            user_input = input("Enter your requirement: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break
            
            if not user_input:
                continue
            
            print("Processing...")
            optimized = await optimizer.optimize_requirement(user_input)
            
            print(f"\n📝 Optimized Requirement:")
            print(f"{optimized}\n")
            print("-" * 50)
            
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())