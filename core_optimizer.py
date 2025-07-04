#!/usr/bin/env python3
"""
Core requirement optimizer logic shared between CLI and Web versions.
"""

import os
import re
import time
from typing import Optional, Dict, Any
from openai import AsyncOpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class RequirementOptimizer:
    """
    Core requirement optimizer that handles AI-based requirement optimization.

    This class contains the shared logic for both CLI and Web versions.
    """

    def __init__(self):
        """Initialize the optimizer with API configuration."""
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

    async def optimize_requirement(self, user_input: str) -> Dict[str, Any]:
        """
        Optimize user input to clearly describe the requirement.

        Args:
            user_input: Raw user input describing what they want

        Returns:
            Dict with result, response_time, mode, and optional error
        """
        # Get system prompt based on language and thinking mode
        system_prompt = self._get_optimization_prompt(user_input)

        # Try the configured OpenAI-compatible API
        result = await self._call_api(system_prompt, user_input)
        if result:
            return result

        # Fallback: return cleaned input
        return {
            "result": self._simple_clean(user_input),
            "response_time": 0,
            "mode": "回退模式"
        }

    async def refine_requirement(self, initial_result: str, feedback: str) -> Dict[str, Any]:
        """
        Refine requirement based on user feedback.

        Args:
            initial_result: Initial AI response
            feedback: User feedback for refinement

        Returns:
            Dict with refined result, response_time, mode, and optional error
        """
        # Get refinement prompt based on language
        system_prompt = self._get_refinement_prompt(feedback)

        # Prepare user message
        is_chinese = self._detect_chinese(feedback)
        user_message = (
            f"之前的需求描述：{initial_result}\n用户反馈：{feedback}"
            if is_chinese
            else f"Previous requirement description: {initial_result}\nUser feedback: {feedback}"
        )

        # Try the configured OpenAI-compatible API
        result = await self._call_api(system_prompt, user_message)
        if result:
            return result

        # Fallback: return initial result with feedback note
        feedback_note = f"[用户反馈: {feedback}]" if is_chinese else f"[User feedback: {feedback}]"
        return {
            "result": f"{initial_result}\n\n{feedback_note}",
            "response_time": 0,
            "mode": "回退模式"
        }

    def _get_prompt(self, text: str, mode: str = "optimization") -> str:
        """
        Get system prompt for requirement processing.

        Args:
            text: Input text to detect language
            mode: "optimization" for initial optimization, "refinement" for feedback-based refinement
        """
        is_chinese = self._detect_chinese(text)

        if mode == "optimization":
            if is_chinese:
                return """你是一个需求分析专家，同时也是Excel和Word专家。你的任务是将用户的原始输入转化为清晰、准确的需求描述。

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
                return """You are a requirement analysis expert and also an Excel and Word expert. Your task is to transform the user's raw input into a clear, accurate requirement description.

Requirements:
1. Only describe what the user wants, do not add suggestions on how to implement
2. Use concise, professional language
3. Maintain the core intent of the requirement
4. Remove redundant information
5. Ensure the description is complete and clear
6. If involving Excel or Word features, accurately understand related terms and requirements
7. Output result must be in list format, with each requirement point numbered

Please transform the following user input into a clear requirement description:"""

        elif mode == "refinement":
            if is_chinese:
                return """你是一个需求分析专家，同时也是Excel和Word专家。根据用户的反馈，调整和优化之前的需求描述。

要求：
1. 根据用户反馈调整需求描述
2. 保持专业和简洁
3. 确保调整后的描述更符合用户意图
4. 不要添加实现建议，只描述需求
5. 如果涉及Excel或Word功能，准确理解相关术语和需求
6. 输出结果必须以列表形式展示，每个需求点用数字编号

请提供调整后的需求描述："""
            else:
                return """You are a requirement analysis expert and also an Excel and Word expert. Based on user feedback, adjust and optimize the previous requirement description.

Requirements:
1. Adjust requirement description based on user feedback
2. Keep it professional and concise
3. Ensure the adjusted description better matches user intent
4. Do not add implementation suggestions, only describe requirements
5. If involving Excel or Word features, accurately understand related terms and requirements
6. Output result must be in list format, with each requirement point numbered

Please provide the adjusted requirement description:"""

        else:
            raise ValueError(f"Unknown mode: {mode}")

    def _get_optimization_prompt(self, user_input: str) -> str:
        """Get system prompt for requirement optimization."""
        return self._get_prompt(user_input, "optimization")

    def _get_refinement_prompt(self, feedback: str) -> str:
        """Get system prompt for requirement refinement."""
        return self._get_prompt(feedback, "refinement")

    def _detect_chinese(self, text: str) -> bool:
        """Detect if text contains Chinese characters."""
        return any('\u4e00' <= char <= '\u9fff' for char in text)

    async def _call_api(self, system_prompt: str, user_input: str) -> Optional[Dict[str, Any]]:
        """Call OpenAI-compatible API using OpenAI client with detailed error handling."""
        start_time = time.time()
        try:
            # Build the request parameters
            request_params = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input}
                ],
                "max_tokens": 1500,
                "temperature": 0.1,
            }

            # Add enable_thinking parameter for compatibility with Qwen and other APIs
            # For non-streaming calls, it must be set to False
            request_params["extra_body"] = {"enable_thinking": False}

            # Non-streaming mode
            response = await self.client.chat.completions.create(**request_params)
            result = response.choices[0].message.content.strip()

            # Calculate response time
            response_time = time.time() - start_time

            return {
                "result": result,
                "response_time": response_time,
                "mode": "标准模式"
            }

        except Exception as e:
            response_time = time.time() - start_time
            error_info = self._format_error(e, response_time)


            return {
                "error": error_info["message"],
                "error_type": error_info["type"],
                "error_suggestion": error_info["suggestion"],
                "response_time": response_time
            }

    def _format_error(self, error: Exception, response_time: float) -> Dict[str, str]:
        """Format error with detailed information and suggestions."""
        error_str = str(error).lower()

        # Connection errors
        if "connection" in error_str or "timeout" in error_str or "network" in error_str:
            return {
                "type": "连接错误",
                "message": f"无法连接到API服务器 ({self.client.base_url})",
                "suggestion": "请检查网络连接和API服务器地址配置"
            }

        # Authentication errors
        if "unauthorized" in error_str or "401" in error_str or "api key" in error_str:
            return {
                "type": "认证错误",
                "message": "API密钥验证失败",
                "suggestion": "请检查.env文件中的API_KEY配置是否正确"
            }

        # Rate limit errors
        if "rate limit" in error_str or "429" in error_str:
            return {
                "type": "频率限制",
                "message": "API调用频率超出限制",
                "suggestion": "请稍等片刻后重试，或检查API配额"
            }

        # Model not found errors
        if "model" in error_str and ("not found" in error_str or "404" in error_str):
            return {
                "type": "模型错误",
                "message": f"模型 '{self.model}' 不可用",
                "suggestion": "请检查.env文件中的AI_MODEL配置，确保模型名称正确"
            }

        # Server errors
        if "500" in error_str or "502" in error_str or "503" in error_str:
            return {
                "type": "服务器错误",
                "message": "API服务器内部错误",
                "suggestion": "服务器暂时不可用，请稍后重试"
            }

        # JSON or parsing errors
        if "json" in error_str or "parse" in error_str:
            return {
                "type": "响应格式错误",
                "message": "API响应格式异常",
                "suggestion": "API服务可能不兼容，请检查API_BASE_URL配置"
            }

        # Generic error
        return {
            "type": "未知错误",
            "message": str(error),
            "suggestion": "请检查网络连接和API配置，或联系技术支持"
        }

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


class SessionManager:
    """
    Manages optimization sessions with state tracking.

    This class handles session state for both CLI and Web versions.
    """

    def __init__(self, optimizer: RequirementOptimizer):
        """Initialize session manager with optimizer instance."""
        self.optimizer = optimizer
        self.current_requirement = ""
        self.current_feedback = ""
        self.status = "IDLE"  # IDLE, PROCESSING, WAITING_FEEDBACK, ERROR

    async def start_session(self, user_input: str) -> Dict[str, Any]:
        """
        Start a new optimization session.

        Args:
            user_input: Initial user requirement

        Returns:
            Dict with type, content, and metadata
        """
        self.current_requirement = user_input
        self.current_feedback = ""
        self.status = "PROCESSING"

        # Generate initial response
        result = await self.optimizer.optimize_requirement(user_input)

        if "error" in result:
            self.status = "ERROR"
            error_message = self._format_error_message(result)
            return {
                "type": "error",
                "content": error_message,
                "response_time": result["response_time"],
                "error_type": result.get("error_type", "未知错误"),
                "error_suggestion": result.get("error_suggestion", "")
            }

        self.status = "WAITING_FEEDBACK"
        return {
            "type": "ai_response",
            "content": result["result"],
            "response_time": result["response_time"],
            "mode": result["mode"]
        }

    async def handle_feedback(self, feedback: str) -> Dict[str, Any]:
        """
        Handle user feedback in current session.

        Args:
            feedback: User feedback for refinement

        Returns:
            Dict with type, content, and metadata
        """
        if feedback.lower() in ['/n', 'n']:
            return self.reset_session()

        self.current_feedback = feedback
        self.status = "PROCESSING"

        # Generate refined response
        result = await self.optimizer.refine_requirement(
            self.current_requirement, feedback
        )

        if "error" in result:
            self.status = "ERROR"
            error_message = self._format_error_message(result)
            return {
                "type": "error",
                "content": error_message,
                "response_time": result["response_time"],
                "error_type": result.get("error_type", "未知错误"),
                "error_suggestion": result.get("error_suggestion", "")
            }

        self.status = "WAITING_FEEDBACK"
        return {
            "type": "ai_response_refined",
            "content": result["result"],
            "response_time": result["response_time"],
            "mode": result["mode"]
        }

    def reset_session(self) -> Dict[str, Any]:
        """Reset current session data."""
        self.current_requirement = ""
        self.current_feedback = ""
        self.status = "IDLE"
        return {
            "type": "new_conversation",
            "content": "开始新对话"
        }

    def get_status(self) -> str:
        """Get current session status."""
        return self.status

    def _format_error_message(self, result: Dict[str, Any]) -> str:
        """Format error message with type and suggestion."""
        error_type = result.get("error_type", "错误")
        error_message = result.get("error", "未知错误")
        suggestion = result.get("error_suggestion", "")

        formatted_message = f"【{error_type}】{error_message}"
        if suggestion:
            formatted_message += f"\n\n💡 建议: {suggestion}"

        return formatted_message

    async def generate_final_prompt(self) -> str:
        """
        Generate final optimized prompt based on current session.

        Returns:
            Final optimized prompt
        """
        if self.current_feedback:
            # Use refined requirement
            result = await self.optimizer.refine_requirement(
                self.current_requirement, self.current_feedback
            )
        else:
            # Use original optimized requirement
            result = await self.optimizer.optimize_requirement(self.current_requirement)

        return result.get("result", self.current_requirement)