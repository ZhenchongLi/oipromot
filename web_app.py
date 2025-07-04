#!/usr/bin/env python3
"""
Web application version of the requirement optimizer using shared core logic.
"""

import json
import uuid
import os
from typing import Dict
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, HTTPException, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.datastructures import Headers
from dotenv import load_dotenv
from core_optimizer import RequirementOptimizer, SessionManager

# Load environment variables
load_dotenv()


class ProxyHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware to handle reverse proxy headers for correct URL generation."""
    
    async def dispatch(self, request: Request, call_next):
        # Handle X-Forwarded-Proto and X-Forwarded-Host headers
        forwarded_proto = request.headers.get("X-Forwarded-Proto")
        forwarded_host = request.headers.get("X-Forwarded-Host")
        forwarded_port = request.headers.get("X-Forwarded-Port")
        
        # Update request scope for correct URL generation
        if forwarded_proto:
            request.scope["scheme"] = forwarded_proto
        if forwarded_host:
            request.scope["server"] = (forwarded_host, int(forwarded_port) if forwarded_port else 80)
        
        response = await call_next(request)
        return response


class ConnectionManager:
    """Manages WebSocket connections and sessions using shared core logic."""

    def __init__(self):
        """Initialize connection manager."""
        self.active_connections: Dict[str, WebSocket] = {}
        self.sessions: Dict[str, SessionManager] = {}
        self.optimizer = RequirementOptimizer()

    async def connect(self, websocket: WebSocket, session_id: str):
        """Connect a new WebSocket session."""
        await websocket.accept()
        self.active_connections[session_id] = websocket
        self.sessions[session_id] = SessionManager(self.optimizer)

    def disconnect(self, session_id: str):
        """Disconnect a WebSocket session."""
        if session_id in self.active_connections:
            del self.active_connections[session_id]
        if session_id in self.sessions:
            del self.sessions[session_id]

    async def send_message(self, session_id: str, message: dict):
        """Send message to specific session."""
        if session_id in self.active_connections:
            await self.active_connections[session_id].send_text(json.dumps(message))

    async def handle_message(self, session_id: str, message: dict):
        """Handle incoming messages from clients."""
        if session_id not in self.sessions:
            await self.send_message(session_id, {
                "type": "error",
                "content": "会话不存在"
            })
            return

        session = self.sessions[session_id]
        message_type = message.get("type")
        content = message.get("content", "")

        try:
            if message_type == "user_input":
                await self._handle_user_input(session_id, session, content)
            elif message_type == "new_conversation":
                await self._handle_new_conversation(session_id, session)
        except Exception as e:
            await self.send_message(session_id, {
                "type": "error",
                "content": f"处理消息时出错: {str(e)}"
            })

    async def _handle_user_input(self, session_id: str, session: SessionManager, user_input: str):
        """Handle user input (both new requirement and feedback)."""
        # Send processing message
        await self.send_message(session_id, {
            "type": "processing",
            "content": "处理中..."
        })

        # Check if this is a new conversation or feedback
        if session.get_status() == "IDLE":
            # New requirement
            result = await session.start_session(user_input)
        else:
            # Feedback
            result = await session.handle_feedback(user_input)

        await self.send_message(session_id, result)

    async def _handle_new_conversation(self, session_id: str, session: SessionManager):
        """Handle new conversation request."""
        result = session.reset_session()
        await self.send_message(session_id, result)


# FastAPI app setup
app = FastAPI(title="需求优化器", description="交互式需求优化web应用")

# Add proxy headers middleware (must be added before other middlewares)
app.add_middleware(ProxyHeadersMiddleware)

# Add session middleware
app.add_middleware(SessionMiddleware, secret_key="your-secret-key-change-this-in-production")

# Static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Get access password from environment
ACCESS_PWD = os.getenv("ACCESS_PWD")


def check_auth(request: Request):
    """Check if user is authenticated."""
    if not ACCESS_PWD:
        return True  # No password required if not set
    return request.session.get("authenticated") == True


def require_auth(request: Request):
    """Dependency to require authentication."""
    if not check_auth(request):
        raise HTTPException(status_code=401, detail="Authentication required")

# Connection manager
manager = ConnectionManager()


@app.get("/", response_class=HTMLResponse)
async def get_index(request: Request):
    """Serve the main page."""
    if not check_auth(request):
        return RedirectResponse(url="/login", status_code=302)
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/login", response_class=HTMLResponse)
async def get_login(request: Request):
    """Serve the login page."""
    if not ACCESS_PWD:
        return RedirectResponse(url="/", status_code=302)
    if check_auth(request):
        return RedirectResponse(url="/", status_code=302)
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login")
async def post_login(request: Request, password: str = Form(...)):
    """Handle login form submission."""
    if not ACCESS_PWD:
        return RedirectResponse(url="/", status_code=302)
    
    if password == ACCESS_PWD:
        request.session["authenticated"] = True
        return RedirectResponse(url="/", status_code=302)
    else:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "密码错误"
        })


@app.get("/logout")
async def logout(request: Request):
    """Handle logout."""
    request.session.pop("authenticated", None)
    return RedirectResponse(url="/login", status_code=302)


@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time communication."""
    # For WebSocket, we'll accept the connection and handle auth via message
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