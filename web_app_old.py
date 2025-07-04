#!/usr/bin/env python3
"""
Web application version of the requirement optimizer.
"""

import os
import asyncio
import re
import time
import uuid
from typing import Optional, Dict, Any
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from openai import AsyncOpenAI
from dotenv import load_dotenv
import json

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

    async def optimize_requirement(self, user_input: str) -> dict:
        """
        Optimize user input to clearly describe the requirement.

        Args:
            user_input: Raw user input describing what they want

        Returns:
            Dict with optimized requirement description and metadata
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
        if result and "result" in result:
            return result

        # Fallback: return cleaned input
        return {
            "result": self._simple_clean(user_input),
            "response_time": 0,
            "mode": "回退模式"
        }

    async def refine_requirement(self, initial_result: str, feedback: str) -> dict:
        """
        Refine requirement based on user feedback.

        Args:
            initial_result: Initial AI response
            feedback: User feedback for refinement

        Returns:
            Dict with refined requirement description and metadata
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
        if result and "result" in result:
            return result

        # Fallback: return initial result with feedback note
        return {
            "result": f"{initial_result}\n\n[用户反馈: {feedback}]",
            "response_time": 0,
            "mode": "回退模式"
        }

    async def _call_api(self, system_prompt: str, user_input: str) -> Optional[dict]:
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

            return {
                "result": result,
                "response_time": response_time,
                "mode": "思考模式" if enable_thinking else "无思考模式"
            }

        except Exception as e:
            response_time = time.time() - start_time
            return {
                "error": str(e),
                "response_time": response_time
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


class ConnectionManager:
    """Manages WebSocket connections and sessions."""

    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.optimizer = RequirementOptimizer()

    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        self.active_connections[session_id] = websocket
        self.sessions[session_id] = {
            "current_requirement": "",
            "current_feedback": "",
            "status": "IDLE"
        }

    def disconnect(self, session_id: str):
        if session_id in self.active_connections:
            del self.active_connections[session_id]
        if session_id in self.sessions:
            del self.sessions[session_id]

    async def send_message(self, session_id: str, message: dict):
        if session_id in self.active_connections:
            await self.active_connections[session_id].send_text(json.dumps(message))

    async def handle_message(self, session_id: str, message: dict):
        """Handle incoming messages from clients."""
        message_type = message.get("type")
        content = message.get("content", "")

        if message_type == "new_requirement":
            await self._handle_new_requirement(session_id, content)
        elif message_type == "feedback":
            await self._handle_feedback(session_id, content)
        elif message_type == "new_conversation":
            await self._handle_new_conversation(session_id)

    async def _handle_new_requirement(self, session_id: str, user_input: str):
        """Handle new requirement input."""
        session = self.sessions[session_id]
        session["current_requirement"] = user_input
        session["current_feedback"] = ""
        session["status"] = "PROCESSING"

        # Send processing message
        await self.send_message(session_id, {
            "type": "processing",
            "content": "处理中..."
        })

        # Generate initial response
        response = await self.optimizer.optimize_requirement(user_input)
        
        if "error" in response:
            await self.send_message(session_id, {
                "type": "error",
                "content": f"API错误: {response['error']}",
                "response_time": response["response_time"]
            })
            return
        
        await self.send_message(session_id, {
            "type": "ai_response",
            "content": response["result"],
            "response_time": response["response_time"],
            "mode": response["mode"]
        })

        session["status"] = "WAITING_FEEDBACK"

    async def _handle_feedback(self, session_id: str, feedback: str):
        """Handle user feedback."""
        session = self.sessions[session_id]
        session["current_feedback"] = feedback
        session["status"] = "PROCESSING"

        # Send processing message
        await self.send_message(session_id, {
            "type": "processing",
            "content": "处理中..."
        })

        # Generate refined response
        response = await self.optimizer.refine_requirement(
            session["current_requirement"], feedback
        )

        if "error" in response:
            await self.send_message(session_id, {
                "type": "error",
                "content": f"API错误: {response['error']}",
                "response_time": response["response_time"]
            })
            return
        
        await self.send_message(session_id, {
            "type": "ai_response_refined",
            "content": response["result"],
            "response_time": response["response_time"],
            "mode": response["mode"]
        })

        session["status"] = "WAITING_FEEDBACK"

    async def _handle_new_conversation(self, session_id: str):
        """Handle new conversation request."""
        session = self.sessions[session_id]
        session["current_requirement"] = ""
        session["current_feedback"] = ""
        session["status"] = "IDLE"

        await self.send_message(session_id, {
            "type": "new_conversation",
            "content": "开始新对话"
        })


# FastAPI app setup
app = FastAPI(title="需求优化器", description="交互式需求优化web应用")

# Static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Connection manager
manager = ConnectionManager()


@app.get("/", response_class=HTMLResponse)
async def get_index(request: Request):
    """Serve the main page."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time communication."""
    await manager.connect(websocket, session_id)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            await manager.handle_message(session_id, message)
    except WebSocketDisconnect:
        manager.disconnect(session_id)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)