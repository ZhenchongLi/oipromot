#!/usr/bin/env python3
"""
Simple CLI for requirement optimization.
"""

import os
import asyncio
import argparse
import re
import signal
import sys
import time
from typing import Optional
from openai import AsyncOpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class RequirementOptimizer:
    """Optimizes user input with interactive confirmation flow."""

    def __init__(self, no_think: bool = False):
        # Unified OpenAI-compatible API configuration
        api_base_url = os.getenv("API_BASE_URL", "http://localhost:11434/v1")
        if not api_base_url.endswith("/v1"):
            api_base_url = api_base_url.rstrip("/") + "/v1"

        api_key = os.getenv("API_KEY")  # None for Ollama
        self.model = os.getenv("AI_MODEL") or os.getenv("MODEL", "qwen3:1.7b")
        self.no_think = no_think

        # Initialize OpenAI client with custom base URL
        # For Ollama, we need to provide a dummy key since OpenAI client requires it
        if api_key is None:
            api_key = "sk-no-key-required"  # Ollama ignores the key

        self.client = AsyncOpenAI(
            base_url=api_base_url,
            api_key=api_key
        )

        self.current_requirement = ""
        self.current_feedback = ""

    async def start_session(self, user_input: str) -> str:
        """
        Start a new interactive session.

        Args:
            user_input: Initial user requirement

        Returns:
            Status indicator
        """
        # Store current requirement
        self.current_requirement = user_input
        self.current_feedback = ""

        # Generate initial response
        initial_result = await self.optimize_requirement(user_input)

        # Detect language
        is_chinese = any('\u4e00' <= char <= '\u9fff' for char in user_input)

        # Show AI response and options
        if is_chinese:
            print(f"\n🤖 AI回复: {initial_result}")
            print("\n请选择:")
            print("1. 输入反馈意见进行调整")
            print("2. 输入 '/n' 或 'n' 开始新对话")
        else:
            print(f"\n🤖 AI Reply: {initial_result}")
            print("\nPlease choose:")
            print("1. Enter feedback for adjustment")
            print("2. Enter '/n' or 'n' to start new conversation")

        return "WAITING_FEEDBACK"

    async def handle_feedback(self, feedback: str) -> str:
        """
        Handle user feedback in current session.

        Args:
            feedback: User feedback or command

        Returns:
            Status or result
        """
        if feedback.lower() in ['/n', 'n']:
            self.reset_session()
            return "NEW_CONVERSATION"
        else:
            # Process feedback and adjust
            self.current_feedback = feedback
            adjusted_result = await self.refine_requirement(self.current_requirement, feedback)

            # Detect language
            is_chinese = any('\u4e00' <= char <= '\u9fff' for char in feedback)

            if is_chinese:
                print(f"\n🤖 AI调整后回复: {adjusted_result}")
                print("\n请选择:")
                print("1. 输入反馈意见继续调整")
                print("2. 输入 '/n' 或 'n' 开始新对话")
            else:
                print(f"\n🤖 AI Adjusted Reply: {adjusted_result}")
                print("\nPlease choose:")
                print("1. Enter feedback for further adjustment")
                print("2. Enter '/n' or 'n' to start new conversation")

            return "WAITING_FEEDBACK"

    async def generate_final_prompt(self) -> str:
        """
        Generate final optimized prompt based on current session.

        Returns:
            Final optimized prompt
        """
        if self.current_feedback:
            # Use refined requirement
            final_result = await self.refine_requirement(self.current_requirement, self.current_feedback)
        else:
            # Use original optimized requirement
            final_result = await self.optimize_requirement(self.current_requirement)

        return final_result

    def reset_session(self):
        """Reset current session data."""
        self.current_requirement = ""
        self.current_feedback = ""

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
            if self.no_think:
                system_prompt = """直接转化用户输入为清晰的需求描述。请以列表形式输出，每个需求点用数字编号。只输出最终结果，不要思考过程，不要解释。"""
            else:
                system_prompt = """你是一个需求分析专家，同时也是Excel和Word专家。你的任务是将用户的原始输入转化为清晰、准确的需求描述。

要求：
1. 只描述用户想要什么，不要添加如何实现的建议
2. 使用简洁、专业的语言
3. 保持需求的核心意图
4. 去除冗余信息
5. 确保描述完整且明确
6. 如果涉及Excel或Word功能，准确理解相关术语和需求
7. 输出结果必须以列表形式展示，每个需求点用数字编号

请将以下用户输入转化为清晰的需求描述："""
        else:
            if self.no_think:
                system_prompt = """Transform user input into clear requirement description. Please output in list format, with each requirement point numbered. Output final result only, no thinking process, no explanation."""
            else:
                system_prompt = """You are a requirement analysis expert and also an Excel and Word expert. Your task is to transform the user's raw input into a clear, accurate requirement description.

Requirements:
1. Only describe what the user wants, do not add suggestions on how to implement
2. Use concise, professional language
3. Maintain the core intent of the requirement
4. Remove redundant information
5. Ensure the description is complete and clear
6. If involving Excel or Word features, accurately understand related terms and requirements
7. Output result must be in list format, with each requirement point numbered

Please transform the following user input into a clear requirement description:"""

        # Try the configured OpenAI-compatible API
        result = await self._call_api(system_prompt, user_input)
        if result:
            return result

        # Fallback: return cleaned input
        return self._simple_clean(user_input)

    async def refine_requirement(self, initial_result: str, feedback: str) -> str:
        """
        Refine requirement based on user feedback.

        Args:
            initial_result: Initial AI response
            feedback: User feedback for refinement

        Returns:
            Refined requirement description
        """
        # Detect language
        is_chinese = any('\u4e00' <= char <= '\u9fff' for char in feedback)

        if is_chinese:
            if self.no_think:
                system_prompt = """根据用户反馈调整需求描述。请以列表形式输出，每个需求点用数字编号。只输出最终结果，不要思考过程。"""
            else:
                system_prompt = """你是一个需求分析专家。根据用户的反馈，调整和优化之前的需求描述。

要求：
1. 根据用户反馈调整需求描述
2. 保持专业和简洁
3. 确保调整后的描述更符合用户意图
4. 不要添加实现建议，只描述需求
5. 输出结果必须以列表形式展示，每个需求点用数字编号

请提供调整后的需求描述："""
        else:
            if self.no_think:
                system_prompt = """Adjust requirement description based on user feedback. Please output in list format, with each requirement point numbered. Output final result only, no thinking process."""
            else:
                system_prompt = """You are a requirement analysis expert. Based on user feedback, adjust and optimize the previous requirement description.

Requirements:
1. Adjust requirement description based on user feedback
2. Keep it professional and concise
3. Ensure the adjusted description better matches user intent
4. Do not add implementation suggestions, only describe requirements
5. Output result must be in list format, with each requirement point numbered

Please provide the adjusted requirement description:"""

        # Try the configured OpenAI-compatible API
        user_message = f"之前的需求描述：{initial_result}\n用户反馈：{feedback}" if is_chinese else f"Previous requirement description: {initial_result}\nUser feedback: {feedback}"
        result = await self._call_api(system_prompt, user_message)
        if result:
            return result

        # Fallback: return initial result with feedback note
        return f"{initial_result}\n\n[User feedback: {feedback}]"

    async def _call_api(self, system_prompt: str, user_input: str) -> Optional[str]:
        """Call OpenAI-compatible API using OpenAI client."""
        start_time = time.time()
        try:
            # Configure parameters based on no-think mode
            temperature = 0.1 if self.no_think else 0.3
            max_tokens = 1500 if self.no_think else 3000

            if self.no_think:
                system_prompt = f"{system_prompt}/no_think"

            # Build the request parameters
            request_params = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input}
                ],
                "max_tokens": max_tokens,
                "temperature": temperature,
            }

            # Add enable_thinking parameter for Ollama when no-think is enabled
            if self.no_think or True:
                # Use the correct structure for Ollama parameters
                request_params["extra_body"] = {
                    "enable_thinking": False
                }

            response = await self.client.chat.completions.create(**request_params)
            
            # Calculate response time
            response_time = time.time() - start_time
            
            result = response.choices[0].message.content.strip()
            
            # Remove thinking tags if they appear (fallback for when enable_thinking doesn't work)
            if self.no_think and '<think>' in result:
                result = re.sub(r'<think>.*?</think>', '', result, flags=re.DOTALL).strip()
            
            # Display response time
            mode_text = " (No-Think)" if self.no_think else ""
            print(f"⏱️ Response time: {response_time:.2f}s{mode_text}")
            
            return result

        except Exception as e:
            response_time = time.time() - start_time
            print(f"API error: {e} (after {response_time:.2f}s)")
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


def signal_handler(signum, frame):
    """Handle Ctrl+C gracefully."""
    print("\n👋 Goodbye!")
    sys.exit(0)


async def main():
    """CLI interface for the requirement optimizer with interactive flow."""
    # Set up signal handler for Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)
    
    parser = argparse.ArgumentParser(description="Interactive Requirement Optimizer")
    parser.add_argument("--no-think", action="store_true",
                       help="Disable thinking mode for faster, more direct responses")
    args = parser.parse_args()

    optimizer = RequirementOptimizer(no_think=args.no_think)
    session_active = False

    mode_text = " (No-Think Mode)" if args.no_think else ""
    print(f"🎯 Interactive Requirement Optimizer{mode_text}")
    print("Transform user input with confirmation flow")
    print("Commands: 'quit' to exit, '/n' or 'n' for new conversation, Ctrl+C for fast quit\n")

    while True:
        try:
            try:
                if not session_active:
                    user_input = input("Enter your requirement: ").strip()
                else:
                    user_input = input("Your feedback: ").strip()
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break

            if user_input.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break

            if user_input.lower() in ['/n', 'n']:
                optimizer.reset_session()
                session_active = False
                print("✨ Starting new conversation\n")
                continue

            if not user_input:
                continue

            try:
                if not session_active:
                    # Start new session
                    print("Processing...")
                    result = await optimizer.start_session(user_input)
                    if result == "WAITING_FEEDBACK":
                        session_active = True
                else:
                    # Handle feedback in current session
                    result = await optimizer.handle_feedback(user_input)

                    if result == "NEW_CONVERSATION":
                        session_active = False
                        print("✨ Starting new conversation\n")
                        continue
                    elif result == "WAITING_FEEDBACK":
                        # Continue waiting for feedback
                        continue

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