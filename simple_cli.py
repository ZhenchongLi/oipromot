#!/usr/bin/env python3
"""
Simple CLI for requirement optimization.
"""

import os
import asyncio
from typing import Optional
from openai import AsyncOpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class RequirementOptimizer:
    """Optimizes user input to clearly describe requirements without extra guidance."""

    def __init__(self):
        # Unified OpenAI-compatible API configuration
        api_base_url = os.getenv("API_BASE_URL", "http://localhost:11434/v1")
        if not api_base_url.endswith("/v1"):
            api_base_url = api_base_url.rstrip("/") + "/v1"

        api_key = os.getenv("API_KEY")  # None for Ollama
        self.model = os.getenv("AI_MODEL") or os.getenv("MODEL", "qwen3:1.7b")

        # Initialize OpenAI client with custom base URL
        # For Ollama, we need to provide a dummy key since OpenAI client requires it
        if api_key is None:
            api_key = "sk-no-key-required"  # Ollama ignores the key

        self.client = AsyncOpenAI(
            base_url=api_base_url,
            api_key=api_key
        )

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
            system_prompt = """你是一个需求分析专家，同时也是Excel和Word专家。你的任务是将用户的原始输入转化为清晰、准确的需求描述。

要求：
1. 只描述用户想要什么，不要添加如何实现的建议
2. 使用简洁、专业的语言
3. 保持需求的核心意图
4. 去除冗余信息
5. 确保描述完整且明确
6. 如果涉及Excel或Word功能，准确理解相关术语和需求

请将以下用户输入转化为清晰的需求描述："""
        else:
            system_prompt = """You are a requirement analysis expert and also an Excel and Word expert. Your task is to transform the user's raw input into a clear, accurate requirement description.

Requirements:
1. Only describe what the user wants, do not add suggestions on how to implement
2. Use concise, professional language
3. Maintain the core intent of the requirement
4. Remove redundant information
5. Ensure the description is complete and clear
6. If involving Excel or Word features, accurately understand related terms and requirements

Please transform the following user input into a clear requirement description:"""

        # Try the configured OpenAI-compatible API
        result = await self._call_api(system_prompt, user_input)
        if result:
            return result

        # Fallback: return cleaned input
        return self._simple_clean(user_input)

    async def _call_api(self, system_prompt: str, user_input: str) -> Optional[str]:
        """Call OpenAI-compatible API using OpenAI client."""
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input}
                ],
                max_tokens=3000,
                temperature=0.3
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            print(f"API error: {e}")
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
            try:
                user_input = input("Enter your requirement: ").strip()
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break

            if user_input.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break

            if not user_input:
                continue

            print("Processing...")
            try:
                optimized = await optimizer.optimize_requirement(user_input)
                print(f"\n📝 Optimized Requirement:")
                print(f"{optimized}\n")
                print("-" * 50)
            except KeyboardInterrupt:
                print("\nOperation cancelled.")
                continue

        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())