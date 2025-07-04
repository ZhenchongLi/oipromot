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

        # Default to Chinese
        print(f"\n🤖 AI回复: {initial_result}")
        print("\n请选择:")
        print("1. 输入反馈意见进行调整")
        print("2. 输入 '/n' 或 'n' 开始新对话")

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

            # Default to Chinese
            print(f"\n🤖 AI调整后回复: {adjusted_result}")
            print("\n请选择:")
            print("1. 输入反馈意见继续调整")
            print("2. 输入 '/n' 或 'n' 开始新对话")

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
        # Default to Chinese
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
        # Default to Chinese
        system_prompt = """你是一个需求分析专家。根据用户的反馈，调整和优化之前的需求描述。

要求：
1. 根据用户反馈调整需求描述
2. 保持专业和简洁
3. 确保调整后的描述更符合用户意图
4. 不要添加实现建议，只描述需求
5. 输出结果必须以列表形式展示，每个需求点用数字编号

请提供调整后的需求描述："""

        # Try the configured OpenAI-compatible API
        user_message = f"之前的需求描述：{initial_result}\n用户反馈：{feedback}"
        result = await self._call_api(system_prompt, user_message)
        if result:
            return result

        # Fallback: return initial result with feedback note
        return f"{initial_result}\n\n[用户反馈: {feedback}]"

    async def _call_api(self, system_prompt: str, user_input: str) -> Optional[str]:
        """Call OpenAI-compatible API using OpenAI client."""
        start_time = time.time()
        try:
            # Default to no-think mode, enable think mode if /t is present
            enable_thinking = "/t" in user_input
            no_think = not enable_thinking

            # Configure parameters based on thinking mode
            temperature = 0.1 if no_think else 0.3
            max_tokens = 1500 if no_think else 3000

            if no_think:
                # Use simplified no-think prompt for Chinese
                system_prompt = """直接转化用户输入为清晰的需求描述。请以列表形式输出，每个需求点用数字编号。只输出最终结果，不要思考过程，不要解释。"""

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

            # Add enable_thinking parameter for Ollama
            request_params["extra_body"] = {
                "enable_thinking": enable_thinking
            }

            response = await self.client.chat.completions.create(**request_params)

            # Calculate response time
            response_time = time.time() - start_time

            result = response.choices[0].message.content.strip()

            # Remove thinking tags if they appear (fallback for when enable_thinking doesn't work)
            if no_think and '<think>' in result:
                result = re.sub(r'<think>.*?</think>', '', result, flags=re.DOTALL).strip()

            # Display response time
            mode_text = " (思考模式)" if enable_thinking else " (无思考模式)"
            print(f"⏱️ 响应时间: {response_time:.2f}s{mode_text}")

            return result

        except Exception as e:
            response_time = time.time() - start_time
            print(f"API错误: {e} (用时 {response_time:.2f}s)")
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
    print("\n👋 再见!")
    sys.exit(0)


async def main():
    """CLI interface for the requirement optimizer with interactive flow."""
    # Set up signal handler for Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)

    parser = argparse.ArgumentParser(description="Interactive Requirement Optimizer")
    args = parser.parse_args()

    optimizer = RequirementOptimizer()
    session_active = False

    print("🎯 交互式需求优化器")
    print("通过确认流程转换用户输入")
    print("命令: 'quit' 退出, '/n' 或 'n' 开始新对话, '/t' 启用思考模式, Ctrl+C 快速退出\n")

    while True:
        try:
            try:
                if not session_active:
                    user_input = input("请输入您的需求: ").strip()
                else:
                    user_input = input("您的反馈: ").strip()
            except KeyboardInterrupt:
                print("\n再见!")
                break

            if user_input.lower() in ['quit', 'exit', 'q']:
                print("再见!")
                break

            if user_input.lower() in ['/n', 'n']:
                optimizer.reset_session()
                session_active = False
                print("✨ 开始新对话\n")
                continue

            if not user_input:
                continue

            try:
                if not session_active:
                    # Start new session
                    print("处理中...")
                    result = await optimizer.start_session(user_input)
                    if result == "WAITING_FEEDBACK":
                        session_active = True
                else:
                    # Handle feedback in current session
                    result = await optimizer.handle_feedback(user_input)

                    if result == "NEW_CONVERSATION":
                        session_active = False
                        print("✨ 开始新对话\n")
                        continue
                    elif result == "WAITING_FEEDBACK":
                        # Continue waiting for feedback
                        continue

            except KeyboardInterrupt:
                print("\n操作已取消。")
                continue

        except KeyboardInterrupt:
            print("\n再见!")
            break
        except Exception as e:
            print(f"错误: {e}")


def cli_main():
    """Entry point for the CLI script."""
    asyncio.run(main())


if __name__ == "__main__":
    cli_main()